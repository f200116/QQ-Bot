# -*- coding: utf-8 -*-
import random
from nonebot import on_command
from nonebot.adapters import Message
from PIL import Image, ImageFont, ImageDraw
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Event
import json
import os
from pathlib import Path as path

cwd_path = path(__file__).resolve()
info_path = cwd_path.parents[0] / 'data' / 'all_info.json'
img_dir_path = cwd_path.parents[0] / 'image'

img_dongTi = on_command('dongti', aliases={'dt'}, priority=100)

with open(info_path, 'r', encoding='utf-8') as fr:
    all_info = json.load(fr)


@img_dongTi.handle()
async def message_handle(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()  # 首次发送命令时跟随的参数，
    if not plain_text:
        args = Message(MessageSegment.text('随机'))
    elif str(args) == '查询':
        list1 = all_info['list']
        flag_text = '输入序号或者名字即可\n'
        i = 1
        for each in list1:
            flag_text += f'{i}. {each["name"]}  {each["total"]}\n'
            i += 1
        file_path = await CreateImg(text=flag_text, file_path=img_dir_path)
        out_img = MessageSegment.image('file:///' + file_path)
        await img_dongTi.send(out_img)
        await img_dongTi.finish()
    matcher.set_arg("mods_name", args)  # 如果用户发送了参数则直接赋值


@img_dongTi.got('mods_name')
async def handle_name(event: Event, matcher: Matcher, mods_name: str = ArgPlainText('mods_name')):
    if str(mods_name) == '随机':
        one_info = random.choice(all_info['data'])
    else:
        if mods_name.isdigit():
            i = int(mods_name) - 1
            if i >= len(all_info['list']):
                await img_dongTi.finish('输入内容有误！')
                return
            else:
                one_info = all_info['data'][i]
        else:
            mods_name = str(mods_name)
            n1 = 0
            for each in all_info['list']:
                if each['name'] == mods_name:
                    break
                n1 += 1
            else:
                await img_dongTi.finish('输入内容有误！')
                return
            one_info = all_info['data'][n1]

    one_set = random.choice(one_info['data'])
    one_url = random.choice(one_set['url'])
    # image = MessageSegment.image(one_url)
    await img_dongTi.send(f'{one_set["title"]}\n{one_url}')
    await img_dongTi.finish()


async def CreateImg(text: str, file_path, max_len: int = 0, fontSize: int = 30, center=False) -> str:
    '''
    生成带有字符的图片
    :param text: 文本内容
    :param max_len: 文本最长行的字数
    :return:
    '''
    fontPath = os.path.join("/usr/share/fonts/Chinese", "simkai.ttf")  # 存放字体的路径
    # fontSize = 30  # 设置字体大小
    liens = text.split('\n')  # 按照换行符获取行数
    for each in liens:
        if len(each) > max_len:
            max_len = len(each)
    # 画布颜色
    x_max, y_max = (fontSize * (max_len + 3)), len(liens) * (fontSize + 5)
    im = Image.new("RGB", (x_max, y_max), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    # 字体样式

    font = ImageFont.truetype(fontPath, fontSize)  # 字体信息
    # 文字颜色
    if center:
        x = (x_max - (max_len - 3) * fontSize) / 2
        y = (y_max - len(liens) * fontSize) / 2
        dr.text((x, y), text, font=font, fill='#FF2400')

    else:
        dr.text((50, 50), text, font=font, fill="#FF6EC7")
    # t = time.localtime(time.time())
    # img_name = time.strftime("%Y-%m-%d-%H-%M-%S", t)
    img_name = 'output'
    out_path = os.path.join(file_path, img_name + '.png')
    im.save(out_path)  # 保存本地图片
    # im.show()  # 进行展示
    return out_path
