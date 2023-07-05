import time

from nonebot import get_bot
from nonebot_plugin_apscheduler import scheduler


@scheduler.scheduled_job('interval', seconds=5)
async def again():
    global time_again
    bot = get_bot()
    t = time.localtime(time.time())
    time_ = str(time.strftime("%Y-%m-%d %H:%M", t))

    s = await bot.call_api('get_group_list')

    for id_ in s:
        group_id = id_['group_id']
        group_name = id_['group_name']
        # print(group_id)

        self_id = bot.self_id
        msg_l = await bot.call_api('get_group_member_info',

                                   **{'group_id': group_id, 'user_id': self_id, 'no_cache': True})
        again_name = msg_l['card']

        end_name = 'qqBot~ ' + time_

        if again_name != end_name:
            # print(self_id)
            await bot.call_api("set_group_card",
                               **{'group_id': group_id, 'user_id': self_id, 'card': end_name})

