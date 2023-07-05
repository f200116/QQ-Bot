import random

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.internal.params import ArgPlainText
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

guess = on_command('猜数字', priority=100)

num = random.randint(1, 1023)
mod_flag = 1
i = 1
num2 = 1
num3 = 1023
n = 1


@guess.handle()
async def handle_message(matcher: Matcher, args: Message = CommandArg()):
    global num, mod_flag, i, num2, num3, n
    num = random.randint(1, 1023)
    mod_flag = 1
    i = 1
    num2 = 1
    num3 = 1023
    n = 1
    await guess.send(
        '欢迎来玩猜数字小游戏\n游戏规则：你需要在指定次数内猜出本局的数字，我会回答你猜的数字较大、较小或相等。10次内猜中答案即为成功。\n输入q可以直接退出。开始游戏吧~')
    if args:
        matcher.set_arg("is_show", args)


@guess.got('is_show', prompt="是否需要提前显示答案？(y/n)")
async def handle_got1(is_show: str = ArgPlainText(f'is_show')):
    global mod_flag
    if is_show == 'y':
        mod_flag = 0
        await guess.send(f'本局的答案是: {num}')


@guess.got('str1', prompt=f"第{1}次 请输入你选择的数字(请确保数字在{num2} - {num3}之间)：")
async def main(str1: str = ArgPlainText('str1')):
    global num2, num3, num, i, n
    while True:
        flag = False
        while True:
            if str1.lower() == 'q' or n > 3:
                num1 = -1
                n = 1
                break
            if flag:
                await guess.reject(prompt=f'第{i}次 请输入你选择的数字(请确保数字在{num2} - {num3}之间)：')
            if not str1.isdigit():
                flag = True
                await guess.send(f'错误输入第{n}次 你输入的信息有误，请重新输入！')
                print(n)
                n += 1
                continue
            num1 = int(str1)

            if num1 < num2 or num1 > num3:
                flag = True
                await guess.send(f'错误输入第{n}次 你输入的信息有误，请重新输入！')
                print('n2', n)
                n += 1
                continue
            break

        if num1 == -1:
            await guess.finish('正在退出，欢迎下次游玩。')
            return

        if mod_flag == 0:
            flag = await judge_size(num1, num)
        elif mod_flag == 1:
            flag = await judge_bigger_or_lower(num1, num2, num3)
        else:
            return

        if flag == 0:
            await guess.send(f'恭喜你答对了 用了 {i} 次机会！')
            await guess.finish()
        elif flag == 1:
            await guess.send('你猜的数字有点大。')
            num3 = num1 - 1

        elif flag == 2:
            await guess.send('你猜的数字有点小。')
            num2 = num1 + 1
        i += 1
        if i > 10:
            if mod_flag == 1:
                num = random.randint(num2, num3)
            await guess.finish(f'很遗憾，你10次内并未答对  答案是{num}')
        n = 1
        await guess.reject(prompt=f'第{i}次 请输入你选择的数字(请确保数字在{num2} - {num3}之间)：')


async def judge_size(num1: int, num2: int):
    if num1 == num2:
        return 0
    if num1 > num2:
        return 1
    if num1 < num2:
        return 2


async def judge_bigger_or_lower(num1, num2, num3):
    n1 = num3 - num1
    n2 = num1 - num2
    if num2 == num3:
        return 0
    if n1 < n2:
        return 1
    if n1 > n2:
        return 2
    return random.randint(1, 2)
