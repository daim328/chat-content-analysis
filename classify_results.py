"""
=============================================================================
集体决策对话分类程序
Group & Individual Classification of Chat Conversations
=============================================================================

功能：读取 message20260119.xlsx 中的小组对话数据，对每个小组（group）和每个个体成员
      （participant_code）在两种决策情景（time_risk=0 纯风险决策 / time_risk=1 延迟风险决策）
      下进行分类，并将结果写入 dataset2026.xlsx。

分类体系：
  Group 层面 (G1-G4):
    G1 = 多数原则 (Majority principle): 两人选择相同，第三人适应
    G2 = 折中 (Compromise): 协商后在初始选择之间达成一致
    G3 = 少数驱动 (Minority): 单人推动决策，他人冷漠或被动
    G4 = 一致同意 (Unanimity): 首轮对话即全体同意同一方案

  Individual 层面 (I1-I7):
    I1 = 冷漠 (Indifference): 拒绝参与或表示不在乎
    I2 = 愿意适应 (Willingness to adapt): 主动改变自己的不同决定
    I3 = 要求他人适应 (Demand to adapt): 明确要求他人调整决定
    I4 = 要求更多风险/延迟 (Demand for risk/delayed risk): 推动更冒险/延迟的决定
    I5 = 接受风险/延迟要求 (Acceptance of risk/delayed risk): 接受并执行风险要求
    I6 = 要求更少延迟风险 (Demand for less delayed risk): 推动更保守/更少延迟的决定
    I7 = 接受更多延迟风险 (Acceptance of more delayed risk): 接受并执行更多延迟风险要求

数据流：
  message20260119.xlsx (对话数据) → 逐会话分类 → 映射到 dataset2026.xlsx (个体层面数据)

注意事项：
  - 同一参与者在不同 time_risk 条件下可能属于不同的 msg_group
  - 因此分别构建 TR=0 和 TR=1 的映射桥接
  - 未参与对话的个体保持 NaN

作者: Claude Code 辅助分类
日期: 2026-05-03
=============================================================================
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
import os

# =============================================================================
# 0. 路径配置
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_FILE = os.path.join(BASE_DIR, 'message20260119.xlsx')
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE  = os.path.join(BASE_DIR, 'dataset2026.xlsx')


# =============================================================================
# 1. Group 层面分类 (G1-G4)
# =============================================================================
# 分类依据：通读 97 个对话会话后，根据对话模式进行定性判断。
# 每个 msg_group × time_risk 组合独立分类。
#
# 判断标准：
#   G4 (一致同意): 消息数极少(≤5条)，首轮即达成共识，无实质性协商
#   G1 (多数原则): 两人初始立场一致或快速达成一致，第三人明确改变立场适应
#   G2 (折中): 经过讨论后采取中间方案，"middle", "compromise", "meet in between"
#   G3 (少数驱动): 一人主导整个讨论方向，其他人较为被动或表示无所谓

def build_group_classification():
    """
    返回字典: G[msg_group][time_risk] = 分类值 (1-4)

    以下分类基于对所有 97 个对话会话的逐条内容分析。
    每个 msg_group 的对话摘要详见分析记录。
    """
    G = {}

    # Group 1
    # TR=0: P1(ncmbeu96) 用数学论证主导讨论，P2(w925dou6) 和 P3(6ogvjie9)
    #        最初犹豫后均适应 P1 的立场 → G1（两人适应一人）
    # TR=1: 快速一致同意方案2（14条消息，无争议） → G4
    G[1]  = {0: 1, 1: 4}

    # Group 2
    # TR=0: P3(qirxmn9p) 初始主张方案2，经 P1(rx0314r2) 反对后转向方案1，
    #        P2(hj311cpt) 基本沉默缺席 → P1 的立场最终获胜，多数原则 → G1
    # TR=1: P2(b1ljp7hw) 和 P3(n6gyc5p4) 推动更多风险/等待，
    #        P1(epbcekix) 最终适应 → G1
    G[2]  = {0: 1, 1: 1}

    # Group 3
    # TR=0: 两次会话均为快速一致同意（maj=0: 7条; maj=1: 5条） → G4
    # TR=1: 两次会话均为快速一致同意（maj=0: P1 适应 P2/P3; maj=1: P3 主导后一致） → G4
    G[3]  = {0: 4, 1: 4}

    # Group 4
    # TR=0: 快速就方案2达成一致（maj=0: 7条），maj=1 仅1条消息 → G4
    # TR=1: maj=0 即时一致同意方案2（4条），maj=1 快速讨论后同意 P1 → G4
    G[4]  = {0: 4, 1: 4}

    # Group 5
    # TR=0: P1(os109bhi) 提议折中 "Should we come to an agreement in the middle?
    #        Proposal 1?" → 明确妥协 → G2
    # TR=1: 两次会话均快速一致同意 → G4
    G[5]  = {0: 2, 1: 4}

    # Group 6
    # TR=0: maj=0 讨论风险百分比达成折中; maj=1 数学讨论后折中于 P2 → G2
    # TR=1: maj=0 两人（P1+P3）立场相同，P2 适应; maj=1 P3 适应 P1 → G1
    G[6]  = {0: 2, 1: 1}

    # Group 7
    # TR=0: 两个 maj=0 会话均为折中方案; maj=1 讨论后妥协 → G2
    # TR=1: 两个会话均快速一致同意 → G4
    G[7]  = {0: 2, 1: 4}

    # Group 8
    # TR=0: P1 明确说 "I think its a compromise" → G2
    # TR=1: 快速一致同意 P2（maj=0），maj=1 仅2条离题消息 → G4
    G[8]  = {0: 2, 1: 4}

    # Group 9
    # TR=0: maj=0 折中于 60%; maj=1 折中于中间方案 → G2
    # TR=1: maj=0 折中于方案2; maj=1 折中于中间方案 → G2
    G[9]  = {0: 2, 1: 2}

    # Group 10
    # TR=0: P2 和 P3 立场一致（maj=0），P1 跟随（maj=1） → G1
    # TR=1: P3 提出建议，P2 适应（P1 基本不参与） → G3
    G[10] = {0: 1, 1: 3}

    # Group 11
    # TR=0: 三方各陈述偏好(50/60/70)后折中于 60% → G2
    # TR=1: P1 坚决反对等待4周，P2+P3 接受 → G3（单人驱动）
    G[11] = {0: 2, 1: 3}

    # Group 12
    # TR=0: maj=0 快速一致同意A方案（4条）; maj=1 快速一致同意中间方案 → G4
    # TR=1: maj=0 16条消息详细讨论后折中于 P3 方案 → G2
    G[12] = {0: 4, 1: 2}

    # Group 13
    # TR=0: maj=0 快速一致同意 P2（6条）; maj=1 已有多数，快速一致 → G4
    # TR=1: P3(obs7t4q0) 坚决反对等待（"im not gonna wait 4 weeks"），
    #        P2 表示不关心，P1 随便 → G3（P3 驱动）
    G[13] = {0: 4, 1: 3}

    # Group 14
    # TR=0: maj=0 折中于 P1（中间方案）; maj=1 详细辩论（21条）后折中 → G2
    # TR=1: maj=0 最终一致同意 P2（"I honestly dont really care" → 快速一致） → G4
    G[14] = {0: 2, 1: 4}

    # Group 15
    # TR=0: maj=0 快速一致同意 P2（6条）; maj=1 仅2条消息即同意 → G4
    # TR=1: P1+P3 协商折中于选项9（中间方案） → G2
    G[15] = {0: 4, 1: 2}

    # Group 16
    # TR=0: 风险偏好者 vs 风险厌恶者的长时间讨论（18条），最终折中 → G2
    # TR=1: maj=0 快速一致（2条）; maj=1 P3 适应 P1 → G4
    G[16] = {0: 2, 1: 4}

    # Group 17
    # TR=0: maj=0 1条消息建议中间方案; maj=1 激烈辩论后多数投票 2v1 → G1
    # TR=1: maj=0 快速一致同意 P2/P3; maj=1 快速一致同意 P1 → G4
    G[17] = {0: 1, 1: 4}

    # Group 18
    # TR=0: P2 主导主张较少风险，P1 同意，P3 未参与对话 → G3
    # TR=1: maj=0 详细讨论后达成折中（"90 percent its the middle"） → G2
    G[18] = {0: 3, 1: 2}

    # Group 19
    # TR=0: maj=0 快速一致同意冒险（3人均同意）; maj=1 P1 数学论证主导 → G3
    # TR=1: maj=0 一致同意 P2; maj=1 P1 主导选择中间方案 → G3
    G[19] = {0: 3, 1: 3}

    # Group 20
    # TR=0: 折中于 70%（"shifting to one above"） → G2
    # TR=1: 一致同意/民主投票（"democracy"） → G4
    G[20] = {0: 2, 1: 4}

    # Group 21
    # TR=0: P2+P3 立场相同（67%权重），P1 适配 → G1
    # TR=1: 快速一致同意折中方案 → G4
    G[21] = {0: 1, 1: 4}

    # Group 22
    # TR=0: maj=0 长时间辩论（27条），最终折中于"first 4 A then B" → G2
    # TR=1: P3 主导决策，P1 同意（仅2条消息） → G3
    G[22] = {0: 2, 1: 3}

    # Group 23
    # TR=0: maj=0 快速一致同意方案2; maj=1 P1+P2 各持己见，P3 未参与 → G3
    # TR=1: 快速一致同意方案3 → G4
    G[23] = {0: 3, 1: 4}

    # Group 24
    # TR=0: maj=0 折中于 "A until 6 and B from 7"; maj=1 讨论后折中 → G2
    # TR=1: 快速一致同意 P2（5条消息协商后同意） → G4
    G[24] = {0: 2, 1: 4}

    # Group 25
    # TR=0: 两人对话（P2 缺席），无实质性协商（"do what you think it's best"） → G4
    # TR=1: 无数据
    G[25] = {0: 4, 1: None}

    # Group 26
    # TR=0: 快速一致同意最大化收益（6条） → G4
    # TR=1: 无数据
    G[26] = {0: 4, 1: None}

    # Group 27
    # TR=0: 协商后折中于 60-70% 阈值 → G2
    # TR=1: 无数据
    G[27] = {0: 2, 1: None}

    # Group 28
    # TR=0: P2(1eicckha) 要求 P1 降低风险（"50/50 is too high a risk...so you should
    #        lower the risk"），P1 被要求适应 → G1
    # TR=1: 无数据
    G[28] = {0: 1, 1: None}

    return G


# =============================================================================
# 2. Individual 层面分类 (I1-I7)
# =============================================================================
# 分类依据：逐条分析每个参与者在对话中的发言内容和角色。
#
# 判断标准：
#   I1 (冷漠): 不积极参与，表示"不关心"、"随便"、"fine with anything"
#   I2 (愿意适应): 明确表示同意他人立场，或从自己立场转向他人立场
#   I3 (要求他人适应): 主动提出方案并要求他人采纳，或主导讨论方向
#   I4 (要求更多风险/延迟): 明确推动风险更高/等待更久的选项
#   I5 (接受风险/延迟要求): 被说服后接受他人的风险/延迟要求
#   I6 (要求更少延迟风险): 明确推动风险更低/等待更短的选项
#   I7 (接受更多延迟风险): 接受他人提出的更多延迟风险要求

def build_individual_classification():
    """
    返回字典: I[participant_code][time_risk] = 分类值 (1-7)

    基于对所有会话的逐条内容分析。按会话组织。
    """
    I = {}

    # ========================
    # session: bbgfffw6 (majority=0)
    # ========================

    # Group 1 (TR=0): P1 leads with math, P2&P3 adapt
    I['ncmbeu96'] = {0: 3, 1: 3}    # TR0: 用数学论证主导; TR1: 同样用数学论证主导
    I['w925dou6'] = {0: 2, 1: 2}    # TR0: 最初犹豫后适应P1; TR1: 适应方案2
    I['6ogvjie9'] = {0: 2, 1: 3}    # TR0: 适应P1; TR1: 主动提议方案2

    # Group 2 (TR=0): P1 holds firm, P3 flip-flops, P2 mostly absent
    I['rx0314r2'] = {0: 2, 1: 2}    # TR0: 最初反对后转为同意; TR1: 快速同意
    I['hj311cpt'] = {0: 3, 1: 3}    # TR0: 推动自己立场; TR1: 建议中间方案
    I['qirxmn9p'] = {0: 3, 1: 2}    # TR0: 先是要求他人适应，后自己适应; TR1: 同意他人

    # Group 3 (TR=0): quick agreement
    I['4t7f8z8s'] = {0: 2, 1: 2}    # TR0: 同意方案2; TR1(G4): 适应
    I['7g3hzz4a'] = {0: 3, 1: 2}    # TR0: 推动立场; TR1: 表示都可以
    I['yj9as5vl'] = {0: 2, 1: 3}    # TR0: 提议方案2; TR1: 推动立场
    I['tiakgq4z'] = {0: 4, 1: None} # TR0: 想赌博冒险 ("I'd risk it")
    I['hoxtva6l'] = {0: 2, 1: None} # TR0: 质疑后同意
    I['mfodxdqr'] = {0: 2, 1: None} # TR0: 同意他人方案

    # Group 4 / Group 5 (参与者跨组)
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
    I['b1ljp7hw'] = {0: None, 1: 3}  # TR1: 推动风险立场
    I['n6gyc5p4'] = {0: None, 1: 4}  # TR1: 要求更多风险 (B at 8,9,10)
    I['epbcekix'] = {0: None, 1: 6}  # TR1: 不愿等待，最终适应

    # Group 3
    I['ehz7bo8w'] = {0: 2, 1: 2}    # TR0: 同意; TR1: 适应
    I['wbyf9v3z'] = {0: 2, 1: 6}    # TR0: 同意; TR1: 要求更少延迟
    I['h711c9j8'] = {0: 2, 1: 3}    # TR0: 同意; TR1: 质疑并主导讨论

    # ========================
    # session: nzsz5b21 (majority=1, TR=0 only)
    # ========================
    I['tz13p6oq'] = {0: 2, 1: None}  # 跟随趋势 ("I'll follow trend")
    I['rh2p1guk'] = {0: 2, 1: None}  # 愿意适应 ("If we cannot decide, I can also go for 3")
    I['5tju8bwm'] = {0: 3, 1: None}  # 推动选择
    I['wntam0iz'] = {0: 6, 1: None}  # 不愿等待 ("i dont want to wait 4 weeks")

    # ========================
    # session: f8edwq9b (majority=1)
    # ========================

    # Group 4/6
    I['qsx3cu9b'] = {0: 3, 1: 3}    # TR0(G6): 主导讨论; TR1(G4): 主导
    I['ne9tcre6'] = {0: 3, 1: 2}    # TR0(G6): 提供数学论证; TR1(G4): 同意
    I['hvrtd05u'] = {0: 2, 1: 2}    # TR0(G6): 附和; TR1(G4): 附和

    # Group 5/7
    I['dn7y6gxh'] = {0: 3, 1: 3}    # TR0(G7): 主导讨论; TR1(G5): 主导，质疑冒险
    I['ads1z9m5'] = {0: 2, 1: 6}    # TR0(G7): 同意; TR1(G5): 更少等待偏好
    I['g4fja7tj'] = {0: 4, 1: 4}    # TR0(G7): 追求风险; TR1(G5): 追求风险

    # Group 6/8
    I['890ews6l'] = {0: 3, 1: 4}    # TR0(G8): 挑战他人立场; TR1(G6): 推动等待/风险
    I['zlh5tdu5'] = {0: 3, 1: 2}    # TR0(G8): 推动自己方案; TR1(G6): 最终适应

    # Group 7/9
    I['4ecrweb0'] = {0: 3, 1: 3}    # TR0(G9): 提议中间方案; TR1(G7): 主导提议
    I['0vm3ban9'] = {0: 2, 1: 3}    # TR0(G9): 同意; TR1(G7): 首先提议
    I['j1umjk3z'] = {0: 2, 1: 2}    # TR0(G9): 同意; TR1(G7): 同意

    # Group 8/10
    I['671jyleo'] = {0: 3, 1: 1}    # TR0(G10): 主导评论; TR1(G8): 离题，低参与
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
    I['lf6j1q36'] = {0: 1, 1: 1}    # TR0: 犹豫不决; TR1: 犹豫不决 → 冷漠

    # Group 9
    I['9hydcim4'] = {0: 3, 1: None}  # TR0: 推动更多风险 ("we should take 60%")
    I['7u8nblcm'] = {0: 2, 1: None}  # TR0: 同意折中
    I['rkkv0lh9'] = {0: 2, 1: None}  # TR0: 适应折中

    # Group 9/10 (TR=1)
    I['8qn9nh3b'] = {0: 2, 1: 6}    # TR0(G10): 适应; TR1(G9): 不愿等4周
    I['hwcutjyi'] = {0: 3, 1: 2}    # TR0(G10): 推动立场; TR1(G9): 配合
    I['wca7iev8'] = {0: 3, 1: 3}    # TR0(G10): 主导提议; TR1(G9): 提议选项

    # Group 10/11
    I['4vn5iz9u'] = {0: 3, 1: 2}    # TR0(G11): 推动50%立场; TR1(G10): 适应
    I['vycv5y5a'] = {0: 3, 1: 3}    # TR0(G11): 主导折中 ("meet in the middle at 60%"); TR1(G10): 提议折中

    # Group 11
    I['nrxq26t9'] = {0: 2, 1: None}  # TR0: 适应折中

    # Group 12
    I['9o5z6npd'] = {0: 3, 1: None}  # TR0: 推动保守选择
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
    I['mldp6kdi'] = {0: 3, 1: 1}    # TR0(G12): 提议投票; TR1(G10): 低参与
    I['uxkihpwg'] = {0: 2, 1: 3}    # TR0(G12): 同意; TR1(G10): 提议中间方案

    # Group 12
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
    I['3z868bro'] = {0: 2, 1: 6}    # TR0(G13): 表示无所谓; TR1(G12): 坚决反对等待

    # Group 13/14
    I['bvph8u1v'] = {0: 3, 1: 1}    # TR0(G14): 主导提议; TR1(G13): 冷漠 ("whatever")
    I['obs7t4q0'] = {0: 2, 1: 6}    # TR0(G14): 适应; TR1(G13): 坚决反对等待
    I['zvmba2hz'] = {0: 3, 1: 4}    # TR0(G14): 提议中间方案; TR1(G13): 愿意等待

    # ========================
    # session: thex540s
    # ========================

    # Group 13/11
    I['gbqvph97'] = {0: 3, 1: 6}    # TR0(G13): 指出已有多数; TR1(G11): 无法到场，反对延迟
    I['gpfru5fz'] = {0: 2, 1: 3}    # TR0(G13): 同意; TR1(G11): 主导讨论
    I['2m2gvym1'] = {0: 2, 1: 2}    # TR0(G13): 同意; TR1(G11): 适应

    # Group 14
    I['muwupzmk'] = {0: 3, 1: None}  # TR0: 主导提议，推动降低风险起点
    I['elvh3j0w'] = {0: 2, 1: None}  # TR0: 推动风险但最终同意折中
    I['48mnzzpe'] = {0: 2, 1: None}  # TR0: 被说服适应

    # ========================
    # session: moe0awio
    # ========================

    # Group 14/17
    I['5m6eokuf'] = {0: 4, 1: 4}    # TR0(G17): 追求高风险 ("go big or go home"); TR1(G14): 追求高风险
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
    I['tyxazhzc'] = {0: 2, 1: 1}    # TR0(G15): 同意; TR1(G14): 不在乎 ("don't really care")
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
    I['ogjqbbqv'] = {0: 3, 1: 2}    # TR0(G18): 主导主张较少风险; TR1(G16): 提议方案1
    I['bin13zaw'] = {0: 3, 1: 2}    # TR0(G18): 论证风险中性; TR1(G16): 同意方案1

    # Group 17/19
    I['t2m5a7ev'] = {0: 3, 1: 3}    # TR0(G19): 主导提议冒险; TR1(G17): 主导提议
    I['j4lmty8b'] = {0: 2, 1: 6}    # TR0(G19): 同意; TR1(G17): 不愿等4周
    I['38cndqe5'] = {0: 2, 1: 2}    # TR0(G19): 同意; TR1(G17): 同意

    # ========================
    # session: noias7kj
    # ========================

    # Group 15/18
    I['ho43nz77'] = {0: 2, 1: 2}    # TR0(G18): 同意; TR1(G15): 同意
    I['jqul0rpn'] = {0: 3, 1: 6}    # TR0(G18): 解释立场; TR1(G15): 觉得4周太长
    I['f5fsh83e'] = {0: 1, 1: 3}    # TR0(G18): 不在乎; TR1(G15): 推动快速决策

    # Group 16/19
    I['l2x4f2m5'] = {0: 3, 1: None}  # TR0(G19): 要求P1适应
    I['rhhck5ce'] = {0: 3, 1: 6}    # TR0(G19): 数学论证; TR1(G16): 无法到场（反对延迟）
    I['b4scyfme'] = {0: 2, 1: 5}    # TR0(G19): 质疑后同意; TR1(G16): 接受不延迟要求

    # ========================
    # session: c29h9lab
    # ========================

    # Group 18/20
    I['txkohpoy'] = {0: 2, 1: 2}    # TR0(G20): 同意; TR1(G18): 同意
    I['ntpj6k3y'] = {0: 3, 1: 1}    # TR0(G20): 主导提议; TR1(G18): 不在乎
    I['va4iv92o'] = {0: 2, 1: 6}    # TR0(G20): 同意; TR1(G18): 偏向更早拿钱

    # Group 19/21
    I['3ykoed4m'] = {0: 3, 1: 2}    # TR0(G21): 主导; TR1(G19): 同意
    I['mvlrigx2'] = {0: 2, 1: 3}    # TR0(G21): 适应; TR1(G19): 主导

    # Group 20/22
    I['2yaken99'] = {0: 3, 1: 1}    # TR0(G22): 推动冒险; TR1(G20): 不在乎 ("okay with whatever")
    I['rzjg5ms6'] = {0: 2, 1: 1}    # TR0(G22): 适应折中; TR1(G20): 开玩笑，不在乎
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
    I['g1tvlvk8'] = {0: 2, 1: 6}    # TR0(G22): 同意; TR1(G19): 不愿冒险+等待
    I['nv74wiwy'] = {0: 2, 1: 4}    # TR0(G22): 同意; TR1(G19): 要求50-50冒险
    I['6nm4aea5'] = {0: 3, 1: 2}    # TR0(G22): 发起变更; TR1(G19): 提问后同意

    # ========================
    # session: y1hj2aj2
    # ========================

    # Group 17/20
    I['nfy1ut59'] = {0: 3, 1: 3}    # TR0(G20): 推动风险中性; TR1(G17): 推动风险
    I['hqox7ku0'] = {0: 6, 1: 2}    # TR0(G20): 厌恶损失; TR1(G17): 适应
    I['ryn74uw6'] = {0: 2, 1: 2}    # TR0(G20): 同意; TR1(G17): 同意

    # ========================
    # session: zspnbitg
    # ========================

    # Group 20/24
    I['04ybbykm'] = {0: 3, 1: 6}    # TR0(G24): 解释，主导; TR1(G20): 想明天拿钱
    I['gol08cao'] = {0: 3, 1: 2}    # TR0(G24): 提议; TR1(G20): 适应
    I['qht1ncs7'] = {0: 2, 1: 3}    # TR0(G24): 适应; TR1(G20): 主导提议

    # Group 23
    I['wdyjnja3'] = {0: 3, 1: None}  # TR0: 提议 ("A until 7")
    I['mnorf4z6'] = {0: 6, 1: None}  # TR0: 主张保守 ("Safe and sure")

    # ========================
    # session: 1gzf7p6u
    # ========================

    # Group 21/23
    I['fe11vpqw'] = {0: 3, 1: 3}    # TR0(G23): 主导; TR1(G21): 提议折中
    I['bw3qty6c'] = {0: 2, 1: 2}    # TR0(G23): 同意; TR1(G21): 同意
    I['lxyawqvz'] = {0: 2, 1: None}  # TR0(G23): 同意

    # ========================
    # session: ymgl8k4i (TR=0 and TR=1)
    # ========================

    # Group 22/26
    I['dufx3vxe'] = {0: 3, 1: 3}    # TR0(G26): 主导最大化收益; TR1(G22): 主导
    I['ee6sjzk2'] = {0: 2, 1: 2}    # TR0(G26): 同意; TR1(G22): 同意

    # Group 23/27
    I['cbe3hywl'] = {0: 6, 1: 6}    # TR0(G27): 要求更低风险; TR1(G23): 要求更少延迟风险
    I['gr8r5tzp'] = {0: 3, 1: 3}    # TR0(G27): 主导提议; TR1(G23): 主导
    I['f5g4wfzh'] = {0: 2, 1: 2}    # TR0(G27): 同意; TR1(G23): 同意

    # Group 24
    I['h9pn79r3'] = {0: None, 1: 3}  # TR1: 推动立场
    I['z6l5xogp'] = {0: None, 1: 2}  # TR1: 适应

    # Group 25 (TR=0 only)
    I['qr344o7n'] = {0: 2, 1: None}  # 同意他人
    I['2ye352y6'] = {0: 1, 1: None}  # "do what you think it's best" → 冷漠

    # Group 26 (TR=0 only)
    I['o2huph9r'] = {0: 2, 1: None}  # 同意

    # Group 28 (TR=0 only)
    I['1eicckha'] = {0: 3, 1: None}  # 要求P1降低风险

    # ========================
    # session: vfgv3mdk (TR=1 only)
    # ========================
    I['19cpp9r7'] = {0: None, 1: 6}  # 坚决不等待 ("In 4 weeks ill forget")
    I['9ms0nc71'] = {0: None, 1: 5}  # 接受不等待要求
    I['fk67q6oc'] = {0: None, 1: 5}  # 接受不等待要求

    # ========================
    # session: tx1s5v14 (TR=0 only)
    # ========================
    I['qx3jcxwr'] = {0: 3, 1: None}  # 提议折中
    I['kmh1o20i'] = {0: 2, 1: None}  # 同意
    I['9uwjw5gr'] = {0: 2, 1: None}  # 同意

    return I


# =============================================================================
# 3. 分类应用与结果输出
# =============================================================================

def apply_classifications():
    """
    主函数：加载数据 → 构建分类 → 映射到 dataset2026 → 输出
    """
    print("=" * 60)
    print("集体决策对话分类程序")
    print("=" * 60)

    # ----------------------------
    # 3.1 加载数据
    # ----------------------------
    print("\n[1/5] 加载数据...")
    msg = pd.read_excel(MESSAGE_FILE)
    ds  = pd.read_excel(DATASET_FILE)
    print(f"  消息数据: {msg.shape[0]} 条消息, {msg['participant_code'].nunique()} 个参与者")
    print(f"  数据集:   {ds.shape[0]} 行, {ds['subject_code'].nunique()} 个被试")

    # ----------------------------
    # 3.2 构建分类字典
    # ----------------------------
    print("\n[2/5] 构建分类体系...")
    G = build_group_classification()
    I = build_individual_classification()

    # 统计
    n_groups_tr0 = sum(1 for g in G if G[g].get(0) is not None)
    n_groups_tr1 = sum(1 for g in G if G[g].get(1) is not None)
    n_indiv_tr0  = sum(1 for pc in I if I[pc].get(0) is not None)
    n_indiv_tr1  = sum(1 for pc in I if I[pc].get(1) is not None)
    print(f"  Group 分类:  {n_groups_tr0} 组 (TR=0), {n_groups_tr1} 组 (TR=1)")
    print(f"  个体分类:    {n_indiv_tr0} 人 (TR=0), {n_indiv_tr1} 人 (TR=1)")

    # ----------------------------
    # 3.3 构建时间风险特定的映射桥接
    # ----------------------------
    # 关键：同一参与者在不同 time_risk 下可能属于不同的 msg_group
    # 因此分别构建 TR=0 和 TR=1 的映射
    print("\n[3/5] 构建映射桥接...")

    msg_tr0 = msg[msg['time_risk'] == 0]
    msg_tr1 = msg[msg['time_risk'] == 1]

    bridge_tr0 = msg_tr0.groupby(['participant_code', 'session_code'])['group'] \
                        .first().reset_index()
    bridge_tr0.columns = ['participant_code', 'session_code', 'msg_group_tr0']

    bridge_tr1 = msg_tr1.groupby(['participant_code', 'session_code'])['group'] \
                        .first().reset_index()
    bridge_tr1.columns = ['participant_code', 'session_code', 'msg_group_tr1']

    # 合并到 dataset2026
    ds = ds.merge(
        bridge_tr0,
        left_on=['subject_code', 'session_code'],
        right_on=['participant_code', 'session_code'],
        how='left'
    )
    ds = ds.merge(
        bridge_tr1,
        left_on=['subject_code', 'session_code'],
        right_on=['participant_code', 'session_code'],
        how='left',
        suffixes=('', '_tr1')
    )

    n_tr0 = ds['msg_group_tr0'].notna().sum()
    n_tr1 = ds['msg_group_tr1'].notna().sum()
    print(f"  TR=0 匹配: {n_tr0} / {len(ds)} 人")
    print(f"  TR=1 匹配: {n_tr1} / {len(ds)} 人")

    # ----------------------------
    # 3.4 应用分类
    # ----------------------------
    print("\n[4/5] 应用分类...")

    # Group 分类
    group_tr0_map = {g: G[g][0] for g in G if G[g].get(0) is not None}
    group_tr1_map = {g: G[g][1] for g in G if G[g].get(1) is not None}

    ds['group_categories1'] = ds['msg_group_tr0'].map(group_tr0_map)
    ds['group_categories2'] = ds['msg_group_tr1'].map(group_tr1_map)

    # Individual 分类
    indiv_tr0_map = {pc: I[pc][0] for pc in I if I[pc].get(0) is not None}
    indiv_tr1_map = {pc: I[pc][1] for pc in I if I[pc].get(1) is not None}

    ds['individual_categories1'] = ds['subject_code'].map(indiv_tr0_map)
    ds['individual_categories2'] = ds['subject_code'].map(indiv_tr1_map)

    # ----------------------------
    # 3.5 清理并输出
    # ----------------------------
    print("\n[5/5] 清理并输出...")

    # 删除临时列
    cols_to_drop = ['msg_group_tr0', 'msg_group_tr1',
                    'participant_code', 'participant_code_tr1']
    for c in cols_to_drop:
        if c in ds.columns:
            ds = ds.drop(columns=[c])

    # 保存
    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"  结果已保存至: {OUTPUT_FILE}")
    print(f"  输出维度: {ds.shape}")

    # ----------------------------
    # 输出统计摘要
    # ----------------------------
    print("\n" + "=" * 60)
    print("分类结果摘要")
    print("=" * 60)

    print("\n--- Group 分类 (G1-G4) ---")
    for col, label in [('group_categories1', 'TR=0 (纯风险)'),
                       ('group_categories2', 'TR=1 (延迟风险)')]:
        vc = ds[col].value_counts().sort_index()
        total = ds[col].notna().sum()
        print(f"\n{label} (n={total}):")
        for val, count in vc.items():
            names = {1: 'G1-多数原则', 2: 'G2-折中', 3: 'G3-少数驱动', 4: 'G4-一致同意'}
            print(f"  {names.get(int(val), val)}: {count} ({count/total*100:.1f}%)")

    print("\n--- Individual 分类 (I1-I7) ---")
    for col, label in [('individual_categories1', 'TR=0 (纯风险)'),
                       ('individual_categories2', 'TR=1 (延迟风险)')]:
        vc = ds[col].value_counts().sort_index()
        total = ds[col].notna().sum()
        print(f"\n{label} (n={total}):")
        names = {1: 'I1-冷漠', 2: 'I2-愿意适应', 3: 'I3-要求他人适应',
                 4: 'I4-要求更多风险/延迟', 5: 'I5-接受风险/延迟要求',
                 6: 'I6-要求更少延迟风险', 7: 'I7-接受更多延迟风险'}
        for val, count in vc.items():
            print(f"  {names.get(int(val), val)}: {count} ({count/total*100:.1f}%)")

    # 交叉表
    print("\n--- Group × Individual 交叉表 (TR=0) ---")
    ct = pd.crosstab(ds['group_categories1'], ds['individual_categories1'],
                     dropna=False, margins=True)
    print(ct.to_string())

    print("\n--- Group × Individual 交叉表 (TR=1) ---")
    ct = pd.crosstab(ds['group_categories2'], ds['individual_categories2'],
                     dropna=False, margins=True)
    print(ct.to_string())

    # 缺失值报告
    missing_both = ds['group_categories1'].isna() & ds['group_categories2'].isna()
    print(f"\n--- 缺失值报告 ---")
    print(f"  完全无对话数据的被试: {missing_both.sum()} 人")
    print(f"  仅有 TR=0 数据: {(ds['group_categories1'].notna() & ds['group_categories2'].isna()).sum()} 人")
    print(f"  仅有 TR=1 数据: {(ds['group_categories1'].isna() & ds['group_categories2'].notna()).sum()} 人")

    return ds


# =============================================================================
# 4. 程序入口
# =============================================================================

if __name__ == '__main__':
    ds = apply_classifications()
    print("\n程序执行完毕。")
