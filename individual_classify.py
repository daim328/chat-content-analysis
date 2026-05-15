"""
=============================================================================
Individual Classification — 个体成员对话行为分类
=============================================================================

根据 category standards2 文件，结合 message20260119.xlsx 的对话内容和
dataset2026.xlsx 的个人投票数据，对每位参与者（participant）在
time_risk=0 和 time_risk=1 两种情形下的行为进行分类。

数据流:
  message20260119.xlsx → 逐人审查 → 结合投票 → dataset2026.xlsx

作者: Claude Code
日期: 2026-05-14
=============================================================================
"""

# =============================================================================
# 个体分类标准 / Individual Classification Standards
# 依据: category standards2.docx
# =============================================================================

INDIVIDUAL_STANDARDS = {

    # ------------------------------------------------------------------
    # I1 冷漠 / Indifference
    # ------------------------------------------------------------------
    # 中文: 个体拒绝参与讨论，或表示自己不在乎。
    # English: The individual either refuses to participate in the
    #   discussion or expresses that he does not care.
    # 赋值: 1
    # ------------------------------------------------------------------
    # 判断标准 (Decision Rules):
    #   1. 完全没有发送任何消息（需结合组内他人是否发言区分"整组静默"）
    #   2. 消息中明确表达"不在乎"、"不关心"、"随便"、"都可以"等
    #   3. 消息完全离题（如只聊天气），不参与决策讨论
    #   4. 消息中表达"犹豫不决"、不提供明确立场
    # 关键词 (Keywords):
    #   i dont care, i don't care, i dont mind, whatever, fine with either,
    #   fine with anything, up to you, do what you think, i'm fine with any,
    #   honestly dont really care, i dont really care, undecided,
    #   随便, 无所谓, 都行, 都可以, 不在乎
    # ------------------------------------------------------------------
    1: {
        'name_cn': '冷漠',
        'name_en': 'Indifference',
        'rule': '拒绝参与 或 表达不在乎',
        'keywords': [
            'i dont care', "i don't care", 'i dont mind', "i don't mind",
            'whatever', 'fine with either', 'fine with anything',
            'up to you', 'do what you think', "i'm fine with any",
            'undecided', 'honestly dont really care', "honestly don't really care",
            '随便', '无所谓', '都行', '都可以', '不在乎',
        ],
    },

    # ------------------------------------------------------------------
    # I2 愿意适应 / Willingness to adapt
    # ------------------------------------------------------------------
    # 中文: 持不同偏好的个体决定自愿或在被要求时调整自己的不同决定。
    # English: The individual with differing preferences decides to adapt
    #   either voluntarily or on request.
    # 赋值: 2
    # ------------------------------------------------------------------
    # 判断标准 (Decision Rules):
    #   1. 最初持有不同偏好，但主动表示愿意配合他人 ("ok, I can go with yours")
    #   2. 在他人的明确要求下改变了自己的决定 ("ok sure", "alright then")
    #   3. 初始提出自己的方案，之后明确放弃转向他人方案
    #   4. 投票数据显示 i_risk ≠ final_risk（实际改变了投票）
    # 关键词 (Keywords):
    #   i can go with, fine for me, fine by me, i agree, ok for me,
    #   i will follow, i can also go, sounds good, works for me,
    #   i am fine with, i'm fine with, agree with you, ok sure,
    #   yeah alright, sounds reasonable, i could agree,
    #   if we cannot decide i can also, i'll follow,
    #   可以, 同意, 好的, 没问题, 我跟
    # ------------------------------------------------------------------
    2: {
        'name_cn': '愿意适应',
        'name_en': 'Willingness to adapt',
        'rule': '自愿或在被要求时调整自己的不同决定',
        'keywords': [
            'i can go with', 'fine for me', 'fine by me', 'i agree',
            'ok for me', 'i will follow', "i'll follow", 'i can also go',
            'sounds good', 'works for me', 'i am fine with', "i'm fine with",
            'agree with you', 'ok sure', 'yeah alright', 'sounds reasonable',
            'i could agree', 'if we cannot decide i can also',
            '可以', '同意', '好的', '没问题',
        ],
    },

    # ------------------------------------------------------------------
    # I3 要求他人适应 / Demand to adapt
    # ------------------------------------------------------------------
    # 中文: 个体明确要求他人调整自己不同的决定。
    # English: The individual explicitly prompts others to adapt their
    #   differing decision.
    # 赋值: 3
    # ------------------------------------------------------------------
    # 判断标准 (Decision Rules):
    #   1. 主动提出自己的方案并要求/建议他人采纳
    #   2. 用论证（数学、逻辑等）主导讨论方向并推动他人跟随
    #   3. 提出投票建议 ("let's vote for proposal X")
    #   4. 投票数据显示 i_risk = final_risk 且他人适应（立场坚持并胜出）
    # 注意: 如果推动的方向明显是"更多风险"→I4 或"更少风险"→I6
    # 关键词 (Keywords):
    #   i suggest, i propose, we should, let's vote, let us vote,
    #   should we, i think we should, we can vote, vote for,
    #   shall we, we could, i would suggest, i would propose,
    #   建议, 应该, 投票, 选
    # ------------------------------------------------------------------
    3: {
        'name_cn': '要求他人适应',
        'name_en': 'Demand to adapt',
        'rule': '明确要求他人调整自己不同的决定（非特定风险方向）',
        'keywords': [
            'i suggest', 'i propose', 'we should', "let's vote",
            'let us vote', 'should we', 'i think we should',
            'we can vote', 'vote for', 'shall we', 'we could',
            'i would suggest', 'i would propose', 'lets vote',
            '建议', '应该', '投票',
        ],
    },

    # ------------------------------------------------------------------
    # I4 要求风险或延迟风险 / Demand for risk (delayed risk)
    # ------------------------------------------------------------------
    # 中文: 个体明确要求他人做出更具风险或延迟的决定。
    # English: The individual explicitly prompts others to make a more
    #   risky(-delayed) decision.
    # 赋值: 4
    # ------------------------------------------------------------------
    # 判断标准 (Decision Rules):
    #   1. 明确推动更具风险的选项（更高阈值、更大赌博）
    #   2. 明确推动更长时间等待以换取更高收益
    #   3. 表达"愿意冒险"、"值得等待"等推动风险/延迟的立场
    # 关键词 (Keywords):
    #   risk it, take the risk, go big or go home, no risk no fun,
    #   worth the risk, i like big, take a chance, higher risk,
    #   more risk, i would risk, gamble, worthwhile to wait,
    #   worth waiting, i would wait, wait to get more,
    #   higher point, more money, bigger profit,
    #   冒险, 赌, 值得等, 更多收益, 更高回报
    # ------------------------------------------------------------------
    4: {
        'name_cn': '要求风险或延迟风险',
        'name_en': 'Demand for risk (delayed risk)',
        'rule': '明确要求他人做出更具风险或延迟的决定',
        'keywords': [
            'risk it', "i'd risk", 'take the risk', 'go big or go home',
            'no risk no fun', 'worth the risk', 'i like big',
            'take a chance', 'higher risk', 'more risk', 'i would risk',
            'gamble', 'worthwhile to wait', 'worth waiting',
            'i would wait', 'wait to get more', 'higher point',
            'more money', 'bigger profit', 'worth it', 'definitely',
            '冒险', '赌', '值得等', '更多收益', '更高回报',
        ],
    },

    # ------------------------------------------------------------------
    # I5 接受风险或延迟风险 / Acceptance of risk (delayed risk)
    # ------------------------------------------------------------------
    # 中文: 个体接受并执行风险或延迟风险的要求。
    # English: The individual accepts and implements the demand for risk
    #   (delayed risk).
    # 赋值: 5
    # ------------------------------------------------------------------
    # 判断标准 (Decision Rules):
    #   1. 在他人提出风险/延迟要求后，明确表示接受并执行
    #   2. "ok let's do it that way" 等接受风险方案的表态
    #   注意: 如果接受的是"改变自己不同决定"的要求 → I2 (on request)
    # 关键词 (Keywords):
    #   ok let's, let's do it, i accept, i'll go with that,
    #   fine let's, alright let's, agreeing to risk
    # ------------------------------------------------------------------
    5: {
        'name_cn': '接受风险或延迟风险',
        'name_en': 'Acceptance of risk (delayed risk)',
        'rule': '接受并执行风险或延迟风险的要求',
        'keywords': [
            "ok let's", "let's do it", 'i accept', "i'll go with that",
            "fine let's", "alright let's", 'agreeing to risk',
        ],
    },

    # ------------------------------------------------------------------
    # I6 要求更少延迟风险 / Demand for less delayed risk
    # ------------------------------------------------------------------
    # 中文: 个体明确要求他人做出风险更低或延迟更短的决定。
    # English: The individual explicitly prompts others to make a less
    #   risky-delayed decision.
    # 赋值: 6
    # ------------------------------------------------------------------
    # 判断标准 (Decision Rules):
    #   1. 明确推动更保守的选项（更低阈值、更安全的选择）
    #   2. 明确推动更短等待时间、不想等4周
    #   3. 表达"太冒险"、"不想等"、"安全第一"等立场
    # 关键词 (Keywords):
    #   too risky, too high, too much risk, safer, safe and sure,
    #   not gonna wait, don't want to wait, do not want to wait,
    #   4 weeks is too long, 4 weeks are too long, cannot wait,
    #   rather not, prefer not to, less risk, lower risk,
    #   not a good deal, get it tomorrow, sooner is better,
    #   i prefer tomorrow, i want it now, i dont want to wait,
    #   don't want to have to come back, not motivated to come,
    #   i won't be here, ill forget, i'll forget, vacation,
    #   no interest in waiting, not worth waiting,
    #   不想等, 太冒险, 太长了, 等不了, 不安全
    # ------------------------------------------------------------------
    6: {
        'name_cn': '要求更少延迟风险',
        'name_en': 'Demand for less delayed risk',
        'rule': '明确要求他人做出风险更低或延迟更短的决定',
        'keywords': [
            'too risky', 'too high', 'too much risk', 'safer',
            'safe and sure', 'not gonna wait', "don't want to wait",
            'do not want to wait', '4 weeks is too long',
            '4 weeks are too long', 'cannot wait', 'rather not',
            'prefer not to', 'less risk', 'lower risk',
            'not a good deal', 'get it tomorrow', 'sooner is better',
            'i prefer tomorrow', 'i want it now', 'i dont want to wait',
            "don't want to have to come back", 'not motivated to come',
            "i won't be here", "ill forget", "i'll forget", 'vacation',
            'no interest in waiting', 'not worth waiting',
            '不想等', '太冒险', '太长了', '等不了', '不安全',
        ],
    },

    # ------------------------------------------------------------------
    # I7 接受更多延迟风险 / Acceptance of more delayed risk
    # ------------------------------------------------------------------
    # 中文: 个体接受并执行更多延迟风险的要求。
    # English: An individual accepts and implements the demand for more
    #   delayed risk.
    # 赋值: 7
    # ------------------------------------------------------------------
    # 判断标准 (Decision Rules):
    #   1. 在他人提出更多延迟风险要求后，明确接受并执行
    #   2. 接受更长的等待时间方案
    #   关键词 (Keywords):
    #   accept more delay, ok more waiting, fine with waiting more
    # ------------------------------------------------------------------
    7: {
        'name_cn': '接受更多延迟风险',
        'name_en': 'Acceptance of more delayed risk',
        'rule': '接受并执行更多延迟风险的要求',
        'keywords': [
            'accept more delay', 'ok more waiting', 'fine with waiting more',
        ],
    },
}

# =============================================================================
# 分类判断优先级 (Tie-breaking order)
# =============================================================================
# 当一条消息匹配多个类别的关键词时，按以下优先级判断：
#   I1 (冷漠) > I4 (要求更多风险) > I6 (要求更少风险) > I3 (要求适应) > I2 (愿意适应)
#   I7 > I5 (接受型优先级较低，通常与 I2 合并)
#
# 基本原则:
#   1. 先判断是否为 I1（不参与/不在乎）—— 如果是，不再考虑其他
#   2. 再判断风险方向: 推动更多风险/延迟 → I4；推动更少风险/更短延迟 → I6
#   3. 方向不明的一般性要求他人适应 → I3
#   4. 接受他人的要求 → I2 (on request) 或 I5 (风险接受) 或 I7 (延迟接受)
#   5. 无法判断 → 默认为 I2（愿意适应）
# =============================================================================

import pandas as pd
import numpy as np
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_FILE = os.path.join(BASE_DIR, 'message20260119.xlsx')
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')


# =============================================================================
# 1. 聊天内容分类 — 基于对话文本的 I1-I7 判断
# =============================================================================

def classify_from_chat():
    """
    读取 message20260119.xlsx，对每位参与者在每个 time_risk 下的
    所有消息进行逐条分析，按 category standards2 的 I1-I7 标准分类。

    返回: dict[participant_code][time_risk] = 1-7

    分类依据：通读全部 851 条消息，结合每条消息的语气、立场和互动模式。
    """
    I = {}

    # ========================
    # session: bbgfffw6 (majority=0)
    # ========================

    # Group 1 (TR=0, TR=1)
    I['ncmbeu96'] = {0: 3, 1: 3}    # TR0: 用数学论证主导讨论，要求他人适应;
                                      # TR1: 同样用数学论证主导
    I['w925dou6'] = {0: 2, 1: 2}    # TR0: 最初犹豫后适应P1;
                                      # TR1: 适应方案2
    I['6ogvjie9'] = {0: 2, 1: 3}    # TR0: 最初有不同偏好但最终适应;
                                      # TR1: 主动提议方案2

    # Group 2 (TR=0, TR=1)
    I['rx0314r2'] = {0: 2, 1: 2}    # TR0: 最初反对后转为同意;
                                      # TR1: 快速同意
    I['hj311cpt'] = {0: 3, 1: 3}    # TR0: 推动自己立场;
                                      # TR1: 建议中间方案
    I['qirxmn9p'] = {0: 3, 1: 2}    # TR0: 先是要求他人适应，后自己适应;
                                      # TR1: 同意他人

    # Group 3 (TR=0, TR=1)
    I['4t7f8z8s'] = {0: 2, 1: 2}    # TR0: 同意方案2; TR1(G4): 适应
    I['7g3hzz4a'] = {0: 3, 1: 2}    # TR0: 推动立场; TR1: 表示都可以
    I['yj9as5vl'] = {0: 2, 1: 3}    # TR0: 提议方案2; TR1: 推动立场
    I['tiakgq4z'] = {0: 4, 1: None} # TR0: 想赌博冒险 ("I'd risk it")
    I['hoxtva6l'] = {0: 2, 1: None} # TR0: 质疑后同意
    I['mfodxdqr'] = {0: 2, 1: None} # TR0: 同意他人方案

    # Group 4 / Group 5 (跨组)
    I['os109bhi'] = {0: 3, 1: 3}    # TR0(G5): 提议折中方案; TR1(G4): 主导讨论
    I['xqu5dupq'] = {0: 2, 1: 2}    # TR0(G5): 提议后适应; TR1(G4): 同意
    I['gpsmk0bn'] = {0: 2, 1: 2}    # TR0(G5): 同意; TR1(G4): 同意

    # Group 6
    I['vssecnms'] = {0: 3, 1: 2}    # TR0: 推动立场; TR1: 同意
    I['p8s0es6v'] = {0: 3, 1: 2}    # TR0: 推动立场; TR1: 同意
    I['aa4qjckr'] = {0: 2, 1: 2}    # TR0: 同意; TR1: 同意

    # ========================
    # session: 6hgrim4b (majority=1)
    # ========================

    # Group 1
    I['56ojdphm'] = {0: 3, 1: None}  # 发起讨论 "Proposal 1 or 2?"
    I['ug12cypl'] = {0: 4, 1: None}  # 建议冒险方案
    I['4yd2gptl'] = {0: 2, 1: None}  # 快速同意
    I['o81zm9mi'] = {0: None, 1: 6}  # 质疑等待价值 → 要求更少延迟

    # Group 2
    I['z4mli9ey'] = {0: 3, 1: None}  # 主导提议
    I['cj1ji23x'] = {0: 2, 1: None}  # 同意
    I['tj4dj7ix'] = {0: 2, 1: None}  # 同意
    I['b1ljp7hw'] = {0: None, 1: 4}  # TR1: "80-90% it's worthwhile to wait" → 要求更多风险/延迟
    I['n6gyc5p4'] = {0: None, 1: 4}  # TR1: "9,10 definitely" → 要求更多风险/延迟
    I['epbcekix'] = {0: None, 1: 6}  # TR1: 不愿等待，最终适应 → 要求更少延迟

    # Group 3
    I['ehz7bo8w'] = {0: 2, 1: 2}    # TR0: 同意; TR1: 适应
    I['wbyf9v3z'] = {0: 2, 1: 6}    # TR0: 同意; TR1: 要求更少延迟
    I['h711c9j8'] = {0: 2, 1: 3}    # TR0: 表示都可以; TR1: 质疑并主导讨论

    # ========================
    # session: nzsz5b21 (majority=1, TR=0 only)
    # ========================
    I['tz13p6oq'] = {0: 2, 1: None}  # "I'll follow trend" → 愿意适应
    I['rh2p1guk'] = {0: 2, 1: None}  # "If we cannot decide, I can also go for 3" → 愿意适应
    I['5tju8bwm'] = {0: 3, 1: None}  # 推动选择 "3"
    I['wntam0iz'] = {0: 6, 1: None}  # "i dont want to wait 4 weeks" → 要求更少延迟

    # ========================
    # session: f8edwq9b (majority=1)
    # ========================

    # Group 4/6
    I['qsx3cu9b'] = {0: 3, 1: 3}    # TR0(G6): 主导讨论; TR1(G4): 主导
    I['ne9tcre6'] = {0: 3, 1: 2}    # TR0(G6): 提供数学论证; TR1(G4): 同意
    I['hvrtd05u'] = {0: 2, 1: 2}    # TR0(G6): 附和; TR1(G4): 附和

    # Group 5/7
    I['dn7y6gxh'] = {0: 3, 1: 6}    # TR0(G7): 主导讨论; TR1(G5): "why do you want to wait so long for 2 euros"
                                      # → 明确要求更少延迟
    I['ads1z9m5'] = {0: 2, 1: 6}    # TR0(G7): 同意; TR1(G5): 更少等待偏好
    I['g4fja7tj'] = {0: 4, 1: 4}    # TR0(G7): "no risk no fun" → 追求风险;
                                      # TR1(G5): 追求风险

    # Group 6/8
    I['890ews6l'] = {0: 3, 1: 4}    # TR0(G8): 挑战他人立场; TR1(G6): 推动等待/风险
    I['zlh5tdu5'] = {0: 3, 1: 2}    # TR0(G8): 推动自己方案; TR1(G6): 最终适应

    # Group 7/9
    I['4ecrweb0'] = {0: 3, 1: 3}    # TR0(G9): 提议中间方案; TR1(G7): 主导提议
    I['0vm3ban9'] = {0: 2, 1: 3}    # TR0(G9): 同意; TR1(G7): 首先提议
    I['j1umjk3z'] = {0: 2, 1: 2}    # TR0(G9): 同意; TR1(G7): 同意

    # Group 8/10
    I['671jyleo'] = {0: 3, 1: 1}    # TR0(G10): 主导评论; TR1(G8): "weather is nice innit" → 离题，冷漠
    I['2avp2prt'] = {0: 2, 1: None} # TR0(G10): 同意

    # ========================
    # session: dkoekgf5 (majority=0)
    # ========================

    # Group 7
    I['ltkdu9m4'] = {0: 3, 1: 2}    # TR0: 提议折中方案; TR1: 同意
    I['5izm8ier'] = {0: 2, 1: 3}    # TR0: 同意; TR1: 提替代方案
    I['ur8cpf1h'] = {0: 2, 1: 2}    # TR0: 同意; TR1: 同意

    # Group 8
    I['s8g1e7mj'] = {0: 3, 1: 3}    # TR0: 提议折中; TR1: 提议方案2
    I['5pdq9e73'] = {0: 2, 1: 2}    # TR0: 同意; TR1: 同意
    I['lf6j1q36'] = {0: 1, 1: 1}    # TR0: "very undecided"; TR1: "undecided about situation 5"
                                      # → 始终犹豫不决 = 不积极参与 = 冷漠

    # Group 9
    I['9hydcim4'] = {0: 3, 1: None}  # TR0: 推动更多风险 "we should take 60%"
    I['7u8nblcm'] = {0: 2, 1: None}  # TR0: 同意折中
    I['rkkv0lh9'] = {0: 2, 1: None}  # TR0: 适应折中

    # Group 9/10 (TR=1)
    I['8qn9nh3b'] = {0: 2, 1: 6}    # TR0(G10): 适应; TR1(G9): "not motivated to come again in 4 weeks"
                                      # → 不愿等待
    I['hwcutjyi'] = {0: 3, 1: 2}    # TR0(G10): 推动立场; TR1(G9): 配合
    I['wca7iev8'] = {0: 3, 1: 3}    # TR0(G10): 主导提议; TR1(G9): 提议选项

    # Group 10/11
    I['4vn5iz9u'] = {0: 3, 1: 2}    # TR0(G11): 推动50%立场; TR1(G10): 适应
    I['vycv5y5a'] = {0: 3, 1: 3}    # TR0(G11): 主导折中 "meet in the middle at 60%";
                                      # TR1(G10): 提议折中
    I['nrxq26t9'] = {0: 2, 1: None}  # TR0: 适应折中

    # Group 12
    I['9o5z6npd'] = {0: 6, 1: None}  # TR0: "choose A for No.5" → 明确要求更少风险
    I['2w4ilsxf'] = {0: 2, 1: None}  # TR0: 同意
    I['cjt74r1o'] = {0: 2, 1: None}  # TR0: 提醒投票一致性

    # ========================
    # session: 0f9u4oto (majority=1)
    # ========================

    # Group 9/11
    I['lt35om27'] = {0: 3, 1: 3}    # TR0(G11): 提议投票; TR1(G9): 提议中间方案
    I['zi7p95ny'] = {0: 2, 1: 2}    # TR0(G11): 同意; TR1(G9): 同意
    I['f5j9rxu9'] = {0: 3, 1: 2}    # TR0(G11): 主导; TR1(G9): 数学论证后适应

    # Group 10/12
    I['mldp6kdi'] = {0: 3, 1: 1}    # TR0(G12): 提议投票; TR1(G10): "hello" "+" → 极低参与
    I['uxkihpwg'] = {0: 2, 1: 3}    # TR0(G12): 同意; TR1(G10): 提议中间方案
    I['54o8c01l'] = {0: 2, 1: 2}    # TR0: 同意; TR1: 同意

    # ========================
    # session: 8kn3iz3d
    # ========================
    I['vqcyaekn'] = {0: 3, 1: 3}    # TR0(G7): 主导提议; TR1(G6): 指出多数，主导
    I['84h1hu66'] = {0: 2, 1: 2}    # TR0(G7): 同意; TR1(G6): 同意
    I['jg63k1y5'] = {0: 2, 1: 2}    # TR0(G7): 同意; TR1(G6): 适应

    # ========================
    # session: 6apbq166
    # ========================

    # Group 12/13
    I['rghhx8hh'] = {0: 2, 1: 2}    # TR0(G13): 同意; TR1(G12): 适应后提议
    I['jxqfasml'] = {0: 2, 1: 3}    # TR0(G13): 同意; TR1(G12): 推动等待
    I['3z868bro'] = {0: 2, 1: 6}    # TR0(G13): 表示无所谓; TR1(G12): "4 weeks is a long time" → 反对等待

    # Group 13/14
    I['bvph8u1v'] = {0: 3, 1: 1}    # TR0(G14): 主导提议; TR1(G13): "whatever" → 冷漠
    I['obs7t4q0'] = {0: 2, 1: 6}    # TR0(G14): 适应; TR1(G13): "im not gonna wait 4 weeks" → 坚决反对等待
    I['zvmba2hz'] = {0: 3, 1: 4}    # TR0(G14): 提议中间方案; TR1(G13): "I would wait four weeks to get more money"
                                      # → 愿意等待更多收益

    # ========================
    # session: thex540s
    # ========================

    # Group 13/11
    I['gbqvph97'] = {0: 3, 1: 6}    # TR0(G13): 指出已有多数; TR1(G11): 无法到场，反对延迟
    I['gpfru5fz'] = {0: 2, 1: 3}    # TR0(G13): 同意; TR1(G11): 主导讨论
    I['2m2gvym1'] = {0: 2, 1: 2}    # TR0(G13): 同意; TR1(G11): 适应

    # Group 14
    I['muwupzmk'] = {0: 6, 1: None}  # TR0: "4 and 4 is safer" → 明确要求更少风险
    I['elvh3j0w'] = {0: 2, 1: None}  # TR0: 推动风险但最终同意折中
    I['48mnzzpe'] = {0: 2, 1: None}  # TR0: 被说服适应

    # ========================
    # session: moe0awio
    # ========================

    # Group 14/17
    I['5m6eokuf'] = {0: 4, 1: 4}    # TR0(G17): "go big or go home" → 追求高风险;
                                      # TR1(G14): "i like big $$" → 追求高风险
    I['ll6dsdgb'] = {0: 2, 1: 2}    # TR0(G17): 抵制后服从多数; TR1(G14): 不同意后适应
    I['w7a8aaj0'] = {0: 3, 1: 3}    # TR0(G17): 推动民主投票; TR1(G14): 推动投票

    # Group 13/16
    I['ctxmjlm2'] = {0: 3, 1: 3}    # TR0(G16): 数学论证主导; TR1(G13): 主导讨论
    I['f1g62gra'] = {0: 2, 1: 2}    # TR0(G16): 同意; TR1(G13): 同意
    I['4dd8h4bq'] = {0: 2, 1: 2}    # TR0(G16): 同意; TR1(G13): 同意

    # Group 12/15
    I['5wc937fh'] = {0: 2, 1: 3}    # TR0(G15): 表示可以; TR1(G12): 主导提议
    I['9l5zm41p'] = {0: 2, 1: 2}    # TR0(G15): 同意; TR1(G12): 同意
    I['fpqmm059'] = {0: None, 1: 2}  # TR1(G12): 表示同意

    # ========================
    # session: l1u9ytue
    # ========================

    # Group 14/15
    I['to8qhvbi'] = {0: 3, 1: 2}    # TR0(G15): 主导提议; TR1(G14): 适应
    I['tyxazhzc'] = {0: 2, 1: 1}    # TR0(G15): 同意; TR1(G14): "don't really care" → 不在乎
    I['8ntxu93h'] = {0: 2, 1: 6}    # TR0(G15): 同意; TR1(G14): 偏向不等待

    # Group 15/16
    I['1gerc30m'] = {0: 3, 1: 2}    # TR0(G16): 主导协商; TR1(G15): 适应
    I['3jqz1v5q'] = {0: 2, 1: 2}    # TR0(G16): 冒险派，最终同意折中; TR1(G15): 同意
    I['dljhygqr'] = {0: 2, 1: 3}    # TR0(G16): 风险厌恶，适应折中; TR1(G15): 主导提议

    # Group 17
    I['3cgbergw'] = {0: 3, 1: None}  # TR0: 提议中间方案（仅1条消息）

    # ========================
    # session: f0el3eip
    # ========================

    # Group 16/18
    I['ogjqbbqv'] = {0: 6, 1: 2}    # TR0(G18): "let's do option A until 50%" → 明确要求更少风险;
    I['bin13zaw'] = {0: 3, 1: 2}    # TR0(G18): 论证风险中性; TR1(G16): 同意方案1

    # Group 17/19
    I['t2m5a7ev'] = {0: 4, 1: 3}    # TR0(G19): "no risk no fun" → 推动更多风险;
                                      # TR1(G17): 主导提议
    I['j4lmty8b'] = {0: 2, 1: 6}    # TR0(G19): 同意; TR1(G17): "kein interesse...4 wochen" → 不愿等4周
    I['38cndqe5'] = {0: 2, 1: 2}    # TR0(G19): 同意; TR1(G17): 同意

    # ========================
    # session: noias7kj
    # ========================

    # Group 15/18
    I['ho43nz77'] = {0: 2, 1: 2}    # TR0(G18): 同意; TR1(G15): 同意
    I['jqul0rpn'] = {0: 3, 1: 6}    # TR0(G18): 解释立场; TR1(G15): "4 Weeks a lot of time" → 觉得4周太长
    I['f5fsh83e'] = {0: 1, 1: 3}    # TR0(G18): "I dont care" → 不在乎;
                                      # TR1(G15): 推动快速决策

    # Group 16/19
    I['l2x4f2m5'] = {0: 3, 1: None}  # TR0(G19): 要求P1适应
    I['rhhck5ce'] = {0: 3, 1: 6}    # TR0(G19): 数学论证; TR1(G16): "I wont be in Heidelberg in four weeks"
                                      # → 无法到场，反对延迟
    I['b4scyfme'] = {0: 2, 1: 2}    # TR0(G19): 质疑后同意; TR1(G16): "ok sure" → 被要求时适应

    # ========================
    # session: c29h9lab
    # ========================

    # Group 18/20
    I['txkohpoy'] = {0: 2, 1: 2}    # TR0(G20): 同意; TR1(G18): 同意
    I['ntpj6k3y'] = {0: 3, 1: 1}    # TR0(G20): 主导提议; TR1(G18): "I dont care if I get it tomorrow or in four weeks"
                                      # → 不在乎时间
    I['va4iv92o'] = {0: 2, 1: 6}    # TR0(G20): 同意; TR1(G18): "sooner is better" → 偏向更早

    # Group 19/21
    I['3ykoed4m'] = {0: 3, 1: 2}    # TR0(G21): 主导; TR1(G19): 同意
    I['mvlrigx2'] = {0: 2, 1: 3}    # TR0(G21): 适应; TR1(G19): 主导

    # Group 20/22
    I['2yaken99'] = {0: 4, 1: 1}    # TR0(G22): "12 points > 8 points" → 推动更多风险;
                                      # TR1(G20): "okay with whatever" → 不在乎
    I['rzjg5ms6'] = {0: 2, 1: 1}    # TR0(G22): 适应折中; TR1(G20): 开玩笑 "its gameeeeeee" → 不在乎
    I['u1d934qi'] = {0: 2, 1: 2}    # TR0(G22): 质疑后同意; TR1(G20): 同意

    # ========================
    # session: 9uypl6dx
    # ========================

    # Group 18/21
    I['bjlkg2c6'] = {0: 3, 1: 3}    # TR0(G21): 提问，主导; TR1(G18): 提问，主导
    I['wtuk7z9j'] = {0: 3, 1: 2}    # TR0(G21): 数学论证; TR1(G18): 适应
    I['3mhvxa5r'] = {0: 2, 1: 2}    # TR0(G21): 同意; TR1(G18): 同意

    # ========================
    # session: 32qq2463
    # ========================

    # Group 19/22
    I['g1tvlvk8'] = {0: 2, 1: 6}    # TR0(G22): 同意; TR1(G19): "i dont want that much risk ... wait"
                                      # → 不愿冒险+等待
    I['nv74wiwy'] = {0: 2, 1: 4}    # TR0(G22): 同意; TR1(G19): "why not select the higher point one?"
                                      # → 要求50-50冒险
    I['6nm4aea5'] = {0: 3, 1: 2}    # TR0(G22): 发起变更; TR1(G19): 提问后同意

    # ========================
    # session: y1hj2aj2
    # ========================

    # Group 17/20
    I['nfy1ut59'] = {0: 3, 1: 3}    # TR0(G20): 推动风险中性; TR1(G17): 推动风险
    I['hqox7ku0'] = {0: 6, 1: 2}    # TR0(G20): "more sensitive to lose 50%" → 厌恶损失;
                                      # TR1(G17): "Alright" → 适应
    I['ryn74uw6'] = {0: 2, 1: 2}    # TR0(G20): 同意; TR1(G17): 同意

    # ========================
    # session: zspnbitg
    # ========================

    # Group 20/24
    I['04ybbykm'] = {0: 3, 1: 6}    # TR0(G24): 解释，主导; TR1(G20): "selected all 10 because tomorrow 100% safe"
                                      # → 想明天拿钱
    I['gol08cao'] = {0: 3, 1: 2}    # TR0(G24): 提议; TR1(G20): 适应
    I['qht1ncs7'] = {0: 2, 1: 3}    # TR0(G24): 适应; TR1(G20): 主导提议

    # Group 23
    I['wdyjnja3'] = {0: 3, 1: None}  # TR0: 提议 "A until 7"
    I['mnorf4z6'] = {0: 6, 1: None}  # TR0: "A for all positions. Safe and sure" → 主张保守

    # ========================
    # session: 1gzf7p6u
    # ========================

    # Group 21/23
    I['fe11vpqw'] = {0: 3, 1: 3}    # TR0(G23): 主导; TR1(G21): 提议折中
    I['bw3qty6c'] = {0: 2, 1: 2}    # TR0(G23): 同意; TR1(G21): 同意
    I['lxyawqvz'] = {0: 2, 1: None}  # TR0(G23): "ok" → 同意

    # ========================
    # session: ymgl8k4i (TR=0 and TR=1)
    # ========================

    # Group 22/26
    I['dufx3vxe'] = {0: 3, 1: 3}    # TR0(G26): 主导最大化收益; TR1(G22): 主导
    I['ee6sjzk2'] = {0: 2, 1: 2}    # TR0(G26): 同意; TR1(G22): "Fine by me" → 同意

    # Group 23/27
    I['cbe3hywl'] = {0: 6, 1: 6}    # TR0(G27): "less risky to choose B from 70% onward" → 要求更低风险;
                                      # TR1(G23): "4 weeks is an amount of time i can wait" → 要求更少延迟风险
    I['gr8r5tzp'] = {0: 3, 1: 3}    # TR0(G27): 主导提议; TR1(G23): 主导
    I['f5g4wfzh'] = {0: 2, 1: 2}    # TR0(G27): 同意; TR1(G23): 同意

    # Group 24
    I['h9pn79r3'] = {0: None, 1: 3}  # TR1: 推动立场
    I['z6l5xogp'] = {0: None, 1: 2}  # TR1: 适应

    # Group 25 (TR=0 only)
    I['qr344o7n'] = {0: 2, 1: None}  # 同意他人
    I['2ye352y6'] = {0: 1, 1: None}  # "do what you think it's best" → 冷漠

    # Group 26 (TR=0 only)
    I['o2huph9r'] = {0: 2, 1: None}  # 同意 "ok that's fine"

    # Group 28 (TR=0 only)
    I['1eicckha'] = {0: 3, 1: None}  # "50/50 is too high...you should lower the risk" → 要求P1降低风险

    # ========================
    # session: vfgv3mdk (TR=1 only)
    # ========================
    I['19cpp9r7'] = {0: None, 1: 6}  # "In 4 weeks ill forget" → 坚决不等待
    I['9ms0nc71'] = {0: None, 1: 2}  # "Yeah alright" → 被要求时适应
    I['fk67q6oc'] = {0: None, 1: 2}  # "sounds reasonable" → 被要求时适应

    # ========================
    # session: tx1s5v14 (TR=0 only)
    # ========================
    I['qx3jcxwr'] = {0: 3, 1: None}  # 提议折中 "A until 6 and B from 7 onwards?"
    I['kmh1o20i'] = {0: 2, 1: None}  # "Fine for me" → 同意
    I['9uwjw5gr'] = {0: 2, 1: None}  # "yes" → 同意

    return I


# =============================================================================
# 2. 投票数据修正 — 结合个人投票行为调整分类
# =============================================================================

def apply_individual_classification():
    """
    主函数：
      1. 加载聊天分类
      2. 加载投票数据
      3. 填补 NaN（无聊天数据的参与者 → 用投票数据推断）
      4. 修正聊天与投票明显矛盾的情况
      5. 输出到 dataset2026.xlsx
    """
    print("=" * 60)
    print("Individual Classification — Chat + Voting Combined")
    print("=" * 60)

    ds = pd.read_excel(DATASET_FILE)
    I = classify_from_chat()
    changes_log = []

    for tr in [0, 1]:
        i_adj = f'individual_categories{tr+1}_adjusted'
        i_exist = f'individual_categories{tr+1}'
        risk_col = f'i{"" if tr == 0 else "_time"}_risk'
        final_col = f'final{"" if tr == 0 else "_time"}_risk'
        vote_col = f'{"risk" if tr == 0 else "time_risk"}_vote1'
        round_col = f'round{tr+1}'

        print(f"\n{'=' * 60}")
        print(f"TR={tr}")
        print(f"{'=' * 60}")

        # Step 1: Apply chat-based classification
        chat_map = {pc: I[pc].get(tr) for pc in I if I[pc].get(tr) is not None}
        ds[i_exist] = ds['subject_code'].map(chat_map)
        n_chat = ds[i_exist].notna().sum()
        print(f"  Chat classified: {n_chat}/{len(ds)}")

        # Step 2: Build group-level voting summary for NaN fill + adjustment
        grp = ds.groupby('group1').agg(
            p1_risk=(risk_col, lambda x: x.iloc[0] if len(x) > 0 else np.nan),
            p2_risk=(risk_col, lambda x: x.iloc[1] if len(x) > 1 else np.nan),
            p3_risk=(risk_col, lambda x: x.iloc[2] if len(x) > 2 else np.nan),
            p1_subj=('subject_code', lambda x: x.iloc[0]),
            p2_subj=('subject_code', lambda x: x.iloc[1] if len(x) > 1 else ''),
            p3_subj=('subject_code', lambda x: x.iloc[2] if len(x) > 2 else ''),
            final_val=(final_col, 'first'),
            winner=(vote_col, 'first'),
        ).reset_index()

        def init_pattern(r):
            vals = {r.p1_risk, r.p2_risk, r.p3_risk} - {np.nan}
            if len(vals) == 1:
                return 'unanimous'
            if len(vals) == 2:
                return 'majority'
            if len(vals) == 3:
                return 'all_diff'
            return 'unknown'

        grp['pattern'] = grp.apply(init_pattern, axis=1)

        # Step 3: Build individual classification from voting (for NaN fill)
        subj_i_vote = {}
        subj_adapted = {}
        subj_winner = {}
        subj_pattern = {}

        for _, r in grp.iterrows():
            for p_idx, p_key in enumerate([1, 2, 3]):
                s = r[f'p{p_key}_subj']
                if not s:
                    continue
                adapted = r[f'p{p_key}_risk'] != r['final_val']
                won = r['winner'] == p_key
                subj_adapted[s] = adapted
                subj_winner[s] = won
                subj_pattern[s] = r['pattern']

                if adapted:
                    subj_i_vote[s] = 2  # I2: adapted vote
                elif won:
                    subj_i_vote[s] = 3  # I3: their position won
                else:
                    subj_i_vote[s] = 2  # I2: default

        # Step 4: Start with chat, adjust with voting
        ds[i_adj] = ds[i_exist].copy()

        for idx, row in ds.iterrows():
            s = row['subject_code']
            i_chat = row[i_exist]

            if pd.isna(i_chat):
                # No chat data → fill from voting
                ds.at[idx, i_adj] = subj_i_vote.get(s, 1)
            else:
                adapted = subj_adapted.get(s)
                winner = subj_winner.get(s)
                pattern = subj_pattern.get(s)

                if adapted is None:
                    continue  # Can't adjust without voting data

                # Adjust: I3 + adapted vote in majority → I2
                if i_chat == 3 and adapted and pattern == 'majority':
                    ds.at[idx, i_adj] = 2
                    changes_log.append(f"TR{tr} {s}: I3→I2 (adapted vote in majority)")

                # Adjust: I2 + held position + won → I3
                elif i_chat == 2 and not adapted and winner:
                    ds.at[idx, i_adj] = 3
                    changes_log.append(f"TR{tr} {s}: I2→I3 (held position + won)")

                # Otherwise keep chat-based

        # Convert
        ds[i_exist] = ds[i_exist].astype('Int64')
        ds[i_adj] = ds[i_adj].astype('Int64')

        # Report
        orig = dict(sorted(ds[i_exist].value_counts().items()))
        adj = dict(sorted(ds[i_adj].value_counts().items()))
        changed = (ds[i_adj] != ds[i_exist]).sum()
        na_filled = ds[i_exist].isna().sum()
        print(f"\n  Original:  {orig}")
        print(f"  Adjusted:  {adj}")
        print(f"  NaN filled: {na_filled}")
        print(f"  Total changed: {changed}")

    # Final report
    print(f"\n{'=' * 60}")
    print(f"调整记录 ({len(changes_log)} 条):")
    for c in changes_log:
        print(f"  {c}")

    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"\n结果已保存至: {OUTPUT_FILE}")
    print("程序执行完毕。")

    return ds


if __name__ == '__main__':
    ds = apply_individual_classification()
