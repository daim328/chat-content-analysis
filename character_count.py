"""
=============================================================================
Character Count — character1 (TR=0) & character2 (TR=1)
=============================================================================

统计每位参与者在 time_risk=0 和 time_risk=1 两种情形下发出的所有消息的
总字符数量。

数据流：
  message20260119.xlsx → 按 participant_code × time_risk 汇总字符数
  → 写入 dataset2026.xlsx (character1, character2)

作者: Claude Code
日期: 2026-05-05
=============================================================================
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_FILE = os.path.join(BASE_DIR, 'message20260119.xlsx')
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')


def count_characters():
    print("=" * 60)
    print("Character Count — character1 & character2")
    print("=" * 60)

    # 加载数据
    print("\n[1/3] 加载数据...")
    msg = pd.read_excel(MESSAGE_FILE)
    ds = pd.read_excel(DATASET_FILE)
    print(f"  消息数据: {msg.shape[0]} 条消息, {msg['participant_code'].nunique()} 个参与者")
    print(f"  数据集:   {ds.shape[0]} 行")

    # 计算每条消息的字符数
    print("\n[2/3] 计算字符数...")
    msg['char_count'] = msg['body'].astype(str).str.len()

    # 按 participant_code × time_risk 汇总
    chars = msg.groupby(['participant_code', 'time_risk'])['char_count'] \
               .sum().unstack(fill_value=0)
    chars.columns = ['character1', 'character2']  # 0 → TR=0, 1 → TR=1
    chars = chars.reset_index()
    chars.columns = ['subject_code', 'character1', 'character2']

    # 合并到 dataset
    ds = ds.merge(chars, on='subject_code', how='left')
    ds['character1'] = ds['character1'].fillna(0).astype(int)
    ds['character2'] = ds['character2'].fillna(0).astype(int)

    # 保存
    print("\n[3/3] 保存结果...")
    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"  结果已保存至: {OUTPUT_FILE}")

    # 统计摘要
    print("\n" + "=" * 60)
    print("统计摘要")
    print("=" * 60)
    for col, label in [('character1', 'TR=0'), ('character2', 'TR=1')]:
        print(f"\n{label} ({col}):")
        print(f"  均值:    {ds[col].mean():.1f}")
        print(f"  中位数:  {ds[col].median():.0f}")
        print(f"  标准差:  {ds[col].std():.1f}")
        print(f"  最小值:  {ds[col].min():.0f}")
        print(f"  最大值:  {ds[col].max():.0f}")
        print(f"  为 0:    {(ds[col] == 0).sum()} 人")

    return ds


if __name__ == '__main__':
    ds = count_characters()
