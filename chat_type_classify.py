"""
=============================================================================
Chat Type Classification — 对话类型分类
=============================================================================

基于 message20260119.xlsx 中 97 个对话会话的定性分析，将每个小组
（session_code × group）在每个 time_risk 条件下的对话互动模式归为
以下 6 种类型：

  Type 1: 快速一致 (Quick Consensus)
         首轮即达成一致，几乎无实质性讨论（通常 ≤5 条消息）
         典型语言: "yes, lets do proposal 1", "fine with me", "ok"

  Type 2: 数学说服 (Mathematical Persuasion)
         成员用期望值计算、数学论证说服他人
         典型语言: "expectation value 0.6×12+0.4×4=8.6",
                   "the break even point is at 50%"

  Type 3: 协商折中 (Negotiated Compromise)
         立场不同，经过讨论后取中间方案
         典型语言: "should we come to an agreement in the middle?",
                   "meet in the middle at 60%", "first 4 A, then B"

  Type 4: 多数跟随 (Majority Alignment)
         两人立场一致或快速达成一致，第三人最终适应
         典型语言: "since you both choose 3, i will 3 too",
                   "3 and me seem to agree so you should lower the risk"

  Type 5: 单人主导 (Single-Driver)
         一人主导讨论方向，其他成员较为被动或冷漠
         典型语言: 主导者长段论证 + 他人 "ok", "fine", "whatever"

  Type 6: 冷漠委托 (Indifferent Delegation)
         成员不积极参与，委托他人决定，或完全离题
         典型语言: "do what you think it's best",
                   "I honestly dont really care", 完全离题

数据流:
  message20260119.xlsx 对话 → 逐组定性判断 → dataset2026.xlsx
  (chat_type1 for TR=0, chat_type2 for TR=1)

作者: Claude Code
日期: 2026-05-18
=============================================================================
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_FILE = os.path.join(BASE_DIR, 'message20260119.xlsx')
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')

# 类型标签
TYPE_LABELS = {
    1: '快速一致 (Quick Consensus)',
    2: '数学说服 (Mathematical Persuasion)',
    3: '协商折中 (Negotiated Compromise)',
    4: '多数跟随 (Majority Alignment)',
    5: '单人主导 (Single-Driver)',
    6: '冷漠委托 (Indifferent Delegation)',
}


def build_chat_type_classification():
    """
    基于对全部 97 个对话会话的逐条阅读和定性分析，
    返回每个 (session_code, msg_group, time_risk) 的对话类型。

    返回: dict[(session_code, group, time_risk)] = 1-6
    """
    ct = {}

    # ==================================================================
    # TR = 0
    # ==================================================================

    # --- bbgfffw6 ---
    ct[('bbgfffw6', 1, 0)] = 2   # ncmbeu96用期望值数学论证主导，P2/P3适应
    ct[('bbgfffw6', 2, 0)] = 4   # P3倡导P2方案，P1坚持，P2缺席，P3转向P1
    ct[('bbgfffw6', 3, 0)] = 1   # 快速一致同意方案2 (7条)，一人推动冒险
    ct[('bbgfffw6', 4, 0)] = 4   # P1+P2不同意方案3，P3妥协方案2
    ct[('bbgfffw6', 5, 0)] = 3   # P1提议折中 "Should we come to an agreement in the middle?"
    ct[('bbgfffw6', 6, 0)] = 3   # 讨论风险百分比后折中

    # --- 6hgrim4b ---
    ct[('6hgrim4b', 1, 0)] = 1   # 快速同意 (3条) "its basically the same, so 1?"
    ct[('6hgrim4b', 2, 0)] = 1   # P1主导提议，P2+P3快速同意 (5条)
    ct[('6hgrim4b', 3, 0)] = 1   # 三方快速一致同意 (5条)

    # --- nzsz5b21 ---
    ct[('nzsz5b21', 4, 0)] = 6   # 仅1条 "already have majority, I'll follow trend"
    ct[('nzsz5b21', 5, 0)] = 1   # 3条，P1选3，P2愿意适应，P3不想等

    # --- f8edwq9b ---
    ct[('f8edwq9b', 6, 0)] = 2   # P1+P2数学论证讨论 (21条)，P3开始时不确定后同意
    ct[('f8edwq9b', 7, 0)] = 3   # 三方各自陈述风险偏好，长篇讨论 (22条) 后折中
    ct[('f8edwq9b', 8, 0)] = 5   # P1挑战P3立场，P3坚持 (5条)
    ct[('f8edwq9b', 9, 0)] = 1   # P2提议中间方案，快速同意 (8条)
    ct[('f8edwq9b', 10, 0)] = 5  # P2主导评论，P3同意 (5条)

    # --- dkoekgf5 ---
    ct[('dkoekgf5', 7, 0)] = 3   # P1提议折中 "might be a compromise" (7条)
    ct[('dkoekgf5', 8, 0)] = 3   # P1说 "its a compromise" (9条)
    ct[('dkoekgf5', 9, 0)] = 3   # 协商后折中于60% (11条)
    ct[('dkoekgf5', 10, 0)] = 3  # 协商后达成一致 (9条)
    ct[('dkoekgf5', 11, 0)] = 3  # 三方各陈述偏好 (50/60/70) 后折中于60% (9条)
    ct[('dkoekgf5', 12, 0)] = 1  # 快速一致同意保守方案A (4条)

    # --- 0f9u4oto ---
    ct[('0f9u4oto', 11, 0)] = 1  # P1提议投票，快速一致 (9条)
    ct[('0f9u4oto', 12, 0)] = 3  # P2提议中间方案，快速同意 (6条)

    # --- 8kn3iz3d ---
    ct[('8kn3iz3d', 7, 0)] = 5   # P3主导提议50/50，P1+P2适应 (16条)

    # --- 6apbq166 ---
    ct[('6apbq166', 13, 0)] = 4  # P1指出已有majority，P3表示无所谓 (6条)
    ct[('6apbq166', 14, 0)] = 3  # 协商后折中于P1中间方案 (7条)

    # --- thex540s ---
    ct[('thex540s', 13, 0)] = 4  # P3指出已有majority，快速一致 (6条)
    ct[('thex540s', 14, 0)] = 3  # 详细辩论后折中于P1 (21条)

    # --- moe0awio ---
    ct[('moe0awio', 15, 0)] = 1  # 快速一致 (2条)
    ct[('moe0awio', 16, 0)] = 2  # P1数学论证主导，P2+P3同意 (5条)
    ct[('moe0awio', 17, 0)] = 3  # 激烈辩论 "go big or go home" vs 保守，最终多数投票2v1 (27条)

    # --- l1u9ytue ---
    ct[('l1u9ytue', 15, 0)] = 1  # 快速一致同意P2 (6条)
    ct[('l1u9ytue', 16, 0)] = 3  # 风险偏好者vs风险厌恶者长时间讨论后折中 (18条)
    ct[('l1u9ytue', 17, 0)] = 1  # 仅1条 "should we agree on proposal 3? it's the middle"

    # --- f0el3eip ---
    ct[('f0el3eip', 18, 0)] = 5  # P1主导主张较少风险，P2论证 (4条)
    ct[('f0el3eip', 19, 0)] = 1  # "no risk no fun" 快速同意 (6条)

    # --- noias7kj ---
    ct[('noias7kj', 18, 0)] = 5  # P1解释立场，P2+P3同意 (7条)
    ct[('noias7kj', 19, 0)] = 2  # P1数学论证主导 (5条)

    # --- c29h9lab ---
    ct[('c29h9lab', 20, 0)] = 3  # 协商后折中于70% (7条)
    ct[('c29h9lab', 21, 0)] = 1  # 快速一致 (3条)
    ct[('c29h9lab', 22, 0)] = 3  # P1推动冒险 vs P2主张保守，长篇辩论后折中 "first 4 A then B" (27条)

    # --- 9uypl6dx ---
    ct[('9uypl6dx', 21, 0)] = 2  # P2用数学论证，P1+P3同意 (12条)

    # --- 32qq2463 ---
    ct[('32qq2463', 22, 0)] = 1  # 快速一致 (3条)

    # --- y1hj2aj2 ---
    ct[('y1hj2aj2', 20, 0)] = 3  # P2主张风险中性 vs P1厌恶损失，讨论后折中 (6条)

    # --- 1gzf7p6u ---
    ct[('1gzf7p6u', 23, 0)] = 1  # 快速一致同意P1或P2 (5条)

    # --- zspnbitg ---
    ct[('zspnbitg', 23, 0)] = 5  # 一人提议A until 7，另一人主张全A (2条)
    ct[('zspnbitg', 24, 0)] = 3  # P1用数学论证，讨论后折中 (10条)

    # --- ymgl8k4i ---
    ct[('ymgl8k4i', 25, 0)] = 6  # P3说 "do what you think it's best"，P1同意 (8条)
    ct[('ymgl8k4i', 26, 0)] = 1  # 快速一致最大化收益 (6条)
    ct[('ymgl8k4i', 27, 0)] = 3  # 协商后折中于60-70% (7条)
    ct[('ymgl8k4i', 28, 0)] = 5  # P2要求P1降低风险 (2条)

    # --- tx1s5v14 ---
    ct[('tx1s5v14', 24, 0)] = 3  # P2提议折中方案 (3条)

    # ==================================================================
    # TR = 1
    # ==================================================================

    # --- bbgfffw6 ---
    ct[('bbgfffw6', 1, 1)] = 2   # P1数学论证，P3提议方案2，快速一致 (14条)
    ct[('bbgfffw6', 2, 1)] = 1   # 快速一致同意方案3 (4条)
    ct[('bbgfffw6', 3, 1)] = 4   # P2+P3倾向方案3，P1适应 (10条)
    ct[('bbgfffw6', 4, 1)] = 1   # 快速一致同意方案2 (4条)
    ct[('bbgfffw6', 5, 1)] = 5   # P3主导识别时间滞后因素，讨论后一致 (7条)

    # --- 6hgrim4b ---
    ct[('6hgrim4b', 1, 1)] = 6   # 仅1条 "why would you wait 4 weeks without 100% certainty?"
    ct[('6hgrim4b', 2, 1)] = 3   # P2+P3推动更多风险/等待，P1反对后适应，长篇讨论 (33条)
    ct[('6hgrim4b', 3, 1)] = 5   # P3质疑P2选择并主导讨论，P1支持P3，P2适应 (19条)

    # --- f8edwq9b ---
    ct[('f8edwq9b', 4, 1)] = 5   # P1主导讨论，P2支持，P3犹豫后同意 (14条)
    ct[('f8edwq9b', 5, 1)] = 3   # P1+P2反对等待 vs P3追求风险，协商后一致 (16条)
    ct[('f8edwq9b', 6, 1)] = 4   # P1推动等待，P3反对等待 (通胀论)，最终适应 (8条)
    ct[('f8edwq9b', 7, 1)] = 1   # P3首先提议，P2同意，快速一致 (10条)
    ct[('f8edwq9b', 8, 1)] = 6   # 仅1条 "weather is nice innit" — 完全离题

    # --- dkoekgf5 ---
    ct[('dkoekgf5', 7, 1)] = 1   # 快速同意参与者2 (6条)
    ct[('dkoekgf5', 8, 1)] = 4   # 快速同意P2 "That's the majority" (6条)
    ct[('dkoekgf5', 9, 1)] = 3   # P1不想等4周，P2提议中间方案，协商 (14条)
    ct[('dkoekgf5', 10, 1)] = 1  # P3基于多数提议，P2同意 (3条)

    # --- 0f9u4oto ---
    ct[('0f9u4oto', 9, 1)] = 3   # P1+P2快速一致中间方案，P3数学论证后同意 (11条)
    ct[('0f9u4oto', 10, 1)] = 1  # 极简对话 (3条)

    # --- 8kn3iz3d ---
    ct[('8kn3iz3d', 6, 1)] = 4   # P3主导指出多数，P1+P2快速同意 (15条)

    # --- 6apbq166 ---
    ct[('6apbq166', 12, 1)] = 3  # 详细讨论后折中于P3方案 (16条)
    ct[('6apbq166', 13, 1)] = 5  # P3坚决反对等待，P1 "whatever" P2 "don't care" (14条)

    # --- thex540s ---
    ct[('thex540s', 11, 1)] = 3  # P3无法到场反对延迟，P1主导讨论后折中 (13条)

    # --- moe0awio ---
    ct[('moe0awio', 12, 1)] = 1  # 快速一致 (4条)
    ct[('moe0awio', 13, 1)] = 5  # P1主导 "4 weeks is quite worse"，P2+P3同意 (10条)
    ct[('moe0awio', 14, 1)] = 4  # P2喜欢大钱，P3不同意后适应，多数投票 (9条)

    # --- l1u9ytue ---
    ct[('l1u9ytue', 14, 1)] = 5  # P2 "don't really care"，P1+P3协商 (11条)
    ct[('l1u9ytue', 15, 1)] = 3  # 协商后折中于选项9 (11条)

    # --- f0el3eip ---
    ct[('f0el3eip', 16, 1)] = 1  # 快速同意方案1 (2条)
    ct[('f0el3eip', 17, 1)] = 3  # P1提议P2，P2数学论证，P3不愿等 (6条)

    # --- noias7kj ---
    ct[('noias7kj', 15, 1)] = 1  # P1觉得4周长，快速一致P1 (4条)
    ct[('noias7kj', 16, 1)] = 1  # P1无法到场，P3同意 (3条)

    # --- c29h9lab ---
    ct[('c29h9lab', 18, 1)] = 3  # 讨论时间偏好，折中于90% (16条)
    ct[('c29h9lab', 19, 1)] = 1  # 一致同意P2 (2条)
    ct[('c29h9lab', 20, 1)] = 1  # 轻松讨论 "democracy"，快速一致 (19条)

    # --- 9uypl6dx ---
    ct[('9uypl6dx', 18, 1)] = 3  # P1提问主导，P2担心取钱时间，协商后一致 (13条)

    # --- 32qq2463 ---
    ct[('32qq2463', 19, 1)] = 3  # P2推动冒险方案 vs P1反对风险+等待 (9条)

    # --- y1hj2aj2 ---
    ct[('y1hj2aj2', 17, 1)] = 1  # P2主张等待 vs P1质疑，快速一致P1 (5条)

    # --- 1gzf7p6u ---
    ct[('1gzf7p6u', 21, 1)] = 3  # P2提议折中 "1 would be a good compromise" (3条)

    # --- zspnbitg ---
    ct[('zspnbitg', 20, 1)] = 5  # P1想明天拿钱，P3主导讨论，P2适应 (6条)

    # --- ymgl8k4i ---
    ct[('ymgl8k4i', 22, 1)] = 1  # 快速同意 (2条)
    ct[('ymgl8k4i', 23, 1)] = 1  # 快速一致选择3 (6条)
    ct[('ymgl8k4i', 24, 1)] = 4  # P1主张立场，P3适应 (5条)

    # --- vfgv3mdk ---
    ct[('vfgv3mdk', 11, 1)] = 5  # P1坚决不等待，P2+P3接受 (4条)

    return ct


def apply_chat_type_classification():
    """
    主函数：加载数据 → 构建分类 → 映射到 dataset2026 → 输出
    """
    print("=" * 60)
    print("Chat Type Classification — 6 Types")
    print("=" * 60)

    msg = pd.read_excel(MESSAGE_FILE)
    ds = pd.read_excel(DATASET_FILE)

    ct = build_chat_type_classification()

    # Build msg_group bridges
    for tr in [0, 1]:
        tr_msg = msg[msg['time_risk'] == tr]
        bridge = tr_msg[['participant_code', 'session_code', 'group']] \
                 .drop_duplicates()
        bridge.columns = ['subject_code', 'session_code', f'g{tr}']
        ds = ds.merge(bridge, on=['subject_code', 'session_code'], how='left')

    # Apply classification
    for tr in [0, 1]:
        col = f'chat_type{tr+1}'
        ds[col] = pd.NA

        for idx, row in ds.iterrows():
            g = row[f'g{tr}']
            if pd.notna(g):
                key = (row['session_code'], int(g), tr)
                if key in ct:
                    ds.at[idx, col] = ct[key]

        ds[col] = ds[col].astype('Int64')

    # Clean up temp columns
    for tr in [0, 1]:
        ds = ds.drop(columns=[f'g{tr}'])

    # Save
    ds.to_excel(OUTPUT_FILE, index=False)

    # Report
    print(f"\n共有 {len(ct)} 个组 × time_risk 分类")
    for tr in [0, 1]:
        col = f'chat_type{tr+1}'
        print(f"\n{'=' * 60}")
        print(f"TR={tr}  ({col}):")
        print(f"{'=' * 60}")
        vc = ds[col].value_counts().sort_index()
        for k, v in vc.items():
            print(f"  {TYPE_LABELS.get(int(k), k)}: {v}")
        print(f"  NaN (无该TR聊天数据): {ds[col].isna().sum()}")

    print(f"\n结果已保存至: {OUTPUT_FILE}")
    print("程序执行完毕。")
    return ds


if __name__ == '__main__':
    ds = apply_chat_type_classification()
