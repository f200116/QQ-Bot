import asyncio

import requests
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

setu = on_command("setu", aliases={"色图", "涩图"}, priority=10)


@setu.handle()
async def handle_first_receive(matcher: Matcher, bot: Bot, event: Event, args: Message = CommandArg()):
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

    # 判断是否r18，并获取搜索需求
    r18 = False
    args = str(args)
    # print('args-->', args)
    l_arg = args.split('，')
    # print('l_arg-->', l_arg)
    if l_arg[-1].lower() in ['y', 'n']:
        # print('ok')
        # print(l_arg)
        if l_arg[-1].lower() == 'y':
            r18 = True
        l_arg.pop(-1)
    #     print(l_arg)
    # print(l_arg)
    l_need = l_arg

    list_msg_id = []

    # print(setu)

    await setu.send('请稍等...')
    l_msg = await get_image(r18, l_need)
    if not l_msg:
        await setu.finish('请求返回列表为空，问题原因可能为：\n\n1.键入关键词太多爬取范围过小\n\n2.请求api时发生错误（一般不会发生）')

    try:
        for img_ in l_msg[0]:
            msg_id = (await setu.send(img_))['message_id']
            list_msg_id.append(msg_id)
        await setu.send(at + '小撸怡情，大撸伤身，樯橹灰飞烟灭！！\n图片均出自P站，仅供学习参考使用。')
        if r18:
            await asyncio.sleep(30)
            for id in list_msg_id:
                await bot.delete_msg(message_id=id)
    except:
        img_ = at + '服务器请求超时...\n兴许一会儿会发出来\n爬取到的网址为：'
        for url in l_msg[1]:
            img_ += '\n' + url + '\n'
        await setu.send(img_)

    await setu.finish()


async def get_image(r18: bool, l_need: list):
    l1 = []
    l2 = []

    url = 'https://api.lolicon.app/setu/v2'
    if r18:
        url += '?r18=1'
    else:
        url += '?r18=0'
    print('l_need', l_need)
    for need in l_need:
        if need:
            url += f'&tag={need}'
    print(f'api-url -->[{url}]')

    try:
        dict1 = requests.get(url).json()['data']
        if not dict1:
            return None
        for lis in dict1:
            img_url = lis['urls']['original']
            print('img-url -->', img_url)

            img_ = MessageSegment.image(file=img_url)
            l1.append(img_)
            l2.append(img_url)

        return l1, l2
    except:
        return None


async def is_group(arg: str) -> bool:
    l_arg = arg.split(' ')
    print(l_arg)
    flag = l_arg[3].isdigit()
    return not flag
