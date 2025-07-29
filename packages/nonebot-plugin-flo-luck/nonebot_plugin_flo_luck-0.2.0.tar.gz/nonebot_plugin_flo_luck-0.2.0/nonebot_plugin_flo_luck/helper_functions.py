import datetime
import random

"""
Helper functions that project uses.
"""

# (val: int, short_info: str,
# (long_info_1: str,
#  long_info_2: str,
#  ......           ))
luck_info = (
    (0, "最凶",
     ("要不今天咱们就在床上躲一会吧...害怕...",
      "保佑。祝你平安。",
      "哎呀，幸运值几乎触底了！整个世界都在与你作对，每一步都充满荆棘。",
      "运势黑暗至极，做任何事都如履薄冰，需万分小心。")),
    (1, "大凶",
     ("可能有人一直盯着你......",
      "要不今天咱还是别出门了......",
      "幸运值极低，被厄运之神紧紧盯住，每一个决定都可能引发连锁的不幸。",
      "运势陷入泥潭，需要极大的毅力和勇气才能挣脱困境。")),
    (10, "凶",
     ("啊这...昨天是不是做了什么不好的事？",
      "啊哈哈...或许需要多加小心呢。",
      "幸运值有所提升，但仍处于低谷，随时可能陷入更深的困境。",
      "运势如同过山车，时好时坏，但大部分时间都在低谷徘徊，保持警惕。")),
    (20, "末吉",
     ("呜呜，今天运气似乎不太好...",
      "勉强能算是个吉签吧。",
      "幸运值略有波动，但整体仍不理想，仿佛被无形的障碍阻挡。",
      "迷雾中的航行，方向不明。")),
    (30, "末小吉",
     ("唔...今天运气有点差哦。",
      "今天喝水的时候务必慢一点。",
      "幸运值有所提升，但仍处于危险边缘。",
      "暴风雨中的小船，随时可能被巨浪吞噬，需保持冷静和坚韧。")),
    (40, "小吉",
     ("还行吧，稍差一点点呢。",
      "差不多是阴天的水平吧，不用特别担心哦。",
      "幸运值开始有所好转，但仍需小心谨慎，因为稍有不慎就可能前功尽弃。",
      "黎明前的黑暗，虽然曙光初现，但仍需耐心等待和坚持。")),
    (50, "半吉",
     ("看样子是普通的一天呢。一切如常......",
      "加油哦！今天需要靠自己奋斗！",
      "终于摆脱了厄运，运势开始稳步上升，继续努力才能保持势头。",
      "运势如同春日里的小草，虽然刚刚探出头来，但已经充满了生机和希望。")),
    (60, "吉",
     ("欸嘿...今天运气还不错哦？喜欢的博主或许会更新！",
      "欸嘿...今天运气还不错哦？要不去抽卡？",
      "幸运值大幅上升，幸运之神眷顾，做什么都顺风顺水。",
      "运势如同夏日里的阳光，明媚而炽热，让人感受到无尽的温暖和力量。")),
    (70, "大吉",
     ("好耶！运气非常不错呢！今天是非常愉快的一天 ⌯>ᴗo⌯ .ᐟ.ᐟ",
      "好耶！大概是不经意间看见彩虹的程度吧？",
      "金色光环笼罩，无论做什么都能得到最好的结果。",
      "丰收的季节，硕果累累，让人感受到无尽的喜悦和满足。")),
    (80, "祥吉",
     ("哇哦！特别好运哦！无论是喜欢的事还是不喜欢的事都能全部解决！",
      "哇哦！特别好运哦！今天可以见到心心念念的人哦！",
      "幸运几乎无人能敌，宇宙力量加持，做什么都能取得惊人的成就。",
      "璀璨的星空，每一颗星星都闪耀着耀眼的光芒，让人陶醉其中。")),
    (90, "佳吉",
     ("૮₍ˊᗜˋ₎ა 不用多说，今天怎么度过都会顺意的！",
      "૮₍ˊᗜˋ₎ა  会发生什么好事呢？真是期待...",
      "幸运值已经接近完美，神明庇佑，做什么都能得心应手。",
      "梦幻般的仙境，每一个角落都充满了美好和奇迹。")),
    (100, "最吉",
     ("100， 100诶！不用求人脉，好运自然来！",
      "好...好强！好事都会降临在你身边哦！",
      "哇哦！你的幸运值已经达到了宇宙的极限！仿佛被全世界的幸福和美好所包围！",
      "恭喜你成为宇宙间最幸运的人！愿你的未来永远如同神话般绚烂多彩，好运与你同在！")),
    (0xff, "No way to reach here",
     ("How u reach here", ))
)


def today() -> str:
    """
    Get today's date - 2024.7.7 -> 240707
    :return: format date_string
    """
    return datetime.datetime.now().strftime("%y%m%d")


def luck_tip(val: int) -> tuple[str, str]:
    """
    Select info from luck_info according to luck_val
    :param val: luck_val
    :return: (short_info, long_info)
    """
    for index in range(len(luck_info) - 1):
        if luck_info[index][0] <= val < luck_info[index + 1][0]:
            return luck_info[index][1], random.choice(luck_info[index][2])

    return "Error", "Error"


def luck_generator(user_id: str, bottom: int = 0, top: int = 100) -> int:
    """
    Generate random luck_val at [bottom, top],
    Seed related with user_id and today's date
    :param user_id:
    :param bottom:
    :param top:
    :return: luck_val
    """
    rand = random.Random()
    rand.seed(int(today()) + int(user_id) * random.randint(0, 6))
    return rand.randint(bottom, top)


def get_average(values: list) -> tuple[int, float]:
    """
    Calculate average value of values
    :param values:
    :return: (list length, average value)
    """
    days = len(values)
    average = sum(values) / days
    return days, average


def spdata2dict(spdata: tuple) -> dict:
    keys = ("user_id", "greeting", "bottom", "top")
    ret = {key: val for key, val in zip(keys, spdata)}
    return ret
