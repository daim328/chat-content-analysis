"""
=============================================================================
AFINN Sentiment Analysis — sentiment1 (TR=0) & sentiment2 (TR=1)
=============================================================================

使用 AFINN 情感词典 (Nielsen, 2011) 度量每位参与者在 time_risk=0 和
time_risk=1 两种情形下的平均情感指数。

AFINN 词典为单词赋予 -5 到 +5 的分数：
  - 正值 = 积极情感（正面词汇、赞同、讨论积极方面）
  - 负值 = 消极情感
  - 0    = 中性

计算方式：
  1. 对每条消息进行分词
  2. 查找每个词在 AFINN 词典中的分数
  3. 对每位 participant × time_risk 的所有消息取平均分
  4. 无消息的参与者记为 NaN

数据流：
  message20260119.xlsx → AFINN 分词打分 → 按人平均 → dataset2026.xlsx

参考: Nielsen, F. Å. (2011). A new ANEW: Evaluation of a word list for
      sentiment analysis in microblogs. Proceedings of the ESWC2011 Workshop
      on 'Making Sense of Microposts'.

作者: Claude Code
日期: 2026-05-05
=============================================================================
"""

import pandas as pd
import numpy as np
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_FILE = os.path.join(BASE_DIR, 'message20260119.xlsx')
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')


def load_afinn():
    """加载 AFINN-111 情感词典 (Nielsen, 2011)"""
    from afinn import Afinn
    afinn = Afinn()
    return afinn


def tokenize(text):
    """简单分词：按非字母字符分割，转小写"""
    if pd.isna(text) or not isinstance(text, str):
        return []
    return re.findall(r"[a-zA-Z']+", text.lower())


def compute_sentiment(text, afinn):
    """计算单条消息的 AFINN 情感总分"""
    if not text or not isinstance(text, str) or text.strip() == '':
        return np.nan
    score = afinn.score(text)
    return score


def apply_sentiment_analysis():
    print("=" * 60)
    print("AFINN Sentiment Analysis — sentiment1 & sentiment2")
    print("=" * 60)

    # 加载数据
    print("\n[1/4] 加载数据...")
    msg = pd.read_excel(MESSAGE_FILE)
    ds = pd.read_excel(DATASET_FILE)
    print(f"  消息数据: {msg.shape[0]} 条消息, {msg['participant_code'].nunique()} 个参与者")
    print(f"  数据集:   {ds.shape[0]} 行")

    # 加载 AFINN
    print("\n[2/4] 加载 AFINN 情感词典...")
    afinn = load_afinn()
    print("  AFINN 词典已就绪")

    # 计算每条消息的情感分数
    print("\n[3/4] 计算情感分数...")
    msg['sentiment_score'] = msg['body'].apply(lambda x: compute_sentiment(x, afinn))

    # 按 participant_code × time_risk 计算平均情感分
    sent = msg.groupby(['participant_code', 'time_risk'])['sentiment_score'] \
              .mean().unstack()
    sent.columns = ['sentiment1', 'sentiment2']  # 0 → TR=0, 1 → TR=1
    sent = sent.reset_index()
    sent.columns = ['subject_code', 'sentiment1', 'sentiment2']

    # 合并到 dataset
    ds = ds.merge(sent, on='subject_code', how='left')
    # 确保无消息者为 NaN（已在 groupby mean 中处理）

    # 保存
    print("\n[4/4] 保存结果...")
    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"  结果已保存至: {OUTPUT_FILE}")

    # 统计摘要
    print("\n" + "=" * 60)
    print("统计摘要")
    print("=" * 60)

    for col, label in [('sentiment1', 'TR=0'), ('sentiment2', 'TR=1')]:
        valid = ds[col].dropna()
        print(f"\n{label} ({col}):")
        print(f"  有效值:  {len(valid)} / {len(ds)}")
        print(f"  均值:    {valid.mean():.3f}")
        print(f"  中位数:  {valid.median():.3f}")
        print(f"  标准差:  {valid.std():.3f}")
        print(f"  最小值:  {valid.min():.3f}")
        print(f"  最大值:  {valid.max():.3f}")

    # 极端值
    print("\n--- sentiment1 最高/最低 ---")
    top5 = ds.nlargest(5, 'sentiment1')[['subject_code', 'sentiment1']].dropna()
    bot5 = ds.nsmallest(5, 'sentiment1')[['subject_code', 'sentiment1']].dropna()
    print("  Top 5 (最积极):")
    for _, row in top5.iterrows():
        print(f"    {row['subject_code']}: {row['sentiment1']:.3f}")
    print("  Bottom 5 (最消极):")
    for _, row in bot5.iterrows():
        print(f"    {row['subject_code']}: {row['sentiment1']:.3f}")

    print("\n--- sentiment2 最高/最低 ---")
    top5 = ds.nlargest(5, 'sentiment2')[['subject_code', 'sentiment2']].dropna()
    bot5 = ds.nsmallest(5, 'sentiment2')[['subject_code', 'sentiment2']].dropna()
    print("  Top 5 (最积极):")
    for _, row in top5.iterrows():
        print(f"    {row['subject_code']}: {row['sentiment2']:.3f}")
    print("  Bottom 5 (最消极):")
    for _, row in bot5.iterrows():
        print(f"    {row['subject_code']}: {row['sentiment2']:.3f}")

    return ds


if __name__ == '__main__':
    ds = apply_sentiment_analysis()
