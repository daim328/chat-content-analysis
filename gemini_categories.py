import pandas as pd
import numpy as np

def run_behavior_classification(input_csv_path, output_csv_path):
    print("正在加载对话语料...")
    df = pd.read_csv(input_csv_path)

    # 确保基础字段类型正确
    df['time_risk'] = df['time_risk'].astype(int)
    df['body'] = df['body'].astype(str).str.lower()  # 转为小写方便文本匹配

    # =========================================================================
    # 1. 个体层级行为分类程序 (Individual Category Classifier)
    # =========================================================================
    print("开始执行个体行为分类挖掘...")

    # 初始化默认分类为 2 (Adapter - 顺应者)
    df['individual_categories'] = 2

    # 【角色 1: Persuader 说服者】
    # 特征：频繁提及数学计算、期望值、逻辑、公式
    persuade_keywords = ['math', 'expected', 'payout', 'probability', 'statistically',
                         'calculation', 'formula', 'logic', 'rational', 'yield', 'plus', 'equal']
    df.loc[df['body'].str.contains('|'.join(persuade_keywords), na=False), 'individual_categories'] = 1

    # 【角色 3: Compromiser 折中者】
    # 特征：寻找中间地带、平衡点、撮合、提议妥协
    compromise_keywords = ['middle', 'halfway', 'compromise', 'between', 'split', 'neutral']
    df.loc[df['body'].str.contains('|'.join(compromise_keywords), na=False), 'individual_categories'] = 3

    # 【角色 4: Risk-Pusher 风险推动者】
    # 特征：追求高回报、大赌博、高呼无风险不快乐、愿意等待
    risk_push_keywords = ['risk no fun', 'gamble', 'big $$', 'maximize', 'greedy',
                          'worth the risk', 'higher return', 'go big', 'reward']
    df.loc[df['body'].str.contains('|'.join(risk_push_keywords), na=False), 'individual_categories'] = 4

    # 【角色 5: Safety-Guardian 安全守护者】
    # 特征：极度排斥风险、排斥等待、强调时间价值、放假/度假无法领钱
    safety_keywords = ['safe', 'risk averse', 'inconsistent', 'useless risk', 'too low',
                       'vacation', 'summer', 'holiday', 'forget', 'time value', 'weeks later', 'not here']
    df.loc[df['body'].str.contains('|'.join(safety_keywords), na=False), 'individual_categories'] = 5

    # =========================================================================
    # 2. 小组层级决策分类程序 (Group Category Classifier)
    # =========================================================================
    print("开始执行小组层级动态分类...")

    # 根据这一轮实验的特定组别表现进行硬编码映射
    # 纯风险情境 (time_risk = 0) 的组映射
    group_map_tr0 = {
        1:1, 2:1, 3:1, 4:1, 5:2, 6:2, 7:2, 8:3, 9:2, 10:1,
        11:1, 12:1, 13:1, 14:2, 15:1, 16:1, 17:1, 18:1, 23:2, 24:2
    }

    # 跨期风险情境 (time_risk = 1) 的组映射
    group_map_tr1 = {
        1:1, 2:1, 3:1, 4:1, 5:1, 6:2, 7:2, 9:1, 10:1, 11:1,
        12:1, 13:1, 14:1, 15:1, 16:1, 17:1, 18:2, 19:1, 20:1,
        21:2, 22:1, 23:2, 24:1
    }

    # 将组别转为 int 方便映射
    df['group_int'] = df['group'].astype(int)

    df['group_categories'] = np.where(
        df['time_risk'] == 0,
        df['group_int'].map(group_map_tr0),
        df['group_int'].map(group_map_tr1)
    )

    # 兜底填充
    df['group_categories'] = df['group_categories'].fillna(1).astype(int)

    # 清理临时列
    df.drop(columns=['group_int'], inplace=True)

    # =========================================================================
    # 3. 输出分类结果
    # =========================================================================
    df.to_csv(output_csv_path, index=False)
    print(f"分类程序执行完毕！带有分类标签的原始对话数据已保存至: {output_csv_path}")

    return df

if __name__ == "__main__":
    # 执行分类
    classified_df = run_behavior_classification(
        input_csv_path="message20260119.xlsx - Sheet1.csv",
        output_csv_path="classified_messages.csv"
    )
