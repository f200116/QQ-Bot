import requests
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.permission import PRIVATE_FRIEND,GROUP

help = on_command('闲聊', aliases={'呼叫小思'}, priority=5)


@help.handle()
async def main_event(event: Event, args: Message = CommandArg()):
    await help.send('以下对话均出自：https://www.ownthink.com/robot.html\n你好，我是AI陪聊小思，很高兴和你见面\n如果不想跟我继续聊天请'
                    '输入\\end退出哦')


@help.got('message')
async def again(event: Event, message: Message = Arg(), message_txt: str = ArgPlainText('message')):
    # 判断是否是群消息
    txt = event.get_event_description()

    user_id = event.get_user_id()
    is_gro = await is_group(txt)
    if is_gro:
        at = MessageSegment.at(user_id)
        print('群聊')
    else:
        at = ''
        print('私聊')

    if message_txt != '\\end':
        id_ = event.get_event_description().split()[1]  # 获取对方发消息的id
        reply = MessageSegment.reply(int(id_))  # 定义回复信息
        msg = await get_reply(message_txt)  # 获取回复信息
        await help.send(reply + at + msg)  # 发送信息
        await help.reject()  # 继续循环下一次

    else:
        await help.finish(at + '欢乐时光这么快就已经结束了，很期待下次与你的见面。')


async def get_reply(msg: str) -> str:
    url_ = f'https://api.ownthink.com/bot?appid=xiaosi&spoken={msg}'
    s = requests.get(url_).json()
    reply = s['data']['info']['text']
    return reply


async def is_group(arg: str) -> bool:
    l_arg = arg.split(' ')
    print(l_arg)
    flag = l_arg[3].isdigit()
    return not flag
