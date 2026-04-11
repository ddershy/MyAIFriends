# backend/web/views/friend/message/memory/update.py 调用流程图\
from django.utils.timezone import now
from langchain_core.messages import SystemMessage, HumanMessage

from web.models.friend import SystemPrompt, Message
from web.views.friend.message.memory.graph import MemoryGraph


def create_system_message():  # 存系统信息
    system_prompts = SystemPrompt.objects.filter(title='记忆').order_by('order_number')
    prompt = ''
    for sp in system_prompts:
        prompt += sp.prompts  # 拼接提示词
    return SystemMessage(prompt)


def create_human_message(friend):  # 定义人类说的话
    prompt = f'【原始记忆】\n{friend.memory}\n'
    prompt += f'【最近对话】\n'
    messages = list(Message.objects.filter(friend=friend).order_by('-id')[:10])  # 逆序排序十条
    messages.reverse()
    for m in messages:
        prompt += f'user: {m.user_message}\n'
        prompt += f'ai: {m.output}'
    return HumanMessage(prompt)


def update_memory(friend):
    app = MemoryGraph.create_app()

    inputs = {  # 消息列表
        'messages': [
            create_system_message(),
            create_human_message(friend),
        ]
    }

    from pprint import pprint
    pprint(inputs)
    res = app.invoke(inputs)
    friend.memory = res['messages'][-1].content
    pprint(friend.memory)

    friend.update_time = now()
    friend.save()
