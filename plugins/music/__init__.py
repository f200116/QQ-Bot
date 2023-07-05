import os
from urllib import parse
import re
import requests
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText
from nonebot.permission import SUPERUSER
from PIL import Image, ImageFont, ImageDraw

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}

music = on_command('music', aliases={'音乐', '歌曲'}, priority=10)
all_info = []

file_path_self = os.path.realpath(__file__)  # 当前文件的绝对路径
dir_path = os.path.split(file_path_self)[0]  # 父文件夹路径
msg_path = os.path.join(dir_path, 'image')  # 存放保存图片的目录
if not os.path.exists(msg_path):
    os.mkdir(msg_path)


@music.handle()
async def message_handle(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()  # 首次发送命令时跟随的参数，
    if plain_text:
        matcher.set_arg("music_name", args)  # 如果用户发送了参数则直接赋值


@music.got('music_name', prompt='请发送你需要搜索的歌名或歌手')
async def handle_name(event: Event, matcher: Matcher, music_name: str = ArgPlainText('music_name')):
    name = music_name
    qq_id = event.get_user_id()
    msg_qq_path = os.path.join(msg_path, qq_id)
    if not os.path.exists(msg_qq_path):
        os.mkdir(msg_qq_path)
        global all_info
    all_info = await get_all_info(name)

    if len(all_info) == 0:
        msg = '？！你发的是个什么玩意儿！？  '
        img_path = await CreateImg(msg, msg_qq_path, center=True)
        img = MessageSegment.image(
            file='file:///' + img_path)
        await music.finish(img)
    else:
        msg = '搜索到以下数据：\n'
        i = 1
        for each in all_info:
            msg += f'\n{i}. {each["name_"]}\n'
            i += 1
        if i == 2:
            s1=Message(MessageSegment.text('1'))
            matcher.set_arg("number", s1)

    img_path = await CreateImg(msg, msg_qq_path)
    img = MessageSegment.image(
        file='file:///' + img_path)

    await music.send(img)


@music.got('number', prompt='请输入你要选择的序号')
async def send_msg(event: Event, bot: Bot, number: str = ArgPlainText('number')):
    try:
        n = int(number)
        if n > len(all_info) or n < 1:
            raise f'序号n应大于1并小于等于最大值{len(all_info)}'
    except:
        await music.send('输入有误，已退出')
        await music.finish()

    music_dict = all_info[n - 1]
    name = music_dict['name_']
    id_ = music_dict['id_']

    music_url = await get_music_url(id_)  # 获取歌曲的url
    if not music_url:
        await music.finish('此音乐暂未收录！')

    qq_ = event.get_session_id().split('_')
    message_record = f'[CQ:record,file={music_url}]'  # 发送语音文件  需要依赖ffmpeg 群聊私聊均可
    message = f'[CQ:music,type=custom,url={music_url},audio={music_url},title={name}] '  # 发送名片分享 群聊无法显示！仅支持私聊
    try:
        # await music.send('稍等~~')
        if len(qq_) == 1:
            qq_ = qq_[0]
            # 私聊
            await bot.call_api('send_private_msg', **{'user_id': qq_, 'message': message_record})

        else:
            qq_ = qq_[1]
            # 群聊
            await bot.call_api('send_group_msg',
                               **{'group_id': qq_, 'message': message_record})


    except Exception as erc:
        erc = str(erc)
        await music.send('失败啦，原因：\n' + erc)
    await music.finish()


async def CreateImg(text: str, path: str, max_len: int = 0, fontSize: int = 30, center=False) -> str:
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
    x_max, y_max = (fontSize * max_len), len(liens) * (fontSize + 5)
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

    img_name = 'output'
    out_path = os.path.join(path, img_name + '.png')
    im.save(out_path)  # 保存本地图片

    return out_path


async def utf8_to_url(s: str):
    # 获取一个utf-8，返回url编码
    result = parse.quote(s)
    result1 = ''
    for each in result:
        if each == '%':
            result1 += '_'
        else:
            result1 += each
    return result1


async def get_all_info(name: str):
    url = f'https://www.hifini.com/search-{await utf8_to_url(name)}.htm'  # 汉字转为url编码格式

    response = requests.get(url=url, headers=headers)
    result = re.findall(r'<a href="thread-(\d+).*?>(.*?)</a>', response.text)
    print(result)
    all_list = []
    for each in result:
        id_ = each[0]
        s = each[-1].split('</em>')
        s = ''.join(s)
        s = s.split('<em>')
        name_ = ''.join(s)
        info = {'id_': id_, 'name_': name_}
        all_list.append(info)
    return all_list


async def get_music_url(id_):
    url = f"https://www.hifini.com/thread-{id_}.htm"
    response = requests.get(url=url, headers=headers)
    result = re.findall(r"url: 'get_music.php\?key=(.*?)'", response.text)
    print(result)
    if len(result) == 0:
        result = re.findall(r"url: '(.*?)'", response.text)
        if len(result) == 0:
            return None
        else:
            return result[0]

    key = result[0]
    music_url = f'https://www.hifini.com/get_music.php?key={key}'
    return music_url
