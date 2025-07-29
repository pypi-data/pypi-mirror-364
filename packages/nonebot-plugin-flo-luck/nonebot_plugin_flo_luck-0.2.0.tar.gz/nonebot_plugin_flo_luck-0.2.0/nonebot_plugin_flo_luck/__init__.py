# ------------------------ import ------------------------
# import packages from python
from pathlib import Path
from .database import SelectType, LuckDataBase, SpecialDataBase
from .helper_functions import *

# import packages from nonebot or other plugins
from nonebot import load_plugins, require, logger
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.permission import SUPERUSER

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import *

require("nonebot_plugin_uninfo")
from nonebot_plugin_uninfo import Uninfo

# ------------------------ import ------------------------

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-flo-luck",
    description="Florenz版本的 jrrp，主要追加了特殊列表与排行功能。",
    usage="""
    ==============用户使用==============
    1> jrrp 查看今日幸运值。
    2> jrrp.today 查看今日大家的平均幸运值。
    3> jrrp.week (month|year|all) 查看平均幸运值。
    4> jrrp.rank 查看自己的幸运值在今日的排行。
    ============超级用户使用============
    5> jrrp.add user_id [-g greeting] [-b bottom] [-t top]
       将QQ号为user_id的用户加入特殊列表，问候语为greeting，幸运值取值为[bottom, top]。
       默认无问候语，取值[0, 100]。
    6> jrrp.del id 将该条数据移出特殊列表。
    7> jrrp.check 查看特殊列表信息
    """,
    homepage="https://github.com/Florenz0707/nonebot-plugin-flo-luck",
    type="application",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    extra={
        "author": "florenz0707",
    }
)

sub_plugins = load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)

luck_conn = LuckDataBase()
sp_conn = SpecialDataBase()

# command declarations
jrrp = on_alconna("jrrp", use_cmd_start=True, block=True, priority=5)
jrrp_today = on_alconna("jrrp.today", use_cmd_start=True, block=True, priority=5)
jrrp_week = on_alconna("jrrp.week", use_cmd_start=True, block=True, priority=5)
jrrp_month = on_alconna("jrrp.month", use_cmd_start=True, block=True, priority=5)
jrrp_year = on_alconna("jrrp.year", use_cmd_start=True, block=True, priority=5)
jrrp_all = on_alconna("jrrp.all", use_cmd_start=True, block=True, priority=5)
jrrp_rank = on_alconna("jrrp.rank", use_cmd_start=True, block=True, priority=5)
jrrp_add = on_alconna(
    Alconna(
        "jrrp.add",
        Args["target?", str],
        Option("-g", Args["greeting", str]),
        Option("-b", Args["bottom", int]),
        Option("-t", Args["top", int]),
    ),
    use_cmd_start=True,
    block=True,
    priority=5,
    permission=SUPERUSER
)
jrrp_del = on_alconna(
    Alconna(
        "jrrp.del",
        Args["target?", int]
    ),
    use_cmd_start=True,
    block=True,
    priority=5,
    permission=SUPERUSER
)
jrrp_check = on_alconna("jrrp.check", use_cmd_start=True, block=True, priority=5, permission=SUPERUSER)
jrrp_help = on_alconna("jrrp.help", aliases={"jrrp.menu"}, use_cmd_start=True, block=True, priority=5)


# command functions
@jrrp.handle()
async def jrrp_handler(session: Uninfo):
    user_id = session.user.id
    luck_val = luck_conn.select_by_user_date(user_id, today())
    message = ""
    bottom, top = 0, 100
    if (info := sp_conn.select_by_user(user_id)) is not None:
        data: dict = random.choice(info)
        message = data.get('greeting')
        bottom, top = data.get('bottom'), data.get('top')
    if luck_val == -1:
        luck_val = luck_generator(user_id, bottom, top)
        luck_conn.insert(user_id, luck_val, today())
    short_info, long_info = luck_tip(luck_val)
    await UniMessage.text(" " + message).text(f"\n您今日的幸运值为{luck_val}， 为\"{short_info}\"。{long_info}").finish(
        at_sender=True)


@jrrp_today.handle()
async def jrrp_today_handler():
    val = luck_conn.select_average(today())
    # Today's record empty
    if val == -1:
        await UniMessage.text(f" 啊嘞？今日还没有人获取幸运值哦~快来成为第一个吧！").finish(at_sender=True)
    await UniMessage.text(f" 今日大家的平均幸运值是{val}哦~").finish(at_sender=True)


@jrrp_week.handle()
async def jrrp_week_handler(session: Uninfo):
    user_id = session.user.id
    values = luck_conn.select_by_range(user_id, SelectType.BY_WEEK)
    days, average = get_average(values)
    if days == 0:
        message = " 您本周还没有过幸运值记录哦~"
    else:
        message = f" 您本周总共有{days}条记录，平均幸运值为{average:.2f}。"
    await UniMessage.text(message).finish(at_sender=True)


@jrrp_month.handle()
async def jrrp_month_handler(session: Uninfo):
    user_id = session.user.id
    values = luck_conn.select_by_range(user_id, SelectType.BY_MONTH)
    days, average = get_average(values)
    if days == 0:
        message = " 您本月还没有过幸运值记录哦~"
    else:
        message = f" 您本月总共有{days}条记录，平均幸运值为{average:.2f}。"
    await UniMessage.text(message).finish(at_sender=True)


@jrrp_year.handle()
async def jrrp_year_handler(session: Uninfo):
    user_id = session.user.id
    values = luck_conn.select_by_range(user_id, SelectType.BY_YEAR)
    days, average = get_average(values)
    if days == 0:
        message = " 您今年还没有过幸运值记录哦~"
    else:
        message = f" 您今年总共有{days}条记录，平均幸运值为{average:.2f}。"
    await UniMessage.text(message).finish(at_sender=True)


@jrrp_all.handle()
async def jrrp_all_handler(session: Uninfo):
    user_id = session.user.id
    values = luck_conn.select_by_range(user_id, SelectType.BY_NONE)
    days, average = get_average(values)
    if days == 0:
        message = " 您还没有过幸运值记录哦~"
    else:
        message = f" 您总共有{days}条记录，平均幸运值为{average:.2f}。"
    await UniMessage.text(message).finish(at_sender=True)


@jrrp_rank.handle()
async def jrrp_rank_handler(session: Uninfo):
    user_id = session.user.id
    if luck_conn.select_by_user_date(user_id, today()) == -1:
        await UniMessage.text(" 您今日还没有幸运值哦~先开启幸运值再查看排名吧！").finish(at_sender=True)
    today_total = luck_conn.select_by_date(today())
    today_total.sort(key=(lambda item: item[1]), reverse=True)
    for index in range(len(today_total)):
        if today_total[index][0] == user_id:
            await UniMessage.text(f" 您的幸运值是{today_total[index][1]}，"
                                  f"在今日的排名中目前位于 {index + 1} / {len(today_total)}。").finish(at_sender=True)


@jrrp_add.handle()
async def jrrp_add_handler(
        user_id: Match[str] = AlconnaMatch("target"),
        greeting: Query[str] = Query("greeting", ""),
        bottom: Query[int] = Query("bottom", 0),
        top: Query[int] = Query("top", 100)):
    if not user_id.available:
        await UniMessage.text("参数无效。").finish()
    user_id = user_id.result
    if not (greeting.available and bottom.available and top.available):
        await UniMessage.text("参数无效。").finish()
    greeting = greeting.result
    bottom = bottom.result
    top = top.result
    sp_conn.insert(user_id, greeting, bottom, top)
    message = "已插入条目：\n" \
              f"user_id： {user_id}\n" \
              f"greeting： '{greeting}'\n" \
              f"bottom： {bottom}\n" \
              f"top： {top}"
    await UniMessage.text(message).finish()


@jrrp_del.handle()
async def jrrp_del_handler(rec_id: Match[int] = AlconnaMatch("target")):
    if rec_id.available:
        rec_id = rec_id.result
        if (old_info := sp_conn.select_by_id(rec_id)) is None:
            message = f" 删除失败，表中不存在条目'{rec_id}'。"
        else:
            sp_conn.remove(rec_id)
            message = f"删除成功，原数据：\n" \
                      f"user_id： {old_info.get('user_id')} \n" \
                      f"greeting： '{old_info.get('greeting')}'\n" \
                      f"bottom： {old_info.get('bottom')}\n" \
                      f"top：{old_info.get('top')}"
    else:
        message = "参数无效。"
    await UniMessage.text(message).finish()


@jrrp_check.handle()
async def jrrp_check_handler():
    items = sp_conn.select_all()
    if items is not None:
        message = f"共有{len(items)}条数据。"
        index = 1
        for item in items:
            message += f"\n\n{[index]}=================\n" \
                       f"user_id： {item.get('user_id')}\n" \
                       f"greeting： '{item.get('greeting')}'\n" \
                       f"bottom： {item.get('bottom')}\n" \
                       f"top： {item.get('top')}"
            index += 1
        await UniMessage.text(message).finish()


@jrrp_help.handle()
async def jrrp_help_handler():
    message = """
1 > jrrp
查看今日幸运值。
2 > jrrp.today
查看今日大家的平均幸运值。
3 > jrrp.week(month | year | all)
查看平均幸运值。
4 > jrrp.rank
查看自己的幸运值在今日的排行。"""
    await UniMessage.text(message).finish(at_sender=True)
