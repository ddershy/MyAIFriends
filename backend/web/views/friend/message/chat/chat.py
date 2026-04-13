# backend/web/views/friend/message/chat/chat.py
import asyncio
import base64
import json
import os
import threading
import uuid
from queue import Queue

import websockets
from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage, AIMessage
from openai import api_key
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend, Message, SystemPrompt
from web.views.friend.message.chat.graph import ChatGraph
from web.views.friend.message.memory.update import update_memory


class SSERenderer(BaseRenderer): #渲染器
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self,data, accepted_media_type=None, renderer_context=None):
        return data

def add_system_prompt(state,friend):#添加系统提示词
    msgs = state['messages'] #读取之前已有的信息
    system_prompts = SystemPrompt.objects.filter(title="回复").order_by('order_number') #将回复模块按照order_number排序
    prompt= ''
    for sp in system_prompts:
        prompt += sp.prompts #连接起来
    prompt += f'\n【角色性格】\n{friend.character.profile}\n'
    prompt += f'【长期记忆】\n{friend.memory}\n'
    return {'messages':[SystemMessage(prompt)] + msgs} #手动追加

def add_recent_message(state,friend):#近期对话
    msgs = state['messages']
    message_raw = list(Message.objects.filter(friend=friend).order_by('-id')[:10])#近十轮对话,因为是从新到旧排列，需要翻转对话顺序，用list包裹
    message_raw.reverse()
    messages = []
    for m in message_raw:
        messages.append(HumanMessage(m.user_message))
        messages.append(AIMessage(m.output))
    return {'messages':msgs[:1] + messages + msgs[-1:]} #十轮对话加在系统提示词和用户对话之间

class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer] #引入渲染器
    def post(self, request):
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()
        if not message:
            return Response({
                'result': '消息不得为空',
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user)
        if not friends.exists():
            return Response({
                'result': '好友不存在',
            })

        # 对接大模型
        friend = friends.first()
        app = ChatGraph.create_app()

        #构造输入,构造刚刚定义的字典
        inputs ={
            'messages': [HumanMessage(message)] #和构造的函数内变量名对应，封装传入的消息
        }
        inputs = add_system_prompt(inputs,friend) #追加系统信息
        inputs = add_recent_message(inputs,friend)

        # res = app.invoke(inputs) #调用计算流程  非流式回复
        # print(res['messages'][-1].content) #会返回一个


        response = StreamingHttpResponse(
            self.event_stream(app, inputs,friend,message),
            content_type="text/event-stream") #返回StreamingHttpResponse
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    async def tts_sender(self,app,inputs,mq,ws,task_id):
        async for msg, metadata in app.astream(inputs, stream_mode="messages"): #改成异步版本.astream
            if isinstance(msg, BaseMessageChunk):  # 消息是否是本次片段
                if msg.content:  # 判断是否有消息
                    await ws.send(json.dumps({#发给语音同步大模型
                        "header": {
                            "action": "continue-task",
                            "task_id": task_id,
                            "streaming": "duplex"
                        },
                        "payload": {
                            "input": {
                                "text": msg.content
                            }
                        }
                    }))
                    mq.put_nowait({'content':msg.content}) #加到消息队列
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:  # 存储usage信息
                    mq.put_nowait({'usage': msg.usage_metadata})

        await ws.send(json.dumps({ #结束
            "header": {
                "action": "finish-task",
                "task_id": task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {}  # input不能省去，否则会报错
            }
        }))

    async def tts_receiver(self,mq,ws):
        async for msg in ws:
            if isinstance(msg,bytes):
                audio = base64.b64encode(msg).decode('utf-8')#二进制转文本
                mq.put_nowait({'audio':audio})
            else:
                data = json.loads(msg)
                event = data['header']['event']
                if event in ['task-finished','task-failed']:
                    break

    async def run_tts_tasks(self, app, inputs,mq):
        task_id = uuid.uuid4().hex
        api_key = os.getenv('API_KEY')
        wss_url = os.getenv('WSS_URL')
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        async with websockets.connect(wss_url, additional_headers=headers) as ws:
            await ws.send(json.dumps({
                "header": {
                    "action": "run-task",
                    "task_id": task_id,
                    "streaming": "duplex"
                },
                "payload": {
                    "task_group": "audio",
                    "task": "tts",
                    "function": "SpeechSynthesizer",
                    "model": "cosyvoice-v3-flash",
                    "parameters": {
                        "text_type": "PlainText",
                        "voice": "longanyang",  # 音色
                        "format": "mp3",  # 音频格式
                        "sample_rate": 22050,  # 采样率
                        "volume": 50,  # 音量
                        "rate": 1.5,  # 语速
                        "pitch": 1  # 音调
                    },
                    "input": {  # input不能省去，不然会报错
                    }
                }
            }))
            async for msg in ws:
                if json.loads(msg)['header']['event'] == 'task-started':
                    break
            await asyncio.gather(
                self.tts_sender(app,inputs,mq,ws,task_id),#同时等待两个协程结束
                self.tts_receiver(mq,ws),
            )

    def work(self,app,inputs,mq):
        try:
            asyncio.run(self.run_tts_tasks(app,inputs,mq))
        finally: #无论是否有异常，都需要结束
            mq.put_nowait(None) #非阻塞式，防止死循环


    # 流式回复： yield：生成器，每执行一次，会往下进行一个yield之前的内容；
    #生成器定义
    def event_stream(self,app,inputs, friend , message):
        mq = Queue()#消息队列
        thread = threading.Thread(target=self.work,args=(app,inputs,mq))
        thread.start()

        full_output = '' #存储大模型的回复
        full_usage ={} #存储消耗量
        while True:
            msg = mq.get()
            if not msg :
                break
            # print(msg)
            if msg.get('content',None):
                full_output += msg['content']
                yield f"data:{json.dumps({'content': msg['content']}, ensure_ascii=False)}\n\n"  # ensure_ascii=False 确保返回为unicode 看中文
            if msg.get('audio',None):
                yield f"data:{json.dumps({'audio': msg['audio']}, ensure_ascii=False)}\n\n"  # ensure_ascii=False 确保返回为unicode 看中文
            if msg.get('usage',None):
                full_usage = msg['usage']

        yield 'data: [DONE]\n\n' #结束格式 data: [DONE]\n\n
        input_tokens = full_usage.get('input_tokens',0)#存储输入的token
        output_tokens = full_usage.get('output_tokens',0)
        total_tokens = full_usage.get('total_tokens',0) #根据后台的格式获取的
        Message.objects.create(
            friend=friend,
            user_message=message[:500],
            input = json.dumps(
                [m.model_dump() for m in inputs['messages']],
                ensure_ascii=False,#保证输出的是中午而不是unicode
            )[:10000],#阶段，长度和web/models/friend.py Message中定义的一致
            output = full_output[:500],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )
        if Message.objects.filter(friend=friend).count() % 1 == 0:#判断是否有超过10轮，需要记忆
           update_memory(friend)