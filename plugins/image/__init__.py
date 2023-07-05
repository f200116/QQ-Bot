import json, os
from pathlib import Path as path
import requests
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event
from nonebot.permission import SUPERUSER
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.message import MessageSegment
from PIL import Image, ImageFont, ImageDraw
import random

cwd_path = path(__file__).resolve()
# type_list = {'银发', '星空', '兽耳', '竖屏壁纸', '壁纸推荐', '随机壁纸', '横屏壁纸'}

image = on_command('img', aliases={'image'}, priority=10)


@image.handle()
async def handle_first_receive(event: Event, args: Message = CommandArg()):
    type_path = cwd_path.parents[0] / 'data' / 'all_type.json'
    type_dict = await get_info(type_path)

    flag = str(args)
    # if flag != '查询':
    #    await image.send('请稍等...')
    #    pass

    if flag not in type_dict:
        # await image.send('未查询到有效的关键词，将随机(不含三次元)发送...')
        flag = '随机'

    type_ = type_dict[flag]

    if type_:
        if type_ == 'show':
            msg = '在[image、img]后输入以下指令即可\n现有以下指令：'
            i = 1
            for each in type_dict:
                msg += f'\n{i}. ' + each
                i += 1
            dir_path = cwd_path.parents[0] / 'image'
            img_path = await CreateImg(text=msg, file_path=dir_path)
            file_path = MessageSegment.image('file:///' + img_path)
        else:
            file_path = await get_img(type_)
    else:

        file_path = await get_three_yuan(flag)

    await image.finish(file_path)


async def get_img(sort):
    l_url = [f'https://iw233.cn/api.php?sort={sort}&type=json',
             f'http://api.iw233.cn/api.php?sort={sort}&type=json',
             f'http://skri.iw233.cn/api.php?sort={sort}&type=json',
             f'http://aqua.iw233.cn/api.php?sort={sort}&type=json',
             f'https://dev.iw233.cn/api.php?sort={sort}&type=json',
             f'https://mirlkoi.ifast3.vipnps.vip/api.php?sort={sort}&type=json']
    for url in l_url:
        try:
            result = requests.get(url).json()['pic'][0]
            print(result)
            msg = MessageSegment.image(file=result)
            return msg
        except:
            continue
    else:
        return '数据请求失败...'


async def get_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as fr:
        result = json.load(fr)
    return result


async def down_info(file_path, info):
    with open(file_path, 'w', encoding='utf-8') as fw:
        json.dump(info, fw, ensure_ascii=False, indent=2)


async def get_three_yuan(flag: str):
    if flag in ['momo','蠢沫沫']:
        return await get_chun_mo_mo()

    all_url = {
        '黑丝': 'http://api.starrobotwl.com/api/heisi.php',
        '白丝': 'http://api.starrobotwl.com/api/baisi.php',
        'jk': 'http://api.starrobotwl.com/api/jk.php',
        '美女': 'http://api.starrobotwl.com/api/mvzp.php,'
                'http://api.starrobotwl.com/api/sjmnt.php,'
                'http://api.starrobotwl.com/api/sjmnt.php,'
                'http://api.starrobotwl.com/api/mnbz.php',
        '美腿': 'http://api.starrobotwl.com/api/tu.php',
        'cos': 'http://api.starrobotwl.com/api/sjcos.php',
    }

    l_url = all_url.get(flag).split(',')
    l_url = set(l_url)
    for url in l_url:
        try:
            if flag not in ['美腿', ]:
                url = requests.get(url=url).url
            else:

                url = str(requests.get(url=url).text)
                s = ''
                for i in url:
                    if i not in ['\n', '\r']:
                        s += i
                url = s
                break

        except Exception as erc:
            continue

    img_ = MessageSegment.image(file=url)

    return img_


async def get_chun_mo_mo():
    file_path = cwd_path.parents[0] / 'data' / 'all_info.json'
    all_info = await get_info(file_path=file_path)
    info = random.choice(all_info)
    title = info['title']
    url = random.choice(info['url'])
    img = MessageSegment.image(url)
    return img + title


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
