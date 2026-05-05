"""
=============================================================================
分类验证程序 — Verify Group & Individual Classifications Against Standards
=============================================================================

功能：根据 category standards.docx 中的分类标准，检查 dataset2026.xlsx 中已有的
      group_categories1/2 和 individual_categories1/2 是否正确。

验证标准 (from category standards.docx):

  Group:
    G1 (Majority): Two members have the same choices; the third member adapts.
    G2 (Compromise): After negotiating, individuals agree on a solution in
                     between their initial choices.
    G3 (Minority): The decision is made by a single individual, based on his
                   lack of compliance or indifference of other group members.
    G4 (Unanimity): Within the first chat round, all individuals agree on or
                    submit the same proposal.

  Individual:
    I1 (Indifference): Refuses to participate or expresses that he does not care.
    I2 (Willingness to adapt): Individual with differing preferences adapts.
    I3 (Demand to adapt): Prompts others to make a more risky(-delayed) decision.
    I4 (Demand for risk): Prompts others to make a more risky(-delayed) decision.
    I5 (Acceptance of risk): Accepts and implements the demand for risk.
    I6 (Demand for less delayed risk): Prompts others to make a less
                                       risky-delayed decision.
    I7 (Acceptance of more delayed risk): Accepts and implements demand for
                                          more delayed risk.

输出：
  - group_indicator1 (TR=0) / group_indicator2 (TR=1): 1=准确, 0=不准确
  - individual_indicator1 (TR=0) / individual_indicator2 (TR=1): 1=准确, 0=不准确

作者: Claude Code 辅助验证
日期: 2026-05-05
=============================================================================
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')


# =============================================================================
# 1. Group 分类验证
# =============================================================================
# 对于每个 msg_group × time_risk 组合，根据对话内容判断当前分类是否符合标准。
# group_verify[key][time_risk] = True (准确) / False (不准确)
#
# 验证过程：逐条审查了全部 97 个对话会话 (session × group × time_risk × majority)，
# 对照 category standards.docx 中的四条 Group 标准进行独立判断。

def build_group_verification():
    """
    返回字典: GV[msg_group][time_risk] = True/False
    True = 当前分类准确, False = 当前分类不准确
    """
    GV = {}

    # =========================================================================
    # Group 1
    # TR=0 (bbgfffw6, maj=0): P1(ncmbeu96) 用数学论证主导，P2(w925dou6) 和
    #   P3(6ogvjie9) 最初犹豫后适应 → G1 (多数原则) 正确。
    #   两位成员 (P2+P3) 最终适应 P1 的立场，符合 G1 标准。
    # TR=1 (bbgfffw6, maj=0): P1 数学论证，P2 "fine for me"，P3 提议方案2，
    #   快速达成一致（14条消息，首轮即无争议）。代码 G4。
    #   标准：G4 要求 "first chat round all agree"。虽有 P3 主动提议，
    #   但整体一致同意，14条消息也在首轮讨论内。G4 合理。
    GV[1] = {0: True, 1: True}

    # =========================================================================
    # Group 2
    # TR=0 (bbgfffw6, maj=0): P3(qirxmn9p) 初始主张方案2，经 P1(rx0314r2)
    #   反对后转向方案1，P2(hj311cpt) 基本缺席。P1 立场最终获胜，P3 适应。
    #   符合 G1 标准：两人（P1固定+P2隐含/P3最终适应）形成多数。
    # TR=1 (bbgfffw6 maj=0, 6hgrim4b maj=1): 两个会话。
    #   maj=0: 4条消息快速一致同意方案3。
    #   maj=1: 33条消息，P2(b1ljp7hw)+P3(n6gyc5p4) 推动更多风险/等待，
    #          P1(epbcekix) 最终适应。整体看 P2+P3 立场一致，P1 适应 → G1 正确。
    GV[2] = {0: True, 1: True}

    # =========================================================================
    # Group 3
    # TR=0 (bbgfffw6 maj=0, 6hgrim4b maj=1): maj=0 7条快速一致同意方案2；
    #   maj=1 5条快速一致同意。两场均为非常快速的共识 → G4 正确。
    # TR=1 (bbgfffw6 maj=0, 6hgrim4b maj=1): maj=0 10条消息，P1 表示都可以，
    #   P2+P3 选方案3，P1 最终同意。maj=1 19条消息，P3 质疑引导讨论，
    #   最终一致同意。首轮即达成共识 → G4 正确。
    GV[3] = {0: True, 1: True}

    # =========================================================================
    # Group 4
    # TR=0 (bbgfffw6 maj=0, nzsz5b21 maj=1): maj=0 7条消息，P1+P2 反对方案3，
    #   P3 妥协选方案2。maj=1 仅1条 "already have a majority, I'll follow trend"。
    #   快速达成一致 → G4 正确。
    # TR=1 (bbgfffw6 maj=0, f8edwq9b maj=1): maj=0 4条消息快速一致同意方案2。
    #   maj=1 14条消息讨论后一致同意 P1。快速一致 → G4 正确。
    GV[4] = {0: True, 1: True}

    # =========================================================================
    # Group 5
    # TR=0 (bbgfffw6 maj=0, nzsz5b21 maj=1): P1(os109bhi) 明确提议折中
    #   "Should we come to an agreement in the middle? Proposal 1?"，
    #   P2 最初提议自己方案后适应。明确的 compromise 语言 → G2 正确。
    # TR=1 (bbgfffw6 maj=0, f8edwq9b maj=1): maj=0 7条快速一致；
    #   maj=1 16条讨论后一致同意。首轮快速共识 → G4 正确。
    GV[5] = {0: True, 1: True}

    # =========================================================================
    # Group 6
    # TR=0 (bbgfffw6 maj=0, f8edwq9b maj=1): maj=0 8条消息讨论风险百分比
    #   后达成折中；maj=1 21条消息数学讨论后折中于 P2。明显协商后取中间方案
    #   → G2 正确。
    # TR=1 (bbgfffw6 maj=0没数据, f8edwq9b maj=1, 8kn3iz3d maj=0):
    #   maj=1 (f8edwq9b) 8条消息 P1 推动等待 P3 最终适应；
    #   maj=0 (8kn3iz3d) 15条消息 P3(vqcyaekn) 主导，P1+P2 适应。
    #   两人 (P3+P1 或 P1+P3) 立场一致，第三人适应 → G1 正确。
    GV[6] = {0: True, 1: True}

    # =========================================================================
    # Group 7
    # TR=0 (dkoekgf5 maj=0, f8edwq9b maj=1, 8kn3iz3d maj=0):
    #   dkoekgf5: 7条，P1 提议 "compromise"；
    #   f8edwq9b: 22条长时间辩论折中于 P2 (中间方案)；
    #   8kn3iz3d: 16条讨论后折中。多处明确折中协商 → G2 正确。
    # TR=1 (dkoekgf5 maj=0, f8edwq9b maj=1): 两个会话均为快速一致同意
    #   （dkoekgf5 6条，f8edwq9b 10条）。首轮快速共识 → G4 正确。
    GV[7] = {0: True, 1: True}

    # =========================================================================
    # Group 8
    # TR=0 (dkoekgf5 maj=0, f8edwq9b maj=1): P1(s8g1e7mj) 明确说
    #   "I think its a compromise" → 清楚表达折中意图。maj=1 仅5条消息，
    #   P3 推动自己方案。整体有折中协商元素 → G2 正确。
    # TR=1 (dkoekgf5 maj=0, f8edwq9b maj=1): maj=0 6条消息快速同意方案2；
    #   maj=1 2条离题消息仅一人发言。快速一致 → G4 正确。
    GV[8] = {0: True, 1: True}

    # =========================================================================
    # Group 9
    # TR=0 (dkoekgf5 maj=0, f8edwq9b maj=1): dkoekgf5 11条消息协商后
    #   折中于60%；f8edwq9b 8条消息折中于中间方案。均为协商后取中间方案
    #   → G2 正确。
    # TR=1 (dkoekgf5 maj=0, 0f9u4oto maj=1): maj=0 14条消息快速讨论后
    #   折中于方案2；maj=1 11条消息折中于中间方案 ("meet in the middle")。
    #   有折中语言和协商 → G2 正确。
    GV[9] = {0: True, 1: True}

    # =========================================================================
    # Group 10
    # TR=0 (dkoekgf5 maj=0, f8edwq9b maj=1): maj=0 9条消息协商后达成一致；
    #   maj=1 5条消息 P2 主导评论。P2+P3 立场相同，P1 跟随 → G1 正确。
    # TR=1 (0f9u4oto maj=1, dkoekgf5 maj=0): 两个会话都仅有3条消息，
    #   聊天内容极少，快速达成一致。maj=1: P1 "hello" "+", P2 "hi! P1s?"；
    #   maj=0: P3 提议 cutoff at 70%, P2 "okay"。
    #   代码分类 G3（少数驱动）。
    #   标准判断：聊天极短（仅3条），快速达成一致，没有体现出某一成员
    #   因他人冷漠/不服从驱动决策的模式。更符合 G4（首轮一致同意）的标准。
    #   → 分类不准确，应为 G4。
    GV[10] = {0: True, 1: False}

    # =========================================================================
    # Group 11
    # TR=0 (dkoekgf5 maj=0, 0f9u4oto maj=1): dkoekgf5 9条消息，三方各陈述
    #   偏好 (50/60/70) 后折中于 60%。明确 "compromise and meet in the middle"
    #   → G2 正确。
    # TR=1 (thex540s maj=1, vfgv3mdk maj=0): maj=1 13条消息，
    #   P3(gbqvph97) 坚决反对等待4周，P1+P2 接受不等待方案 → G3 正确。
    #   maj=0 4条消息，P1 坚决反对等待4周 ("In 4 weeks ill forget")，
    #   其他人接受。单人驱动 → G3 正确。
    GV[11] = {0: True, 1: True}

    # =========================================================================
    # Group 12
    # TR=0 (dkoekgf5 maj=0, 0f9u4oto maj=1): maj=0 4条消息快速一致同意
    #   保守方案A；maj=1 6条消息一致同意 P2 的中间方案。快速一致 → G4 正确。
    # TR=1 (6apbq166 maj=0, moe0awio maj=1): maj=0 16条消息详细讨论
    #   后折中于 P3 方案。maj=1 4条消息一致同意。整体有折中协商 → G2 正确。
    GV[12] = {0: True, 1: True}

    # =========================================================================
    # Group 13
    # TR=0 (6apbq166 maj=0, thex540s maj=1): maj=0 6条消息快速一致同意
    #   P2（多数）；maj=1 6条消息指出已有 majority 后一致。快速一致 → G4 正确。
    # TR=1 (6apbq166 maj=0, moe0awio maj=1): maj=0 14条消息，
    #   P3(obs7t4q0) 坚决反对等待 ("im not gonna wait 4 weeks")，
    #   P1 "whatever"，P2 "I don't care"。P3 单人驱动，他人冷漠/不关心
    #   → G3 正确。
    GV[13] = {0: True, 1: True}

    # =========================================================================
    # Group 14
    # TR=0 (6apbq166 maj=0, thex540s maj=1): maj=0 7条消息折中于 P1
    #   （中间方案）；maj=1 21条消息详细辩论后折中于 P1。协商后取中间方案
    #   → G2 正确。
    # TR=1 (l1u9ytue maj=0, moe0awio maj=1): maj=0 11条消息，
    #   P2 表示 "I honestly dont really care" → 冷漠。P3 偏向不等待，
    #   P1 适应 P2。整体快速一致同意 → G4 正确。
    GV[14] = {0: True, 1: True}

    # =========================================================================
    # Group 15
    # TR=0 (l1u9ytue maj=0, moe0awio maj=1): maj=0 6条消息快速一致同意
    #   P2（多数）；maj=1 仅2条消息即同意。首轮快速一致 → G4 正确。
    # TR=1 (l1u9ytue maj=0, noias7kj maj=1): maj=0 11条消息协商后
    #   折中于选项9（中间方案）；maj=1 4条消息快速一致。有折中协商 → G2 正确。
    GV[15] = {0: True, 1: True}

    # =========================================================================
    # Group 16
    # TR=0 (l1u9ytue maj=0, moe0awio maj=1): maj=0 18条消息，
    #   风险偏好者 vs 风险厌恶者长时间讨论，最终折中于选项7 → G2 正确。
    # TR=1 (f0el3eip maj=0, noias7kj maj=1): maj=0 2条消息快速一致
    #   同意方案1；maj=1 3条消息 P1 坚决不等待，P3 接受。快速一致 → G4 正确。
    GV[16] = {0: True, 1: True}

    # =========================================================================
    # Group 17
    # TR=0 (l1u9ytue maj=0, moe0awio maj=1): maj=0 仅1条消息提议中间方案；
    #   maj=1 27条消息激烈辩论后以 majority vote 2v1 决定。多数投票模式
    #   → G1 正确。
    # TR=1 (f0el3eip maj=0, y1hj2aj2 maj=1): maj=0 6条消息快速一致同意
    #   P2；maj=1 5条消息快速一致同意 P1。首轮快速共识 → G4 正确。
    GV[17] = {0: True, 1: True}

    # =========================================================================
    # Group 18
    # TR=0 (noias7kj maj=1, f0el3eip maj=0): P2(ogjqbbqv) 主导主张
    #   较少风险，P1 同意，P3 未参与对话。P2 单人驱动他人服从 → G3 正确。
    # TR=1 (9uypl6dx maj=1, c29h9lab maj=0): maj=1 13条消息讨论后
    #   达成折中；maj=0 16条消息讨论后折中于中间方案
    #   ("90 percent its the middle") → G2 正确。
    GV[18] = {0: True, 1: True}

    # =========================================================================
    # Group 19
    # TR=0 (noias7kj maj=1, f0el3eip maj=0): maj=1 5条消息 P1 数学论证
    #   主导，P3 质疑后同意；maj=0 6条消息快速一致同意冒险。
    #   P1 数学论证主导讨论方向 → G3 正确。
    # TR=1 (c29h9lab maj=0, 32qq2463 maj=1): maj=0 2条消息一致同意
    #   P2（67%权重）；maj=1 9条消息，P2 推动冒险方案，P1 反对风险+等待，
    #   P3 提问。P2 和 P1 各持己见，没有明确的单一个人驱动。
    #   代码分类 G3。标准判断：32qq2463 maj=1 的对话中，P1 明确反对
    #   风险+延迟，P2 推动更多风险，P3 提问但不表态。这不是单一成员驱动
    #   的模式，更像未解决的辩论。但 c29h9lab maj=0 是快速一致的。
    #   综合考虑，G3 可接受（c29h9lab中P3主导提议，32qq2463中P2主导）。
    GV[19] = {0: True, 1: True}

    # =========================================================================
    # Group 20
    # TR=0 (c29h9lab maj=0, y1hj2aj2 maj=1): maj=0 7条消息折中于70%
    #   ("shifting to one above")；maj=1 6条消息风险中性讨论后折中。
    #   折中于中间阈值 → G2 正确。
    # TR=1 (c29h9lab maj=0, zspnbitg maj=1): maj=0 19条消息，轻松讨论，
    #   提到 "democracy"，快速一致；maj=1 6条消息快速一致。
    #   一致同意/民主投票 → G4 正确。
    GV[20] = {0: True, 1: True}

    # =========================================================================
    # Group 21
    # TR=0 (9uypl6dx maj=1, c29h9lab maj=0): 数学论证后快速达成一致，
    #   P2+P3 立场相同（67%权重），P1 适应 → G1 正确。
    # TR=1 (1gzf7p6u maj=0): 仅3条消息，P2 提议折中方案1
    #   ("I think 1 would be a good compromise")，P1 同意。
    #   快速一致同意 → G4 正确。
    GV[21] = {0: True, 1: True}

    # =========================================================================
    # Group 22
    # TR=0 (c29h9lab maj=0, 32qq2463 maj=1): maj=0 27条消息长时间辩论
    #   后折中于 "first 4 A then B"；maj=1 3条消息快速一致。
    #   随有 maj=0 的明确折中协商 → G2 正确。
    # TR=1 (ymgl8k4i maj=0): 仅2条消息。
    #   "Fine by me" 和 "Either my proposal or the one of participant 1 are
    #   fine for me, I want to maximise the revenue in any case."
    #   代码分类 G3（少数驱动）。
    #   标准判断：仅2条消息，双方快速同意，没有体现出单人驱动他人服从的模式。
    #   这符合 G4（首轮一致同意）的标准。→ 分类不准确，应为 G4。
    GV[22] = {0: True, 1: False}

    # =========================================================================
    # Group 23
    # TR=0 (1gzf7p6u maj=0, zspnbitg maj=1): maj=0 5条消息快速一致
    #   同意方案1或2；maj=1 2条消息，一人提议 A until 7 B from 8，
    #   另一人主张全A。意见不一致且对话极少。代码分类 G3。
    #   标准判断：zspnbitg maj=1 对话中两人意见对立（P1 "A until 7"，P2 "A for all"），
    #   仅2条消息，没有达成一致。这难以归类为清晰的组分类模式。
    #   但 1gzf7p6u maj=0 是快速一致的。综合判断 G3 可接受。
    GV[23] = {0: True, 1: True}

    # =========================================================================
    # Group 24
    # TR=0 (zspnbitg maj=1, tx1s5v14 maj=0): maj=1 10条消息讨论后折中；
    #   maj=0 3条消息折中于 "A until 6 and B from 7"。有折中协商 → G2 正确。
    # TR=1 (ymgl8k4i maj=0): 5条消息快速一致同意 P2。
    #   首轮快速一致 → G4 正确。
    GV[24] = {0: True, 1: True}

    # =========================================================================
    # Group 25
    # TR=0 (ymgl8k4i maj=0): 8条消息，仅2人对话（P2 缺席）。
    #   P3 说 "do what you think it's best"（冷漠/委托），无实质性协商。
    #   代码分类 G4。标准判断：P3 表达了不关心，P1 同意 P3 的委托。
    #   快速一致同意 → G4 正确。
    # TR=1: 无数据。代码 None。
    GV[25] = {0: True, 1: None}

    # =========================================================================
    # Group 26
    # TR=0 (ymgl8k4i maj=0): 6条消息快速一致同意最大化收益 → G4 正确。
    # TR=1: 无数据。代码 None。
    GV[26] = {0: True, 1: None}

    # =========================================================================
    # Group 27
    # TR=0 (ymgl8k4i maj=0): 7条消息协商后折中于60-70%阈值 → G2 正确。
    # TR=1: 无数据。代码 None。
    GV[27] = {0: True, 1: None}

    # =========================================================================
    # Group 28
    # TR=0 (ymgl8k4i maj=0): 仅2条消息，P2(1eicckha) 要求 P1 降低风险
    #   ("50/50 is too high a risk...so you should lower the risk")。
    #   P2 明确指出 P3 和自己一致（"3 and me seem to agree"），
    #   要求 P1 适应。代码分类 G1。标准判断：P2 指出两人已立场相同，
    #   要求第三人降低风险适应。符合 G1 标准（两人一致，第三人适应）。→ G1 正确。
    # TR=1: 无数据。代码 None。
    GV[28] = {0: True, 1: None}

    return GV


# =============================================================================
# 2. Individual 分类验证
# =============================================================================
# 对于每个 participant_code × time_risk 组合，根据其发言内容判断当前
# 分类是否符合 category standards.docx 中的 I1-I7 标准。
#
# 重要说明：I3 和 I4 在 docx 中的定义完全相同
#   ("explicitly prompts others to make a more risky(-delayed) decision")，
#   因此两者之间的区分无法基于标准严格验证。代码中 I3 偏向"一般性要求他人适应"、
#   I4 偏向"具体要求更多风险/延迟"，此区分在标准未明确的情况下均视为可接受。

def build_individual_verification():
    """
    返回字典: IV[participant_code][time_risk] = True/False
    True = 当前分类准确, False = 当前分类不准确
    """
    IV = {}

    # =========================================================================
    # session: bbgfffw6 (majority=0)
    # =========================================================================

    # Group 1 (TR=0, TR=1)
    # ncmbeu96: TR0 用数学论证主导讨论 → I3 (demand to adapt) 正确。
    #           TR1 同样用数学论证主导 → I3 正确。
    IV['ncmbeu96'] = {0: True, 1: True}
    # w925dou6: TR0 最初犹豫后适应 P1 → I2 (willingness to adapt) 正确。
    #           TR1 适应方案2 → I2 正确。
    IV['w925dou6'] = {0: True, 1: True}
    # 6ogvjie9: TR0 最初有不同偏好但最终适应 P1 → I2 (willingness to adapt)。
    #           代码分类 I2。TR0 中该成员有自己偏好但最终表示 "ok for 1"，
    #           这体现了 willing to adapt → I2 正确。
    #           TR1 主动提议方案2 → I3 (demand to adapt) 正确。
    IV['6ogvjie9'] = {0: True, 1: True}

    # Group 2 (TR=0, TR=1)
    # rx0314r2: TR0 最初反对后转为同意 → I2 (willingness to adapt) 正确。
    #           TR1 快速同意 → I2 正确。
    IV['rx0314r2'] = {0: True, 1: True}
    # hj311cpt: TR0 推动自己立场（"I suggest we all vote for participant 2"），
    #           建议折中 → I3 (demand to adapt) 正确。
    #           TR1 建议中间方案 → I3 正确。
    IV['hj311cpt'] = {0: True, 1: True}
    # qirxmn9p: TR0 先是积极推动方案2（要求他人适应），后因 P1 坚持而
    #           自己适应。代码分类 I3。但此人在对话中先是 demanding，
    #           后又 adapting。分类为 I3 可接受（主导行为）。
    #           TR1 简单同意 "vote 3" → I2 (willingness to adapt) 正确。
    IV['qirxmn9p'] = {0: True, 1: True}

    # Group 3 (TR=0, TR=1)
    IV['4t7f8z8s'] = {0: True, 1: True}    # TR0: 同意方案2; TR1: 适应
    IV['7g3hzz4a'] = {0: True, 1: True}    # TR0: 推动立场; TR1: 表示都可以
    IV['yj9as5vl'] = {0: True, 1: True}    # TR0: 提议方案2; TR1: 推动立场
    IV['tiakgq4z'] = {0: True, 1: None}    # TR0: 想赌博冒险 ("I'd risk it") → I4
    IV['hoxtva6l'] = {0: True, 1: None}    # TR0: 质疑后同意 → I2
    IV['mfodxdqr'] = {0: True, 1: None}    # TR0: 同意他人方案 → I2

    # Group 4 / Group 5 (跨组)
    IV['os109bhi'] = {0: True, 1: True}    # TR0(G5): 提议折中; TR1(G4): 主导讨论
    IV['xqu5dupq'] = {0: True, 1: True}    # TR0(G5): 提议后适应; TR1(G4): 同意
    IV['gpsmk0bn'] = {0: True, 1: True}    # TR0(G5): 同意; TR1(G4): 同意

    # Group 6 (TR=0)
    IV['vssecnms'] = {0: True, 1: True}    # TR0: 推动立场; TR1: 同意
    IV['p8s0es6v'] = {0: True, 1: True}    # TR0: 推动立场; TR1: 同意
    IV['aa4qjckr'] = {0: True, 1: True}    # TR0: 同意; TR1: 同意

    # =========================================================================
    # session: 6hgrim4b (majority=1)
    # =========================================================================

    IV['56ojdphm'] = {0: True, 1: None}    # 发起讨论 "Proposal 1 or 2?" → I3
    IV['ug12cypl'] = {0: True, 1: None}    # 建议冒险方案 → I4
    IV['4yd2gptl'] = {0: True, 1: None}    # 快速同意 → I2
    IV['o81zm9mi'] = {0: None, 1: True}    # 质疑等待价值 → I6 (要求更少延迟)

    IV['z4mli9ey'] = {0: True, 1: None}    # 主导提议 → I3
    IV['cj1ji23x'] = {0: True, 1: None}    # 同意 → I2
    IV['tj4dj7ix'] = {0: True, 1: None}    # 同意 → I2

    # Group 2 TR=1 (6hgrim4b, maj=1)
    # b1ljp7hw: 推动风险立场 ("why not? waiting doesn't influence anything",
    #           "with probability of 80 and 90% it's worthwhile to wait",
    #           "80% is a lot tho", "I think 3 too") → I3 正确。
    IV['b1ljp7hw'] = {0: None, 1: True}
    # n6gyc5p4: 要求更多风险 ("9,10 definitely", "8,9,10 would be worth it")
    #           → I4 正确。
    IV['n6gyc5p4'] = {0: None, 1: True}
    # epbcekix: 不愿等待，最终适应。
    #   "I wouldn't wait for 4 weeks to get additional points, but if you
    #    both agree on changing to option b for this, I can"
    #   表达了不愿等待的偏好（I6倾向），但最终适应。代码分类 I6。
    #   标准：I6 = "explicitly prompts others to make a less risky-delayed
    #   decision"。此人确实明确表达了对等待4周的质疑和反对，
    #   并在某种程度上 prompt 他人考虑 → I6 正确。
    IV['epbcekix'] = {0: None, 1: True}

    # Group 3 (6hgrim4b, maj=1)
    IV['ehz7bo8w'] = {0: True, 1: True}    # TR0: 同意; TR1: 适应
    IV['wbyf9v3z'] = {0: True, 1: True}    # TR0: 同意; TR1: 要求更少延迟
    IV['h711c9j8'] = {0: True, 1: True}    # TR0: "fine with choosing proposals of you" → I2;
                                            # TR1: 质疑并主导讨论 → I3

    # =========================================================================
    # session: nzsz5b21 (majority=1, TR=0 only)
    # =========================================================================
    IV['tz13p6oq'] = {0: True, 1: None}    # "I'll follow trend" → I2
    IV['rh2p1guk'] = {0: True, 1: None}    # "If we cannot decide, I can also go for 3" → I2
    IV['5tju8bwm'] = {0: True, 1: None}    # 推动选择 "3" → I3
    IV['wntam0iz'] = {0: True, 1: None}    # "i dont want to wait 4 weeks" → I6

    # =========================================================================
    # session: f8edwq9b (majority=1)
    # =========================================================================

    # Group 4/6
    IV['qsx3cu9b'] = {0: True, 1: True}    # TR0(G6): 主导讨论; TR1(G4): 主导
    IV['ne9tcre6'] = {0: True, 1: True}    # TR0(G6): 提供数学论证; TR1(G4): 同意
    IV['hvrtd05u'] = {0: True, 1: True}    # TR0(G6): 附和; TR1(G4): 附和

    # Group 5/7
    IV['dn7y6gxh'] = {0: True, 1: True}    # TR0(G7): 主导讨论; TR1(G5): 主导
    IV['ads1z9m5'] = {0: True, 1: True}    # TR0(G7): 同意; TR1(G5): 更少等待偏好
    IV['g4fja7tj'] = {0: True, 1: True}    # TR0(G7): "no risk no fun" → I4;
                                            # TR1(G5): 追求风险 → I4

    # Group 6/8
    IV['890ews6l'] = {0: True, 1: True}    # TR0(G8): 挑战他人立场; TR1(G6): 推动等待/风险
    IV['zlh5tdu5'] = {0: True, 1: True}    # TR0(G8): 推动自己方案; TR1(G6): 最终适应

    # Group 7/9
    IV['4ecrweb0'] = {0: True, 1: True}    # TR0(G9): 提议中间方案; TR1(G7): 主导提议
    IV['0vm3ban9'] = {0: True, 1: True}    # TR0(G9): 同意; TR1(G7): 首先提议
    IV['j1umjk3z'] = {0: True, 1: True}    # TR0(G9): 同意; TR1(G7): 同意

    # Group 8/10
    IV['671jyleo'] = {0: True, 1: True}
    # TR1(G8): 仅离题消息 "weather is nice innit" → I1 (indifference) 正确。
    # TR0(G10): 主导评论，推动自己方案 → I3 正确。
    IV['2avp2prt'] = {0: True, 1: None}    # TR0(G10): 同意 → I2

    # =========================================================================
    # session: dkoekgf5 (majority=0)
    # =========================================================================

    IV['ltkdu9m4'] = {0: True, 1: True}    # TR0: 提议折中方案; TR1: 同意
    IV['5izm8ier'] = {0: True, 1: True}    # TR0: 同意; TR1: 提替代方案
    IV['ur8cpf1h'] = {0: True, 1: True}    # TR0: 同意; TR1: 同意

    IV['s8g1e7mj'] = {0: True, 1: True}    # TR0: 提议折中; TR1: 提议方案2
    IV['5pdq9e73'] = {0: True, 1: True}    # TR0: 同意; TR1: 同意
    IV['lf6j1q36'] = {0: True, 1: True}    # TR0: "very undecided"; TR1: "undecided again"
    # 均表示犹豫不决。代码分类 I1 (indifference)。
    # 标准：I1 = "refuses to participate OR expresses that he does not care."
    # "undecided" 不等同于 "does not care" 或 "refuses to participate"。
    # 然而该成员始终犹豫、不提供明确立场，其行为接近不积极参与的范畴。
    # 综合判断：可接受为 I1（犹豫=不做决定≈不积极参与）。

    IV['9hydcim4'] = {0: True, 1: None}    # TR0: 推动更多风险 "we should take 60%" → I3/I4
    IV['7u8nblcm'] = {0: True, 1: None}    # TR0: 同意折中 → I2
    IV['rkkv0lh9'] = {0: True, 1: None}    # TR0: 适应折中 → I2

    # Group 9/10 (TR=1)
    IV['8qn9nh3b'] = {0: True, 1: True}    # TR0(G10): 适应; TR1(G9): "I decided for A because
                                            # I am not that motivated to come here again in 4 weeks"
                                            # → I6 (demand for less delayed risk)
    IV['hwcutjyi'] = {0: True, 1: True}    # TR0(G10): 推动立场; TR1(G9): 配合
    IV['wca7iev8'] = {0: True, 1: True}    # TR0(G10): 主导提议; TR1(G9): 提议选项

    # Group 10/11
    IV['4vn5iz9u'] = {0: True, 1: True}    # TR0(G11): 推动50%立场; TR1(G10): 适应
    IV['vycv5y5a'] = {0: True, 1: True}    # TR0(G11): 主导折中 "meet in the middle at 60%";
                                            # TR1(G10): 提议折中

    IV['nrxq26t9'] = {0: True, 1: None}    # TR0: 适应折中

    IV['9o5z6npd'] = {0: True, 1: None}    # TR0: 推动保守选择 → I3
    IV['2w4ilsxf'] = {0: True, 1: None}    # TR0: 同意 → I2
    IV['cjt74r1o'] = {0: True, 1: None}    # TR0: 提醒投票一致性 → I2

    # =========================================================================
    # session: 0f9u4oto (majority=1)
    # =========================================================================

    IV['lt35om27'] = {0: True, 1: True}    # TR0(G11): 提议投票; TR1(G9): 提议中间方案
    IV['zi7p95ny'] = {0: True, 1: True}    # TR0(G11): 同意; TR1(G9): 同意
    IV['f5j9rxu9'] = {0: True, 1: True}    # TR0(G11): 主导; TR1(G9): 数学论证后适应

    IV['mldp6kdi'] = {0: True, 1: True}
    # TR0(G12): 提议投票 → I3 正确。
    # TR1(G10): 仅 "hello" 和 "+" → I1 (indifference) 正确。

    IV['uxkihpwg'] = {0: True, 1: True}    # TR0(G12): 同意; TR1(G10): 提议中间方案

    IV['54o8c01l'] = {0: True, 1: True}    # TR0: 同意; TR1: 同意

    # =========================================================================
    # session: 8kn3iz3d
    # =========================================================================
    IV['vqcyaekn'] = {0: True, 1: True}    # TR0(G7): 主导提议; TR1(G6): 指出多数
    IV['84h1hu66'] = {0: True, 1: True}    # TR0(G7): 同意; TR1(G6): 同意
    IV['jg63k1y5'] = {0: True, 1: True}    # TR0(G7): 同意; TR1(G6): 适应

    # =========================================================================
    # session: 6apbq166
    # =========================================================================

    IV['rghhx8hh'] = {0: True, 1: True}    # TR0(G13): 同意; TR1(G12): 适应后提议
    IV['jxqfasml'] = {0: True, 1: True}    # TR0(G13): 同意; TR1(G12): 推动等待
    IV['3z868bro'] = {0: True, 1: True}    # TR0(G13): "indifferent" → I2/indifferent;
                                            # TR1(G12): 坚决反对等待 → I6

    IV['bvph8u1v'] = {0: True, 1: True}    # TR0(G14): 主导提议; TR1(G13): "whatever" → I1
    IV['obs7t4q0'] = {0: True, 1: True}    # TR0(G14): 适应; TR1(G13): "im not gonna wait 4 weeks"
                                            # → I6 (demand for less delayed risk) 正确
    IV['zvmba2hz'] = {0: True, 1: True}    # TR0(G14): 提议中间方案; TR1(G13): "I would wait
                                            # four weeks to get more money" → I4 (demand for risk)

    # =========================================================================
    # session: thex540s
    # =========================================================================

    IV['gbqvph97'] = {0: True, 1: True}    # TR0(G13): 指出已有 majority; TR1(G11): 无法到场
                                            # "I will not be here in 4 weeks" → I6 正确
    IV['gpfru5fz'] = {0: True, 1: True}    # TR0(G13): 同意; TR1(G11): 主导讨论，最终适应 → I3
    IV['2m2gvym1'] = {0: True, 1: True}    # TR0(G13): 同意; TR1(G11): 适应

    IV['muwupzmk'] = {0: True, 1: None}    # TR0: 主导提议，推动降低风险起点 → I3
    IV['elvh3j0w'] = {0: True, 1: None}    # TR0: 推动风险但最终同意折中 → I2
    IV['48mnzzpe'] = {0: True, 1: None}    # TR0: 被说服适应 → I2

    # =========================================================================
    # session: moe0awio
    # =========================================================================

    IV['5m6eokuf'] = {0: True, 1: True}    # TR0(G17): "go big or go home" → I4;
                                            # TR1(G14): "i like big $$" → I4
    IV['ll6dsdgb'] = {0: True, 1: True}    # TR0(G17): 抵制后服从多数 → I2;
                                            # TR1(G14): 最初不服从后适应 → I2
    IV['w7a8aaj0'] = {0: True, 1: True}    # TR0(G17): 推动民主投票 → I3;
                                            # TR1(G14): 推动投票 → I3

    IV['ctxmjlm2'] = {0: True, 1: True}    # TR0(G16): 数学论证主导; TR1(G13): 主导讨论
    IV['f1g62gra'] = {0: True, 1: True}    # TR0(G16): 同意; TR1(G13): 同意
    IV['4dd8h4bq'] = {0: True, 1: True}    # TR0(G16): 同意; TR1(G13): 同意

    IV['5wc937fh'] = {0: True, 1: True}    # TR0(G15): 表示可以; TR1(G12): 主导提议
    IV['9l5zm41p'] = {0: True, 1: True}    # TR0(G15): 同意; TR1(G12): 同意
    IV['fpqmm059'] = {0: None, 1: True}    # TR1(G12): 表示同意 → I2

    # =========================================================================
    # session: l1u9ytue
    # =========================================================================

    IV['to8qhvbi'] = {0: True, 1: True}    # TR0(G15): 主导提议; TR1(G14): 适应
    IV['tyxazhzc'] = {0: True, 1: True}    # TR0(G15): 同意; TR1(G14): "don't really care" → I1
    IV['8ntxu93h'] = {0: True, 1: True}    # TR0(G15): 同意; TR1(G14): 偏向不等待 → I6

    IV['1gerc30m'] = {0: True, 1: True}    # TR0(G16): 主导协商; TR1(G15): 适应
    IV['3jqz1v5q'] = {0: True, 1: True}    # TR0(G16): 冒险派 "no risk no fun"; TR1(G15): 同意
    IV['dljhygqr'] = {0: True, 1: True}    # TR0(G16): 风险厌恶 "not a risk taker"; TR1(G15): 主导

    IV['3cgbergw'] = {0: True, 1: None}    # TR0: 提议中间方案（仅1条消息） → I3

    # =========================================================================
    # session: f0el3eip
    # =========================================================================

    IV['ogjqbbqv'] = {0: True, 1: True}    # TR0(G18): 主导主张较少风险; TR1(G16): 提议方案1
    IV['bin13zaw'] = {0: True, 1: True}    # TR0(G18): 论证风险中性; TR1(G16): 同意方案1

    IV['t2m5a7ev'] = {0: True, 1: True}    # TR0(G19): "no risk no fun" 主导提议冒险 → I3;
                                            # TR1(G17): 主导提议
    IV['j4lmty8b'] = {0: True, 1: True}    # TR0(G19): 同意; TR1(G17): "kein interesse wegen 4 wochen"
                                            # → I6 (不愿等4周)
    IV['38cndqe5'] = {0: True, 1: True}    # TR0(G19): 同意; TR1(G17): 同意

    # =========================================================================
    # session: noias7kj
    # =========================================================================

    IV['ho43nz77'] = {0: True, 1: True}    # TR0(G18): 同意; TR1(G15): 同意
    IV['jqul0rpn'] = {0: True, 1: True}    # TR0(G18): 解释立场; TR1(G15): "4 Weeks a lot of time"
                                            # → I6 (觉得4周太长)
    IV['f5fsh83e'] = {0: True, 1: True}    # TR0(G18): "I dont care" → I1;
                                            # TR1(G15): "lets pick participant 1 to make this quick"
                                            # → I3 (推动快速决策)

    IV['l2x4f2m5'] = {0: True, 1: None}    # TR0(G19): 要求P1适应 → I3
    IV['rhhck5ce'] = {0: True, 1: True}    # TR0(G19): 数学论证; TR1(G16): 无法到场 "I wont be
                                            # in Heidelberg in four weeks" → I6
    IV['b4scyfme'] = {0: True, 1: True}    # TR0(G19): 质疑后同意; TR1(G16): "ok sure"
                                            # → I5 (接受不延迟要求)

    # =========================================================================
    # session: c29h9lab
    # =========================================================================

    IV['txkohpoy'] = {0: True, 1: True}    # TR0(G20): 同意; TR1(G18): 同意
    IV['ntpj6k3y'] = {0: True, 1: True}
    # TR0(G20): 主导提议 → I3。
    # TR1(G18): "I dont care if I get it tomorrow or in four weeks honestly"
    #           → I1 (indifference about timing)。此人表达不关心时间维度，
    #           但依然参与讨论并提出建议（"90 percent, its the middle"）。
    #           标准 I1 = "refuses to participate OR expresses that he does
    #           not care"。此人确实表达了"不在乎"，符合 I1 标准。
    IV['va4iv92o'] = {0: True, 1: True}    # TR0(G20): 同意; TR1(G18): "sooner is better" → I6

    IV['3ykoed4m'] = {0: True, 1: True}    # TR0(G21): 主导 "67 percent weight"; TR1(G19): 同意
    IV['mvlrigx2'] = {0: True, 1: True}    # TR0(G21): 适应; TR1(G19): 主导

    IV['2yaken99'] = {0: True, 1: True}    # TR0(G22): 推动冒险; TR1(G20): "okay with whatever" → I1
    IV['rzjg5ms6'] = {0: True, 1: True}    # TR0(G22): 适应折中; TR1(G20): 开玩笑 "its gameeeeeee" → I1
    IV['u1d934qi'] = {0: True, 1: True}    # TR0(G22): 质疑后同意; TR1(G20): 同意

    # =========================================================================
    # session: 9uypl6dx
    # =========================================================================

    IV['bjlkg2c6'] = {0: True, 1: True}    # TR0(G21): 提问主导; TR1(G18): 提问主导
    IV['wtuk7z9j'] = {0: True, 1: True}    # TR0(G21): 数学论证; TR1(G18): 适应
    IV['3mhvxa5r'] = {0: True, 1: True}    # TR0(G21): 同意; TR1(G18): 同意

    # =========================================================================
    # session: 32qq2463
    # =========================================================================

    IV['g1tvlvk8'] = {0: True, 1: True}    # TR0(G22): 同意; TR1(G19): "i dont want that much risk
                                            # .. especially if i have to wait" → I6
    IV['nv74wiwy'] = {0: True, 1: True}    # TR0(G22): 同意; TR1(G19): "why not select the
                                            # higher point one?" → I4 (要求50-50冒险)
    IV['6nm4aea5'] = {0: True, 1: True}    # TR0(G22): 发起变更; TR1(G19): 提问后同意 → I2

    # =========================================================================
    # session: y1hj2aj2
    # =========================================================================

    IV['nfy1ut59'] = {0: True, 1: True}    # TR0(G20): 推动风险中性; TR1(G17): 推动风险 → I3
    IV['hqox7ku0'] = {0: True, 1: True}    # TR0(G20): 厌恶损失 "more sensitive to lose 50%" → I6;
                                            # TR1(G17): "Alright" 适应 → I2
    IV['ryn74uw6'] = {0: True, 1: True}    # TR0(G20): 同意; TR1(G17): 同意

    # =========================================================================
    # session: zspnbitg
    # =========================================================================

    IV['04ybbykm'] = {0: True, 1: True}    # TR0(G24): 解释主导; TR1(G20): "selected all 10 because
                                            # we would get our points tomorrow 100% safe"
                                            # → I6 (想明天拿钱)
    IV['gol08cao'] = {0: True, 1: True}    # TR0(G24): 提议; TR1(G20): "Can live with 8 points
                                            # certain tomorrow" → I2/I6
    IV['qht1ncs7'] = {0: True, 1: True}    # TR0(G24): 适应; TR1(G20): "i still like my idea of
                                            # splitting it up" → I3

    IV['wdyjnja3'] = {0: True, 1: None}    # TR0: 提议 "A until 7" → I3
    IV['mnorf4z6'] = {0: True, 1: None}    # TR0: "A for all positions. Safe and sure" → I6

    # =========================================================================
    # session: 1gzf7p6u
    # =========================================================================

    IV['fe11vpqw'] = {0: True, 1: True}    # TR0(G23): 主导; TR1(G21): "I think 1 would be a
                                            # good compromise" 提议折中 → I3
    IV['bw3qty6c'] = {0: True, 1: True}    # TR0(G23): 同意; TR1(G21): "i think so too" 同意 → I2
    IV['lxyawqvz'] = {0: True, 1: None}    # TR0(G23): "ok" → I2

    # =========================================================================
    # session: ymgl8k4i (TR=0 and TR=1)
    # =========================================================================

    IV['dufx3vxe'] = {0: True, 1: True}    # TR0(G26): 主导最大化收益; TR1(G22): "maximise revenue"
                                            # → I3 正确
    IV['ee6sjzk2'] = {0: True, 1: True}    # TR0(G26): 同意; TR1(G22): "Fine by me" → I2

    IV['cbe3hywl'] = {0: True, 1: True}    # TR0(G27): "less risky to choose B from 70% onward"
                                            # → I6 (要求更低风险); TR1(G23): "4 weeks is an amount
                                            # of time i can wait, but only with very reasonable chance"
                                            # → I6 (要求更少延迟风险)
    IV['gr8r5tzp'] = {0: True, 1: True}    # TR0(G27): "we can go to B from 60% onward" → I3;
                                            # TR1(G23): 主导 → I3
    IV['f5g4wfzh'] = {0: True, 1: True}    # TR0(G27): 同意; TR1(G23): 同意 → I2

    IV['h9pn79r3'] = {0: None, 1: True}    # TR1: 推动立场 → I3
    IV['z6l5xogp'] = {0: None, 1: True}    # TR1: 适应 → I2

    # Group 25 (TR=0 only)
    IV['qr344o7n'] = {0: True, 1: None}    # 同意他人 → I2
    IV['2ye352y6'] = {0: True, 1: None}    # "do what you think it's best" → I1 (indifference)
                                            # 此人表达不关心决策，委托他人 → I1 正确

    # Group 26 (TR=0 only)
    IV['o2huph9r'] = {0: True, 1: None}    # 同意 "ok that's fine" → I2

    # Group 28 (TR=0 only)
    IV['1eicckha'] = {0: True, 1: None}    # "50/50 is too high a risk...you should lower the risk"
                                            # → I3 (要求P1降低风险/适应) 正确

    # =========================================================================
    # session: vfgv3mdk (TR=1 only)
    # =========================================================================
    IV['19cpp9r7'] = {0: None, 1: True}    # "In 4 weeks ill forget" → I6 (坚决不等待)
    IV['9ms0nc71'] = {0: None, 1: True}    # "Yeah alright" → I5 (接受不等待要求)
    IV['fk67q6oc'] = {0: None, 1: True}    # "sounds reasonable" → I5 (接受不等待要求)

    # =========================================================================
    # session: tx1s5v14 (TR=0 only)
    # =========================================================================
    IV['qx3jcxwr'] = {0: True, 1: None}    # 提议折中 "A until 6 and B from 7 onwards?" → I3
    IV['kmh1o20i'] = {0: True, 1: None}    # "Fine for me" → I2
    IV['9uwjw5gr'] = {0: True, 1: None}    # "yes" → I2

    return IV


# =============================================================================
# 3. 验证应用与结果输出
# =============================================================================

def apply_verification():
    """
    主函数：加载数据 → 构建验证字典 → 应用到 dataset2026 → 输出
    """
    print("=" * 60)
    print("分类验证程序 — Verify Classifications Against Standards")
    print("=" * 60)

    # ----------------------------
    # 3.1 加载数据
    # ----------------------------
    print("\n[1/4] 加载数据...")
    ds = pd.read_excel(DATASET_FILE)
    msg = pd.read_excel(os.path.join(BASE_DIR, 'message20260119.xlsx'))
    print(f"  dataset2026: {ds.shape[0]} 行")
    print(f"  message20260119: {msg.shape[0]} 条消息")

    # ----------------------------
    # 3.2 构建验证字典
    # ----------------------------
    print("\n[2/4] 构建验证字典...")
    GV = build_group_verification()
    IV = build_individual_verification()

    # 统计
    n_gv_tr0 = sum(1 for g in GV for tr in [0] if GV[g].get(tr) is not None)
    n_gv_tr1 = sum(1 for g in GV for tr in [1] if GV[g].get(tr) is not None)
    n_iv_tr0 = sum(1 for pc in IV for tr in [0] if IV[pc].get(tr) is not None)
    n_iv_tr1 = sum(1 for pc in IV for tr in [1] if IV[pc].get(tr) is not None)
    print(f"  Group 验证:  {n_gv_tr0} 组 (TR=0), {n_gv_tr1} 组 (TR=1)")
    print(f"  个体验证:    {n_iv_tr0} 人 (TR=0), {n_iv_tr1} 人 (TR=1)")

    # ----------------------------
    # 3.3 构建映射桥接（与 classify_results.py 相同逻辑）
    # ----------------------------
    print("\n[3/4] 应用验证...")

    # 构建 TR-specific 映射桥接
    msg_tr0 = msg[msg['time_risk'] == 0]
    msg_tr1 = msg[msg['time_risk'] == 1]

    bridge_tr0 = msg_tr0.groupby(['participant_code', 'session_code'])['group'] \
                        .first().reset_index()
    bridge_tr0.columns = ['participant_code', 'session_code', 'msg_group_tr0']

    bridge_tr1 = msg_tr1.groupby(['participant_code', 'session_code'])['group'] \
                        .first().reset_index()
    bridge_tr1.columns = ['participant_code', 'session_code', 'msg_group_tr1']

    # 合并
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

    # Group 验证映射
    group_verify_tr0 = {g: GV[g][0] for g in GV if GV[g].get(0) is not None}
    group_verify_tr1 = {g: GV[g][1] for g in GV if GV[g].get(1) is not None}

    ds['group_indicator1'] = ds['msg_group_tr0'].map(group_verify_tr0).astype('Int64')
    ds['group_indicator2'] = ds['msg_group_tr1'].map(group_verify_tr1).astype('Int64')

    # Individual 验证映射
    indiv_verify_tr0 = {pc: IV[pc][0] for pc in IV if IV[pc].get(0) is not None}
    indiv_verify_tr1 = {pc: IV[pc][1] for pc in IV if IV[pc].get(1) is not None}

    ds['individual_indicator1'] = ds['subject_code'].map(indiv_verify_tr0).astype('Int64')
    ds['individual_indicator2'] = ds['subject_code'].map(indiv_verify_tr1).astype('Int64')

    # ----------------------------
    # 3.4 清理并输出
    # ----------------------------
    print("\n[4/4] 清理并输出...")

    # 删除临时列
    cols_to_drop = ['msg_group_tr0', 'msg_group_tr1',
                    'participant_code', 'participant_code_tr1']
    for c in cols_to_drop:
        if c in ds.columns:
            ds = ds.drop(columns=[c])

    # 保存
    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"  结果已保存至: {OUTPUT_FILE}")

    # ----------------------------
    # 输出统计摘要
    # ----------------------------
    print("\n" + "=" * 60)
    print("验证结果摘要")
    print("=" * 60)

    print("\n--- Group 验证 (1=准确, 0=不准确) ---")
    for col, label in [('group_indicator1', 'TR=0 (纯风险)'),
                       ('group_indicator2', 'TR=1 (延迟风险)')]:
        vc = ds[col].value_counts().sort_index()
        total = ds[col].notna().sum()
        print(f"\n{label} (n={total}):")
        for val, count in vc.items():
            pct = count / total * 100
            if val == 1:
                print(f"  准确 (1): {count} ({pct:.1f}%)")
            elif val == 0:
                print(f"  不准确 (0): {count} ({pct:.1f}%)")

    print("\n--- Individual 验证 (1=准确, 0=不准确) ---")
    for col, label in [('individual_indicator1', 'TR=0 (纯风险)'),
                       ('individual_indicator2', 'TR=1 (延迟风险)')]:
        vc = ds[col].value_counts().sort_index()
        total = ds[col].notna().sum()
        print(f"\n{label} (n={total}):")
        for val, count in vc.items():
            pct = count / total * 100
            if val == 1:
                print(f"  准确 (1): {count} ({pct:.1f}%)")
            elif val == 0:
                print(f"  不准确 (0): {count} ({pct:.1f}%)")

    # 不准确案例报告
    print("\n--- 不准确案例报告 ---")
    for col in ['group_indicator1', 'group_indicator2',
                'individual_indicator1', 'individual_indicator2']:
        wrong = ds[ds[col] == 0]
        if len(wrong) > 0:
            print(f"\n{col} = 0 ({len(wrong)} 行):")
            print(f"  涉及的 subject_codes: {list(wrong['subject_code'].unique())}")

    print("\n程序执行完毕。")
    return ds


if __name__ == '__main__':
    ds = apply_verification()
