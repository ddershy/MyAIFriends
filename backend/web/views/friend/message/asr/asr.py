# backend/web/views/friend/message/asr/asr.py
import asyncio
import json
import os
import uuid

import websockets
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ASRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        audio = request.FILES.get('audio')
        if not audio:
            return Response({
                'result':'音频不存在',
            })
        pcm_data = audio.read()
        # text = asyncio.run(self.run_asr_tasks(pcm_data)) #打开一个事件循环
        text = async_to_sync(self.run_asr_tasks)(pcm_data)
        return Response({
            'result':'success',
            'text':text,
        })

    async def asr_sender(self,pcm_data,ws,task_id): #发送工具
        chunk = 3200
        for i in range(0,len(pcm_data),chunk):
            await ws.send(pcm_data[i:i+chunk]) #每次发一块
            await asyncio.sleep(0.01)
        await ws.send(json.dumps({
            "header": {
                "action": "finish-task",
                "task_id": task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {}
            }
        }))

    async def asr_receiver(self,ws):
        text = ''
        async for msg in ws:#异步循环
            data = json.loads(msg)
            event = data['header']['event']
            if event == 'result-generated':
                output = data['payload']['output']
                if output.get('transcription',None) and output['transcription']['sentence_end']:
                    text += output['transcription']['text']
            elif event in ['task-finished','task-failed']: # === else if event == 'task-finished' or event == 'task-failed'
                break
        return text

    async def run_asr_tasks(self,pcm_data): #时间循环
        task_id= uuid.uuid4().hex
        api_key = os.getenv('API_KEY')
        wss_url = os.getenv('WSS_URL')
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        async with websockets.connect(wss_url, additional_headers=headers) as ws:
            await ws.send(json.dumps({#从文档直接搬
                "header": {
                    "streaming": "duplex",
                    "task_id": task_id,
                    "action": "run-task"
                },
                "payload": {
                    "model": "gummy-realtime-v1",
                    "parameters": {
                        "sample_rate": 16000,
                        "format": "pcm",
                        "transcription_enabled": True,
                    },
                    "input": {},
                    "task": "asr",
                    "task_group": "audio",
                    "function": "recognition"
                }
            }))
            async for msg in ws:#等待task-started事件
                if json.loads(msg)['header']['event'] == 'task-started':
                    break
            _, text = await asyncio.gather( #同时执行两个协程
                self.asr_sender(pcm_data, ws, task_id),
                self.asr_receiver(ws)
            )
            return text