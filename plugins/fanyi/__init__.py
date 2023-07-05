from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
import requests, time, hashlib, json, re
import random
from pathlib import Path as p

fanyi = on_command('翻译', priority=50)

# 获取当前文件的运行目录
cmd_dir = p(__file__).resolve().parents[0]
info_path = cmd_dir / 'info.json'


@fanyi.handle()
async def again(args: Message = CommandArg()):
    args = str(args)
    if args:

        flag = args.split(' ')[-1]

        if re.findall('([中英日韩法俄])译([中英日韩法俄])', flag):
            again_, end_ = re.findall('([中英日韩法俄])译([中英日韩法俄])', flag)[0]
            args = args[:-4]
            info = await get_info(info_path=info_path)
            from_, to_ = info[again_], info[end_]

            # msg = await get_fanyi(args=args, from_=from_, to_=to_)

        else:
            from_ = to_ = 'auto'
        try:
            msg = await get_fanyi(args, from_=from_, to_=to_)
        except Exception as err:
            msg = str(err)
    else:
        msg = '？'
    await fanyi.finish(msg)


'''async def get_fanyi(msg):
    params = {'msg': msg}
    result = requests.get(url='http://api.starrobotwl.com/api/fanyi.php', params=params).text
    return result'''


async def get_fanyi(args, from_='auto', to_='auto'):
    i = args
    lts = str(int(time.time() * 1000))
    salt = lts + str(random.randint(0, 9))
    sign_str = 'fanyideskweb' + i + salt + 'Ygy_4c=r#e#4EX^NUGUc5'
    m = hashlib.md5()
    m.update(sign_str.encode())
    sign = m.hexdigest()
    url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    headers = {
        "Referer": "https://fanyi.youdao.com/",
        "Cookie": 'OUTFOX_SEARCH_USER_ID=-1124603977@10.108.162.139; JSESSIONID=aaamH0NjhkDAeav9d28-x; OUTFOX_SEARCH_USER_ID_NCOO=1827884489.6445506; fanyi-ad-id=305426; fanyi-ad-closed=1; ___rl__test__cookies=1649216072438',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
    }

    data = {
        "i": i,
        "from": from_,
        "to": to_,
        "smartresult": "dict",
        "client": "fanyideskweb",
        "salt": salt,
        "sign": sign,
        "lts": lts,
        "bv": "a0d7903aeead729d96af5ac89c04d48e",
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "action": "FY_BY_REALTlME",
    }

    res = requests.post(url, headers=headers, data=data)
    response = json.loads(res.text)

    value = response['translateResult'][0][0]['tgt']
    print(value)
    return value


async def get_info(info_path):
    with open(info_path, 'r', encoding='utf-8') as fr:
        info = json.load(fr)
    return info
