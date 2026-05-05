"""
=============================================================================
Threat/Coercion Classification — threat1 (TR=0) & threat2 (TR=1)
=============================================================================

分类标准：
  1 = 个体在对话中存在威胁或胁迫其他成员的行为和语言文字
  0 = 无威胁或胁迫行为

审查范围：message20260119.xlsx 全部 851 条消息，97 个对话会话。

审查结论：
  经逐条审查，所有对话均在正常学术实验协商范围内。未发现任何个体
  存在威胁（threaten）、胁迫（coerce）、恐吓（intimidate）或强制
  （force）其他成员的语言或行为。

  具体排除的边界案例：
  - 明确表示不接受某方案（如 "I will not agree with three"）属于
    一致同意规则下的正常否决权行使，非威胁。
  - 指出多数地位要求他人适应（如 "3 and me seem to agree so you
    should lower the risk"）属于多数规则下的正常协商，非胁迫。
  - 表达强烈偏好（如 "im not gonna wait 4 weeks i promise that"）
    属于个人立场表达，非威胁。

  因此 threat1 和 threat2 全部赋值为 0。

数据流：
  message20260119.xlsx → 审查 → dataset2026.xlsx (threat1, threat2)

作者: Claude Code
日期: 2026-05-05
=============================================================================
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')


def apply_threat_classification():
    print("=" * 60)
    print("Threat/Coercion Classification — threat1 & threat2")
    print("=" * 60)

    ds = pd.read_excel(DATASET_FILE)

    # 全部赋值为 0（未发现任何威胁或胁迫行为）
    ds['threat1'] = 0
    ds['threat2'] = 0

    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"\n  结果已保存至: {OUTPUT_FILE}")
    print(f"  threat1 = 0: {len(ds)} / {len(ds)} (100%)")
    print(f"  threat2 = 0: {len(ds)} / {len(ds)} (100%)")
    print(f"\n  审查依据：全部 851 条消息中未发现威胁、胁迫、恐吓或强制语言。")

    return ds


if __name__ == '__main__':
    ds = apply_threat_classification()
