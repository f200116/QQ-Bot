import json
import os
import random
import time

import requests
from nonebot import get_bot
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.params import CommandArg, ArgPlainText
from nonebot_plugin_apscheduler import scheduler

'''

指令刷步和每天定时刷步模块

'''
s = random.randint(0, 59)

file_path = os.path.realpath(__file__)
dir_path = os.path.split(file_path)[0]
user_path = os.path.join(dir_path, 'message')

name = os.path.dirname(__file__)
name = os.path.split(name)[1]

# 每天自动刷步数之后向下面QQ号发送信息
SuperUser='在此键入你超级用户的QQ号'

flag_path = os.path.join('global_files', 'flag', 'flag.json')


@scheduler.scheduled_job('cron', hour=20, minute=30, second=s)
async def timing_again():
    '''
    定义一个定时任务的函数
    :return: None
    '''

    all_flag = await r_file(flag_path)
    flag = all_flag[name]
    print('okokokok')
    if flag:

        global s
        s = random.randint(0, 59)  # 每次刷步后随机选择下一次秒数
        bot = get_bot()
        try:
            t = time.localtime(time.time())  # 获取当前时间截
            id_list = os.listdir(user_path)
            for id_ in id_list:
                info_path = os.path.join(user_path, id_, 'info.json')
                info_dict = await r_file(info_path)
                if info_dict['timing']:
                    step = str(random.randint(10000, 16888))
                    user = info_dict['admin']  # 账号名
                    password = info_dict['password']  # 密码
                    qq = info_dict['qq']  # qq号
                    msg = await again(user=user, password=password, step=step)  # 刷步开始
                    t = time.localtime(time.time())  # 获取当前时间截
                    time_ = str(time.strftime("%Y年%m月%d日 %H:%M:%S", t))  # 格式化时间信息，并专为字符串类型
                    msg = f'{time_}，账号{qq}已提交：\n' + msg
                    await bot.call_api('send_private_msg', **{'user_id': SuperUser, 'message': msg})  # 向主账号发送刷步信息
            else:
                time_ = str(time.strftime('%Y年%m月%d日 %H:%M:%S', t))
                await bot.call_api('send_private_msg',
                                   **{'user_id': SuperUser, 'message': f'{time_}\n所有任务均已提交，请查看日志！'})

        except Exception as erc:
            msg = str(erc)
            await bot.call_api('send_private_msg', **{'user_id': '1654846840', 'message': msg})


######################################################################################
step = on_command('刷步', aliases={'刷步数', '帮我跑步'}, priority=5)


@step.handle()
async def judgment(event: Event, args: Message = CommandArg()):
    '''
    定义一个命令刷步函数
    :param event: 主事件
    :param args: 命令后跟的参数
    :return:
    '''
    args = str(args)
    user_id = event.get_user_id()  # 获取发送信息者id
    if args.isdigit() or not args:  # 判断参数是否为纯数字或无参数，若是，则进行刷步，若不是，则进行绑定或其他操作

        path = os.path.realpath(__file__)
        dir_path = os.path.split(path)[0]
        msg_path = os.path.join(dir_path, 'message')
        if not os.path.exists(msg_path):
            os.mkdir(msg_path)
        path = os.path.join(msg_path, user_id, 'info.json')
        print(path)

        try:  # 进行信息查询，若查到则进行赋值，否则让其进行绑定
            info = await r_file(path)
        except:
            await step.finish('查询信息失败，请绑定！\n使用前请确保已经注册 Zepp Life (原小米运动)账号，并且关联微信\n绑定指定：刷步 绑定')
            return
        # 获取账密
        phone = info['admin']
        password = info['password']

        if not args:  # 判断是否发送步数，如查询失败，则随机进行步数赋值
            steps = str(random.randint(10000, 25666))
            print(steps)
            await step.send('未检测到输入的步数，将从(10000, 25666)之间随机刷步')
        else:
            steps = args
        print(phone, password, steps)
        await step.send('请稍等...')

        # 进行刷步事件，并返回刷步信息
        msg = await again(user=phone, password=password, step=steps)
        # if msg == '刷步失败，请检查用户名和密码！':
        #     msg = '账号密码错误，请重新绑定！\n绑定指令：刷步 绑定'
        await step.send(msg)
        await step.finish()
    else:
        print(args)
        if args not in ['绑定']:
            await step.finish('参数有误，已退出！')


@step.got("flag", prompt="请输入账号、密码。\n注意：账号和密码之间用空格隔开。\n例如：\n183******** qwert12345")
async def handle_flag(event: Event, message_txt: str = ArgPlainText("flag")):
    '''
    定义一个刷步绑定的函数
    :param event:
    :param message_txt:
    :return:
    '''
    user_id = event.get_user_id()
    info = {}
    arg = message_txt.split(' ')
    try:
        admin = arg[0]
        password = arg[1]
    except:
        await step.finish('输入格式有误，请重新绑定！')
    print(admin, password)
    info['qq'] = event.get_user_id()
    info['admin'] = admin
    info['password'] = password
    info['timing'] = False
    path = os.path.realpath(__file__)
    dir_path = os.path.split(path)[0]
    msg_path = os.path.join(dir_path, 'message')
    if not os.path.exists(msg_path):
        os.mkdir(msg_path)
    msg_path=os.path.join(msg_path,user_id)
    if not os.path.exists(msg_path):
        os.mkdir(msg_path)
    path = os.path.join(msg_path, 'info.json')

    # 进行信息写入
    await down_file(path, info)
    at = MessageSegment.at(user_id)
    await step.finish(at + '绑定完成，你可以直接输入：刷步+步数即可刷步\n例如：刷步 15666')


###########################################################################################

set_flag = on_command('全局定时刷步', aliases={'全局定时刷'}, permission=SUPERUSER)


@set_flag.handle()
async def set_flag_(args: Message = CommandArg()):
    args = str(args)

    if args not in ['开', '关']:
        await set_flag.finish()
    f = await r_file(flag_path)

    if args == '开':
        try:
            if not f[name]:
                f[name] = True
                await down_file(flag_path, f)
        except:
            f[name] = True
            await down_file(flag_path, f)
        await set_flag.send('全局定时刷步已打开')


    elif args == '关':
        try:
            if f[name]:
                f[name] = False
                await down_file(flag_path, f)
        except:
            f[name] = False
            await down_file(flag_path, f)
        await set_flag.send('全局定时刷步已关闭')


####################################################################


timing_switch = on_command('定时刷', priority=7)


@timing_switch.handle()
async def switch(event: Event, args: Message = CommandArg()):
    '''
    开关用户的定时刷
    '''
    args = str(args)  # 获取用户发送信息
    if args not in ['开', '关']:
        await set_flag.finish()
    qq = event.get_user_id()
    info_path = os.path.join(user_path, qq, 'info.json')
    at = MessageSegment.at(qq)
    try:
        f = await r_file(info_path)
    except:
        await timing_switch.finish(at + '未查询到相关信息，请绑定！\n绑定指令为：刷步 绑定')

        return

    if args == '开':  # 如果指令是开，则修改为True

        f['timing'] = True
        await down_file(info_path, f)
        await set_flag.send(at + '定时刷步已打开')


    elif args == '关':  # 如果指令是关，则修改为False

        f['timing'] = False
        await down_file(info_path, f)
        await set_flag.send(at + '定时刷步已关闭')

    await set_flag.finish()


async def down_file(path, info: dict):
    '''
    定义一个信息录入的函数
    :param path: 目标路径
    :param info: 录入目标
    :return: None
    '''

    with open(path, 'w', encoding='UTF-8', ) as wf:
        json.dump(info, wf, ensure_ascii=False, indent=4)


async def r_file(path:str) -> dict:
    '''
    定义一个读取已录信息的函数
    :param path: 目标路径
    :return: 目标信息字典
    '''
    with open(path, 'r', encoding='UTF-8') as rf:
        rf = json.load(rf)
    return rf


async def again_2(user, password, step):
    '''
    模拟浏览器发送刷步请求
    :param user: 账号
    :param password:密码
    :param step: 步数
    :return: 返回响应信息
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71'
    }
    url = 'https://apis.jxcxin.cn/api/mi'
    '''
    user: 185554465
    password: 54154154
    step: 12456
    ver: cxydzsv3
    '''
    params = {'user': user, 'password': password, 'step': step, 'ver': 'cxydzsv3'}
    result = requests.get(url=url, params=params, headers=headers).json()['msg']
    if result == '步数提交成功':
        msg = f'步数已提交成功，{step}步，请移至微信端查看。'
    elif result in ['刷步失败，请检查用户名和密码！', '手机号格式错误！']:
        msg = f'{result}\n请重新绑定\n如若忘记账号密码，请下载 Zepp Life (原小米运动)重置密码'
    else:
        msg = result
    return msg


async def again(user, password, step):
    '''
    模拟浏览器发送刷步请求
    :param user: 账号
    :param password:密码
    :param step: 步数
    :return: 返回响应信息
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71'
    }
    url = 'https://www.17bushu.com/changeXiaomiSteps'
    '''
    phone: 12345678910
    password: 123465
    steps: 111
    '''
    data = {'phone': user, 'password': password, 'steps': step}
    try:
        result = requests.post(url=url, headers=headers, data=data).json()['msg']
        if result in ['手机号或密码填写错误啦~', '账号不能为空哦~', '手机号必须为 11 位的数字哦~']:
            msg = f'{result}\n请重新绑定！'

        elif re.match(r'成功修改步数为【\d+】', result):
            msg = f'{result}，请移至微信端查看'
        else:
            msg = await again_2(user, password, step)
        print(result)

    except:
        msg = await again_2(user, password, step)
    return msg
