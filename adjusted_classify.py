"""
=============================================================================
Adjusted Classification — 结合投票数据与聊天内容重新分类
=============================================================================

根据 category standards2 文件，结合 dataset2026 的个人投票数据
（i_risk / i_time_risk / final_risk / final_time_risk）和
message20260119 的文本对话内容，对小组（group）和个体成员（participant）
进行重新分类。

分类标准 (category standards2):
  Group:
    G1 多数原则: 两名成员偏好相同；第三名成员适应。
    G2 折中: 经过协商后，在初始选择之间达成中间方案。
    G3 少数驱动: 在他人不服从或冷漠的情况下，由单一个体做出决策。
    (G4 已移除)

  Individual:
    I1 冷漠: 拒绝参与讨论，或表示自己不在乎。
    I2 愿意适应: 自愿或在被要求时调整自己的不同决定。
    I3 要求他人适应: 明确要求他人调整自己不同的决定。
    I4 要求风险或延迟风险: 明确要求他人做出更具风险或延迟的决定。
    I5 接受风险或延迟风险: 接受并执行风险或延迟风险的要求。
    I6 要求更少延迟风险: 明确要求他人做出风险更低或延迟更短的决定。
    I7 接受更多延迟风险: 接受并执行更多延迟风险的要求。

调整规则:
  1. 聊天分类为基础（来自 classify_results.py + 后续手动修正）
  2. 投票数据填补缺失值（NaN → 基于投票模式分类）
  3. 投票数据修正明显矛盾：
     - Unanimous 初始投票 → G1（无需折中）
     - All-diff + 多轮投票 → G2（需要协商）
     - I3 + 投票已适应 → I2（实际是适应者）
     - I2 + 坚持立场并胜出 → I3（实际是主导者）

输出:
  group_categories1_adjusted  (TR=0)
  group_categories2_adjusted  (TR=1)
  individual_categories1_adjusted (TR=0)
  individual_categories2_adjusted (TR=1)

数据流:
  message20260119.xlsx + dataset2026.xlsx 投票数据
  → category standards2 标准
  → dataset2026.xlsx (4 个新 adjusted 变量)

作者: Claude Code
日期: 2026-05-14
=============================================================================
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')


def build_adjusted_classification():
    """
    主函数：加载数据 → 结合投票+聊天分类 → 创建 adjusted 变量 → 输出
    """
    print("=" * 60)
    print("Adjusted Classification — Voting + Chat Combined")
    print("=" * 60)

    ds = pd.read_excel(DATASET_FILE)
    changes_log = []

    for tr in [0, 1]:
        i_col = f'i{"" if tr == 0 else "_time"}_risk'
        f_col = f'final{"" if tr == 0 else "_time"}_risk'
        v_col = f'{"risk" if tr == 0 else "time_risk"}_vote1'
        r_col = f'round{tr+1}'
        g_exist = f'group_categories{tr+1}'
        i_exist = f'individual_categories{tr+1}'
        g_adj = f'group_categories{tr+1}_adjusted'
        i_adj = f'individual_categories{tr+1}_adjusted'

        # --- Step 1: Build group-level voting summary ---
        grp = ds.groupby('group1').agg(
            p1_i=(i_col, lambda x: x.iloc[0] if len(x) > 0 else np.nan),
            p2_i=(i_col, lambda x: x.iloc[1] if len(x) > 1 else np.nan),
            p3_i=(i_col, lambda x: x.iloc[2] if len(x) > 2 else np.nan),
            p1_s=('subject_code', lambda x: x.iloc[0]),
            p2_s=('subject_code', lambda x: x.iloc[1] if len(x) > 1 else ''),
            p3_s=('subject_code', lambda x: x.iloc[2] if len(x) > 2 else ''),
            final=(f_col, 'first'),
            winner=(v_col, 'first'),
            rounds=(r_col, 'first'),
            g_exist=(g_exist, lambda x: x.iloc[0] if len(x) > 0 and pd.notna(x.iloc[0]) else np.nan),
        ).reset_index()

        # --- Step 2: Determine initial voting pattern ---
        def get_init_pattern(r):
            vals = {r.p1_i, r.p2_i, r.p3_i} - {np.nan}
            if len(vals) == 1:
                return 'unanimous'
            if len(vals) == 2:
                return 'majority'
            if len(vals) == 3:
                return 'all_diff'
            return 'unknown'

        grp['pattern'] = grp.apply(get_init_pattern, axis=1)

        # --- Step 3: Adjusted GROUP classification ---
        grp['adj_g'] = grp['g_exist'].copy()
        for idx, r in grp.iterrows():
            if pd.isna(r['g_exist']):
                # Fill NaN from voting
                if r['pattern'] == 'majority':
                    grp.at[idx, 'adj_g'] = 1
                elif r['pattern'] == 'all_diff':
                    grp.at[idx, 'adj_g'] = 2
                else:
                    grp.at[idx, 'adj_g'] = 1
            elif r['pattern'] == 'unanimous' and r['g_exist'] == 2:
                grp.at[idx, 'adj_g'] = 1
                changes_log.append(
                    f"TR{tr} group1={int(r['group1'])}: G2→G1 (unanimous votes)"
                )
            elif r['pattern'] == 'all_diff' and r['g_exist'] == 1 and r['rounds'] >= 2:
                grp.at[idx, 'adj_g'] = 2
                changes_log.append(
                    f"TR{tr} group1={int(r['group1'])}: G1→G2 (all_diff + 2 rounds)"
                )

        # Map group classification to subjects
        subj_g_map = {}
        for _, r in grp.iterrows():
            for p in [1, 2, 3]:
                s = r[f'p{p}_s']
                if s:
                    subj_g_map[s] = r['adj_g']

        # --- Step 4: Adjusted INDIVIDUAL classification ---
        subj_i_map = {}
        for _, r in grp.iterrows():
            for p_idx, p in enumerate([1, 2, 3]):
                s = r[f'p{p}_s']
                if not s:
                    continue

                i_val_rows = ds.loc[ds['subject_code'] == s, i_exist].values
                i_val = i_val_rows[0] if len(i_val_rows) > 0 else np.nan

                adapted = r[f'p{p}_i'] != r['final']
                winner = r['winner'] == p

                if pd.isna(i_val):
                    # Fill NaN from voting
                    if adapted:
                        i_val = 2
                    elif winner:
                        i_val = 3
                    else:
                        i_val = 2
                elif i_val == 3 and adapted and r['pattern'] == 'majority':
                    i_val = 2
                    changes_log.append(
                        f"TR{tr} {s}: I3→I2 (adapted vote in majority)"
                    )
                elif i_val == 2 and not adapted and winner:
                    i_val = 3
                    changes_log.append(
                        f"TR{tr} {s}: I2→I3 (held position + won)"
                    )

                subj_i_map[s] = int(i_val) if pd.notna(i_val) else np.nan

        # --- Step 5: Apply to dataset ---
        ds[g_adj] = ds['subject_code'].map(subj_g_map).astype('Int64')
        ds[i_adj] = ds['subject_code'].map(subj_i_map).astype('Int64')

        # --- Report ---
        g_na = ds[g_exist].isna().sum()
        i_na = ds[i_exist].isna().sum()
        g_changed = (ds[g_adj] != ds[g_exist]).sum()
        i_changed = (ds[i_adj] != ds[i_exist]).sum()

        print(f"\n{'=' * 60}")
        print(f"TR={tr}")
        print(f"{'=' * 60}")
        print(f"  Group:   NaN filled={g_na}, total changed={g_changed}")
        print(f"  Indiv:   NaN filled={i_na}, total changed={i_changed}")
        print(f"  Group adjusted:   {dict(sorted(ds[g_adj].value_counts().items()))}")
        print(f"  Indiv adjusted:   {dict(sorted(ds[i_adj].value_counts().items()))}")

    # --- Final summary ---
    print(f"\n{'=' * 60}")
    print(f"调整记录 ({len(changes_log)} 条):")
    for c in changes_log:
        print(f"  {c}")

    # --- Save ---
    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"\n结果已保存至: {OUTPUT_FILE}")
    print(f"程序执行完毕。")

    return ds


if __name__ == '__main__':
    ds = build_adjusted_classification()
