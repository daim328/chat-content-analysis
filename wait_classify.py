"""
=============================================================================
Wait Attitude Classification — wait1 (TR=0) & wait2 (TR=1)
=============================================================================

分类标准：
   1 = 不喜欢等待4周，如 "I cannot wait for 4 weeks", "4 weeks are too long",
       "I do not like 4 weeks", "I only want to get the money tomorrow" 等
   0 = 所有消息与延迟/4周无关，或没有表达对等待的好恶
  -1 = 愿意等待4周，如 "I want to wait 4 weeks", "4 weeks can be acceptable",
       "I want bigger profits" 等

数据流：
  message20260119.xlsx → 逐参与人 × time_risk 审查 → 映射到 dataset2026.xlsx

作者: Claude Code
日期: 2026-05-05
=============================================================================
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_FILE = os.path.join(BASE_DIR, 'message20260119.xlsx')
DATASET_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, 'dataset2026.xlsx')


def build_wait_classification():
    """
    返回字典: W[participant_code][time_risk] = -1, 0, or 1

    基于对 message20260119.xlsx 中全部 851 条消息的逐条审查。
    搜索关键词：4 week, four week, wait, tomorrow, delay, collect, pick up,
    abholen, warten, morgen 等。

    time_risk=0 为纯风险决策（无延迟），因此绝大多数参与人为 0。
    time_risk=1 为延迟风险决策，存在对等待4周的态度表达。
    """
    W = {}

    # =========================================================================
    # TIME_RISK = 0 (纯风险决策)
    # 此条件下不存在延迟因素，因此几乎所有参与人应得 0。
    # 仅一人例外：wntam0iz 在 TR=0 对话中明确表达了不愿等待。
    # =========================================================================

    # wntam0iz: "i dont want to wait 4 weeks :(" → 明确不喜欢等待
    W['wntam0iz'] = {0: 1, 1: None}

    # 其他在 TR=0 中提到 "tomorrow" / "wait" 但属于中性陈述的：
    # wtuk7z9j: "We receive all rewards tomorrow, so thats no variable..." → 0（陈述事实）
    # 04ybbykm (TR=0): "we will get 12 points tomorrow" → 0（陈述事实）
    # p8s0es6v: "if it's all the payoff we can get tomorrow" → 0（陈述事实）
    # obs7t4q0 (TR=0): "ah wait i mean 1*" → 0（"wait" 作为口头禅，非等待4周）
    # 2ye352y6 (TR=0): "I wonder what they're waiting for" → 0（等待实验进程，非4周）

    # =========================================================================
    # TIME_RISK = 1 (延迟风险决策)
    # 按 session 逐一审查所有 TR=1 对话中的等待态度表达。
    # =========================================================================

    # --- session: 6hgrim4b (majority=1) ---

    # o81zm9mi (Group 1, maj=1): "why would you wait 4 weeks without a 100%
    #   certainty?" → 质疑等待的价值，不喜欢等待
    W['o81zm9mi'] = {0: None, 1: 1}

    # epbcekix (Group 2, maj=1): "Do we think it is worth waiting 4 weeks..."
    #   "i wouldn't wait for 4 weeks to get additional points"
    #   明确表示不愿等待4周 → 1
    W['epbcekix'] = {0: None, 1: 1}

    # b1ljp7hw (Group 2, maj=1): "waiting doesn't influence anything else"
    #   "with probability of 80 and 90% it's worthwhile to wait"
    #   "80% is a lot tho" → 认为值得等待 → -1
    W['b1ljp7hw'] = {0: None, 1: -1}

    # n6gyc5p4 (Group 2, maj=1): "waiting is the whole point i guess"
    #   "8,9,10 would be worth it" → 愿意为更高收益等待 → -1
    W['n6gyc5p4'] = {0: None, 1: -1}

    # wbyf9v3z (Group 3, maj=1): "if someone needs to endure 4 weeks..."
    #   "I think we should at least enjoy the more tradeoff"
    #   分析性讨论，没有明确表达对等待的好恶，最终同意他人 → 0
    W['wbyf9v3z'] = {0: None, 1: 0}

    # h711c9j8 (Group 3, maj=1): "I also don't really want to have to come
    #   back again to collect my money in 4 weeks"
    #   "I would also agree with Participant1 choice to collect the money
    #   earlier, even if it might be less" → 不喜欢等待 → 1
    W['h711c9j8'] = {0: None, 1: 1}

    # ehz7bo8w (Group 3, maj=1): "hi", "okay", "i can settle for what you
    #   guys are saying" → 未表达对等待的态度 → 0
    W['ehz7bo8w'] = {0: None, 1: 0}

    # --- session: f8edwq9b (majority=1) ---

    # ads1z9m5 (Group 5, maj=1): "since i am not sure if i can be here in
    #   4 weeks i prefer the option from participant 1" → 不喜欢等待 → 1
    W['ads1z9m5'] = {0: None, 1: 1}

    # dn7y6gxh (Group 5, maj=1): "P3 why do you want to wait so long for
    #   2 euros" / "and imagine you get unlucky and get 2 euros lol"
    #   → 质疑等待的价值 → 1
    W['dn7y6gxh'] = {0: None, 1: 1}

    # g4fja7tj (Group 5, maj=1): "youre not taking risks haha"
    #   "well lets choose yellow" → 未直接提及等待 → 0
    W['g4fja7tj'] = {0: None, 1: 0}

    # 890ews6l (Group 6, maj=1): "why does it matter if you get it tomorrow
    #   or in 4 weeks" / "but the time gone by, doesn't make the money less
    #   valuable does it?" / "within one month??"
    #   → 质疑不等待的观点，认为等待无所谓 → -1
    W['890ews6l'] = {0: None, 1: -1}

    # zlh5tdu5 (Group 6, maj=1): "waiting a month for 4 is not a good deal"
    #   "inflation lol?" / "ehh anyway" / "then lets go with yours"
    #   → 不喜欢等待，但最终适应 → 1
    W['zlh5tdu5'] = {0: None, 1: 1}

    # 4ecrweb0 (Group 7, maj=1): "the 4 weeks dont really matter i think"
    #   → 中立 → 0
    W['4ecrweb0'] = {0: None, 1: 0}

    # 0vm3ban9 (Group 7, maj=1): "i would go with participant 2"
    #   "it makes sense" → 未直接提及等待 → 0
    W['0vm3ban9'] = {0: None, 1: 0}

    # j1umjk3z (Group 7, maj=1): "hi", "ok", "yeah" → 未提及等待 → 0
    W['j1umjk3z'] = {0: None, 1: 0}

    # 671jyleo (Group 8, maj=1): "hi" / "weather is nice innit"
    #   → 完全离题，未提及等待 → 0
    W['671jyleo'] = {0: None, 1: 0}

    # qsx3cu9b (Group 4, maj=1): "deutsch or english", "p1 and p2 are identical"
    #   → 未提及等待 → 0
    W['qsx3cu9b'] = {0: None, 1: 0}

    # ne9tcre6 (Group 4, maj=1): "english", "i would vote for p1" → 0
    W['ne9tcre6'] = {0: None, 1: 0}

    # hvrtd05u (Group 4, maj=1): "egal", "ok", "yes" → 0
    W['hvrtd05u'] = {0: None, 1: 0}

    # --- session: thex540s (majority=1) ---

    # gbqvph97 (Group 11, maj=1): "I will not be here in 4 weeks, will you?"
    #   "normally, it does not matter, and I am fine in 4 weeks, but I cannot
    #   pick it up" → 无法到场取钱，不喜欢等待 → 1
    W['gbqvph97'] = {0: None, 1: 1}

    # gpfru5fz (Group 11, maj=1): "why does it matter when you get the money?"
    #   "yes i will, but you will have the chance i think to fetch it
    #   afterwards" / "im now for 2 proposal"
    #   → 起初质疑，后转为适应他人（不等待方案）。态度中立偏适应 → 0
    W['gpfru5fz'] = {0: None, 1: 0}

    # 2m2gvym1 (Group 11, maj=1): "just with 100 percent it would be make
    #   sense to wait" / "other wise after 4 weeks and earn 4 point it is
    #   not make sence for me at least" → 不愿等待（除非100%） → 1
    W['2m2gvym1'] = {0: None, 1: 1}

    # --- session: moe0awio (majority=1) ---

    # 4dd8h4bq (Group 13, maj=1): "but if you guys want the money tomorrow
    #   thats fine with me" → 灵活，中立 → 0
    W['4dd8h4bq'] = {0: None, 1: 0}

    # ctxmjlm2 (Group 13, maj=1): "I think getting it four weeks from now is
    #   quite worse, I dont know if I will be gone by then"
    #   → 不喜欢等待 → 1
    W['ctxmjlm2'] = {0: None, 1: 1}

    # f1g62gra (Group 13, maj=1): "I think mathematically, we can choose
    #   participant 1" / "Both are fine with me though" → 未提及等待 → 0
    W['f1g62gra'] = {0: None, 1: 0}

    # 5m6eokuf (Group 14, maj=1): "we more or less agree" / "i like big $$"
    #   → 未直接提及等待，关注收益 → 0
    W['5m6eokuf'] = {0: None, 1: 0}

    # ll6dsdgb (Group 14, maj=1): "i don't agree with proposal 1" / "perfect"
    #   → 未提及等待 → 0
    W['ll6dsdgb'] = {0: None, 1: 0}

    # w7a8aaj0 (Group 14, maj=1): "already voted" → 0
    W['w7a8aaj0'] = {0: None, 1: 0}

    # fpqmm059 (Group 12, maj=1): "Hey :) i'm fine with your proposals" → 0
    W['fpqmm059'] = {0: None, 1: 0}

    # 5wc937fh (Group 12, maj=1): "Hey! Can we agree on the proposal 1?"
    #   → 未提及等待 → 0
    W['5wc937fh'] = {0: None, 1: 0}

    # 9l5zm41p (Group 12, maj=1): "Wonderful" → 0
    W['9l5zm41p'] = {0: None, 1: 0}

    # --- session: noias7kj (majority=1) ---

    # jqul0rpn (Group 15, maj=1): "I find 4 Weeks a lot of time :)"
    #   → 不喜欢等待 → 1
    W['jqul0rpn'] = {0: None, 1: 1}

    # ho43nz77 (Group 15, maj=1): "sounds good" → 0
    W['ho43nz77'] = {0: None, 1: 0}

    # f5fsh83e (Group 15, maj=1): "okay not 2. gummi bear for you"
    #   "lets pick participant 1 to make this quick"
    #   → 想快速决策（高效），但未明确提及等待4周 → 0
    W['f5fsh83e'] = {0: None, 1: 0}

    # rhhck5ce (Group 16, maj=1): "I wont be in Heidelberg in four weeks"
    #   → 无法等待（地点限制） → 1
    W['rhhck5ce'] = {0: None, 1: 1}

    # b4scyfme (Group 16, maj=1): "ok sure" → 0
    W['b4scyfme'] = {0: None, 1: 0}

    # --- session: 9uypl6dx (majority=1) ---

    # bjlkg2c6 (Group 18, maj=1): "so participant 2, for you its important
    #   to get the money tomorrow?" / "without having to wait 4 weeks"
    #   "yes, they leave it in the office, you can come also in a couple of
    #   months" → 提问并澄清，态度中立 → 0
    W['bjlkg2c6'] = {0: None, 1: 0}

    # wtuk7z9j (Group 18, maj=1): "is it also possible to pick it up in
    #   6 weeks or so?" / "because im on vacation haha" / "okay fine then
    #   i don't mind" → 起初有实际顾虑，后表示不介意 → 0
    W['wtuk7z9j'] = {0: None, 1: 0}

    # 3mhvxa5r (Group 18, maj=1): "i think with delay and more chance of
    #   return i can wait" → 愿意等待 → -1
    W['3mhvxa5r'] = {0: None, 1: -1}

    # --- session: 32qq2463 (majority=1) ---

    # g1tvlvk8 (Group 19, maj=1): "i dont want that much risk .. especially
    #   if i have to wait that time" → 不喜欢等待 → 1
    W['g1tvlvk8'] = {0: None, 1: 1}

    # nv74wiwy (Group 19, maj=1): "why not select the higher point one?"
    #   "6 has a better chance to get a higher point. and 50-50 is you win
    #   or lose situation. so i would rather go for the win side"
    #   → 关注收益而非等待时间 → 0（未明确表达对等待的好恶）
    W['nv74wiwy'] = {0: None, 1: 0}

    # 6nm4aea5 (Group 19, maj=1): "what is so special about 50-50"
    #   → 提问，未表达等待态度 → 0
    W['6nm4aea5'] = {0: None, 1: 0}

    # --- session: zspnbitg (majority=1) ---

    # 04ybbykm (Group 20, maj=1): "I was a bit selfish and selected all 10
    #   because we would get our points tomorrow 100% safe. Otherwise we
    #   would have to wait 4 weeks." → 明确想明天拿钱 → 1
    W['04ybbykm'] = {0: None, 1: 1}

    # gol08cao (Group 20, maj=1): "Can live with 8 points certain tomorrow"
    #   → 偏向明天拿钱 → 1
    W['gol08cao'] = {0: None, 1: 1}

    # qht1ncs7 (Group 20, maj=1): "i still like my idea of splitting it up"
    #   "im cool with it" → 未直接提及等待时间 → 0
    W['qht1ncs7'] = {0: None, 1: 0}

    # --- session: dkoekgf5 (majority=0) ---

    # 8qn9nh3b (Group 9, maj=0): "i decided for A because I am not that
    #   motivated to come here again in 4 weeks" → 不喜欢等待 → 1
    W['8qn9nh3b'] = {0: None, 1: 1}

    # hwcutjyi (Group 9, maj=0): "which one" / "situation 7 is different"
    #   "works for me" / "hahah" / "2 it is" → 未提及等待 → 0
    W['hwcutjyi'] = {0: None, 1: 0}

    # wca7iev8 (Group 9, maj=0): "well in group agreement i would say 2 or 3?"
    #   "ok" → 未提及等待 → 0
    W['wca7iev8'] = {0: None, 1: 0}

    # 4vn5iz9u (Group 10, maj=0): "okay" → 0
    W['4vn5iz9u'] = {0: None, 1: 0}

    # vycv5y5a (Group 10, maj=0): "Since two of us voted for setting the
    #   cut off at 70%..." → 未提及等待 → 0
    W['vycv5y5a'] = {0: None, 1: 0}

    # ltkdu9m4 (Group 7, maj=0): "yes, I'd do 2" → 0
    W['ltkdu9m4'] = {0: None, 1: 0}

    # 5izm8ier (Group 7, maj=0): "we could also go with 8=B" → 0
    W['5izm8ier'] = {0: None, 1: 0}

    # ur8cpf1h (Group 7, maj=0): "so participant 2 again?" → 0
    W['ur8cpf1h'] = {0: None, 1: 0}

    # s8g1e7mj (Group 8, maj=0): "Proposal 2?" / "Nice" → 0
    W['s8g1e7mj'] = {0: None, 1: 0}

    # 5pdq9e73 (Group 8, maj=0): "I would agree" / "That's the majority :)"
    #   → 0
    W['5pdq9e73'] = {0: None, 1: 0}

    # lf6j1q36 (Group 8, maj=0): "And again, I'm undecided about situation 5."
    #   → 0（犹豫，但与等待无关）
    W['lf6j1q36'] = {0: None, 1: 0}

    # --- session: vfgv3mdk (majority=0) ---

    # 19cpp9r7 (Group 11, maj=0): "Yall really want to wait 4 weeks for
    #   2 extra euros" / "In 4 weeks ill forget there was an experiment
    #   at all" → 强烈不喜欢等待 → 1
    W['19cpp9r7'] = {0: None, 1: 1}

    # 9ms0nc71 (Group 11, maj=0): "Yeah alright" → 0（接受他人意见）
    W['9ms0nc71'] = {0: None, 1: 0}

    # fk67q6oc (Group 11, maj=0): "sounds reasonable" → 0
    W['fk67q6oc'] = {0: None, 1: 0}

    # --- session: 6apbq166 (majority=0) ---

    # 3z868bro (Group 12, maj=0): "4 weeks is a long time" / "so getting the
    #   payoff after 4 weeks and that to with 70 percent is not good i feel"
    #   → 不喜欢等待 → 1
    W['3z868bro'] = {0: None, 1: 1}

    # jxqfasml (Group 12, maj=0): "for me it doesnt make a big diffrence if
    #   its tomorrow or in a month" → 中立 → 0
    W['jxqfasml'] = {0: None, 1: 0}

    # rghhx8hh (Group 12, maj=0): "what was your thought process" / "70 percent
    #   is quite good, I'd like to take the chances" → 关注收益未提等待 → 0
    W['rghhx8hh'] = {0: None, 1: 0}

    # obs7t4q0 (Group 13, maj=0): "im not gonna wait 4 weeks i promise that"
    #   "i might not be here in 4 weeks" / "its summer, i wanna be on vacation"
    #   → 强烈不喜欢等待 → 1
    W['obs7t4q0'] = {0: None, 1: 1}

    # zvmba2hz (Group 13, maj=0): "I don't care, we get the money either way"
    #   "I would wait four weeks to get more money" → 愿意等待 → -1
    W['zvmba2hz'] = {0: None, 1: -1}

    # bvph8u1v (Group 13, maj=0): "okay yeah i mean whatever you guys want"
    #   "what do we go for?" → 0（不关心，未明确表达等待态度）
    W['bvph8u1v'] = {0: None, 1: 0}

    # --- session: l1u9ytue (majority=0) ---

    # 8ntxu93h (Group 14, maj=0): "i chose option B just for the 100% chance,
    #   beecuase im not sure, if I remember or have the time to come here
    #   again in 4 weeks" → 不喜欢等待（实际困难） → 1
    W['8ntxu93h'] = {0: None, 1: 1}

    # to8qhvbi (Group 14, maj=0): "I'm open to any solution" / "I think p2
    #   is good" → 未提及等待 → 0
    W['to8qhvbi'] = {0: None, 1: 0}

    # tyxazhzc (Group 14, maj=0): "I honestly dont really care" / "I think
    #   I would rather choose me or 3" → 0（不在乎）
    W['tyxazhzc'] = {0: None, 1: 0}

    # 1gerc30m (Group 15, maj=0): "very risk averse" / "ok i'm down"
    #   "for 9" / "yes" → 未提及等待 → 0
    W['1gerc30m'] = {0: None, 1: 0}

    # 3jqz1v5q (Group 15, maj=0): "interesting haha" / "ok" → 0
    W['3jqz1v5q'] = {0: None, 1: 0}

    # dljhygqr (Group 15, maj=0): "for me option 9 would also be okay :)"
    #   "definitely :)" / "okay so we make a new voting and then 1-8 A and
    #   9 and 10 B? :)" → 未提及等待 → 0
    W['dljhygqr'] = {0: None, 1: 0}

    # --- session: f0el3eip (majority=0) ---

    # j4lmty8b (Group 17, maj=0): "kein interesse wegen möglichen 2 euro
    #   unterschied 4 wochen länger zu warten"
    #   → 不愿为2欧元等4周 → 1
    W['j4lmty8b'] = {0: None, 1: 1}

    # 38cndqe5 (Group 17, maj=0): "for 6, we get 0,6 more, do not deserve
    #   four weeks" → 认为不值得等4周 → 1
    W['38cndqe5'] = {0: None, 1: 1}

    # t2m5a7ev (Group 17, maj=0): "we choose Proposal Participant 2?"
    #   "ok also option 3?" → 未直接提及等待 → 0
    W['t2m5a7ev'] = {0: None, 1: 0}

    # ogjqbbqv (Group 16, maj=0): "I would take option 1" → 0
    W['ogjqbbqv'] = {0: None, 1: 0}

    # bin13zaw (Group 16, maj=0): "Me as well Option 1, it's quite neutral"
    #   → 0
    W['bin13zaw'] = {0: None, 1: 0}

    # --- session: c29h9lab (majority=0) ---

    # ntpj6k3y (Group 18, maj=0): "I dont care if I get it tomorrow or in
    #   four weeks honestly haha" → 明确不在乎 → 0
    W['ntpj6k3y'] = {0: None, 1: 0}

    # txkohpoy (Group 18, maj=0): "me neither" / "i cant tomorrow haha"
    #   → 实际限制（明天无法取），但与等待4周的态度无关 → 0
    W['txkohpoy'] = {0: None, 1: 0}

    # va4iv92o (Group 18, maj=0): "i prefer tomorrow but 90 per cent is okay
    #   too, just unsure if I will remember to collect it"
    #   → 偏好明天但不排斥等待 → 1
    W['va4iv92o'] = {0: None, 1: 1}

    # 2yaken99 (Group 20, maj=0): "also in theory i would go for more money,
    #   but it is summer and who will be here to collect in 4 weeks??"
    #   "but i am okay with whatever you guys want"
    #   → 不喜欢等待（实际困难），但灵活 → 1
    W['2yaken99'] = {0: None, 1: 1}

    # rzjg5ms6 (Group 20, maj=0): "so we all agree again lol" / "its
    #   gameeeeeee" / "lmfao" / "ok money is money come on#"
    #   → 开玩笑/离题，未认真表达等待态度 → 0
    W['rzjg5ms6'] = {0: None, 1: 0}

    # u1d934qi (Group 20, maj=0): "are we actually gonna get the money in
    #   4 weeks or is just the game? :)))"
    #   "alright we should agree to just get this done with"
    #   → 提问而非表态 → 0
    W['u1d934qi'] = {0: None, 1: 0}

    # 3ykoed4m (Group 19, maj=0): "Let us go with Participant 2, as the
    #   proposal has 67 percent weightage." → 未提及等待 → 0
    W['3ykoed4m'] = {0: None, 1: 0}

    # mvlrigx2 (Group 19, maj=0): "we go again with 2" → 0
    W['mvlrigx2'] = {0: None, 1: 0}

    # --- session: ymgl8k4i (majority=0) ---

    # cbe3hywl (Group 23, maj=0): "i think that 4 weeks is an amount of time
    #   that i can wait , but only with a very reasonable chence to get the
    #   points (over 80%)" → 愿意条件性等待 → -1
    W['cbe3hywl'] = {0: None, 1: -1}

    # gr8r5tzp (Group 23, maj=0): "ok 3 it's then" / "yes" → 0
    W['gr8r5tzp'] = {0: None, 1: 0}

    # f5g4wfzh (Group 23, maj=0): "chosing 1 or 3 is the same, it's ok for
    #   me to choose 3" / "all agree?" → 0
    W['f5g4wfzh'] = {0: None, 1: 0}

    # dufx3vxe (Group 22, maj=0): "Either my proposal or the one of
    #   participant 1 are fine for me, I want to maximise the revenue in
    #   any case." → 关注收益最大化，未提等待 → 0
    W['dufx3vxe'] = {0: None, 1: 0}

    # ee6sjzk2 (Group 22, maj=0): "Fine by me" → 0
    W['ee6sjzk2'] = {0: None, 1: 0}

    # h9pn79r3 (Group 24, maj=0): "I think that Me and partcipant 2 have
    #   better proposal" / "ok" → 0
    W['h9pn79r3'] = {0: None, 1: 0}

    # z6l5xogp (Group 24, maj=0): "I know, I'm just greedy" / "let's do
    #   participant 2?" → 0（关注收益）
    W['z6l5xogp'] = {0: None, 1: 0}

    # --- session: y1hj2aj2 (majority=1) ---

    # nfy1ut59 (Group 17, maj=1): "i would propose the same proposal as last
    #   round. i dont mind getting the money a few weeks later, a better
    #   chance for a higher amount is better for me" → 愿意等待 → -1
    W['nfy1ut59'] = {0: None, 1: -1}

    # hqox7ku0 (Group 17, maj=1): "I was not sure of the utility..."
    #   "Alright" → 未明确表达等待态度 → 0
    W['hqox7ku0'] = {0: None, 1: 0}

    # ryn74uw6 (Group 17, maj=1): "i could agree" → 0
    W['ryn74uw6'] = {0: None, 1: 0}

    # --- session: 0f9u4oto (majority=1) ---

    # lt35om27 (Group 9, maj=1): "should we meet in the middle (choosing the
    #   second offer)?" / "okay" → 未提及等待 → 0
    W['lt35om27'] = {0: None, 1: 0}

    # zi7p95ny (Group 9, maj=1): "i was thinking the same" / "so voting for
    #   2?" → 0
    W['zi7p95ny'] = {0: None, 1: 0}

    # f5j9rxu9 (Group 9, maj=1): "if time is important lets settle for P2"
    #   → 提到时间但不明确 → 0
    W['f5j9rxu9'] = {0: None, 1: 0}

    # mldp6kdi (Group 10, maj=1): "hello" / "+" → 0
    W['mldp6kdi'] = {0: None, 1: 0}

    # uxkihpwg (Group 10, maj=1): "hi! P1s?" → 0
    W['uxkihpwg'] = {0: None, 1: 0}

    # --- session: 8kn3iz3d (majority=0) ---

    # vqcyaekn (Group 6, maj=0): "ok so me and participant 1 are thinking
    #   the same" / "yes 60/40 for me too" → 0
    W['vqcyaekn'] = {0: None, 1: 0}

    # 84h1hu66 (Group 6, maj=0): "hi" / "yes" / "proposal 1 then?" → 0
    W['84h1hu66'] = {0: None, 1: 0}

    # jg63k1y5 (Group 6, maj=0): "70/30 split works for me as well"
    #   "60/40" / "proposal 1 then?" → 0
    W['jg63k1y5'] = {0: None, 1: 0}

    # --- session: 1gzf7p6u (majority=0) ---

    # fe11vpqw (Group 21, maj=0): "I dont mind but I think 1 would be a
    #   good compromise" → 未提等待 → 0
    W['fe11vpqw'] = {0: None, 1: 0}

    # bw3qty6c (Group 21, maj=0): "yeah i think so too :P" → 0
    W['bw3qty6c'] = {0: None, 1: 0}

    # --- session: bbgfffw6 (majority=0) ---

    # All TR=1 participants in bbgfffw6 sessions
    # ncmbeu96 (Group 1): "it is a problem about mean value..."
    #   "ja" / "thanks for the coorperation" → 未提及等待 → 0
    W['ncmbeu96'] = {0: None, 1: 0}

    # w925dou6 (Group 1): "hi" / "are we the same people" / "fine for me"
    #   → 0
    W['w925dou6'] = {0: None, 1: 0}

    # 6ogvjie9 (Group 1): "maybe i am too risk avoid but i can take either
    #   1 or 2" / "but i suggest for plan 2?" → 0
    W['6ogvjie9'] = {0: None, 1: 0}

    # rx0314r2 (Group 2): "which one" / "ok" → 0
    W['rx0314r2'] = {0: None, 1: 0}

    # hj311cpt (Group 2): "I suggest the middle so part. 3" → 0
    W['hj311cpt'] = {0: None, 1: 0}

    # qirxmn9p (Group 2): "vote 3" → 0
    W['qirxmn9p'] = {0: None, 1: 0}

    # 4t7f8z8s (Group 3): "all of them are good" / "so maybe 2" / "i will
    #   3 too" → 0
    W['4t7f8z8s'] = {0: None, 1: 0}

    # 7g3hzz4a (Group 3): "I'd be fine with either choice" → 0
    W['7g3hzz4a'] = {0: None, 1: 0}

    # yj9as5vl (Group 3): "2 and 3 are same" / "great:)" → 0
    W['yj9as5vl'] = {0: None, 1: 0}

    # os109bhi (Group 4): "Ok I think two are the same, would it be okay..."
    #   "Great!" → 0
    W['os109bhi'] = {0: None, 1: 0}

    # xqu5dupq (Group 4): "yes, Proposal 2" → 0
    W['xqu5dupq'] = {0: None, 1: 0}

    # gpsmk0bn (Group 4): "yes" → 0
    W['gpsmk0bn'] = {0: None, 1: 0}

    # vssecnms (Group 5): "I'm absolutely fine..." / "Sure!" → 0
    W['vssecnms'] = {0: None, 1: 0}

    # p8s0es6v (Group 5): "Hi, I think we should identidy not only the
    #   potential tradeoff, but also the time lag." / "Then I'd select
    #   proposal 3" → 提到时间因素但不明确好恶 → 0
    W['p8s0es6v'] = {0: None, 1: 0}

    # aa4qjckr (Group 5): "Yes!" → 0
    W['aa4qjckr'] = {0: None, 1: 0}

    return W


def apply_wait_classification():
    """
    主函数：加载数据 → 构建分类 → 映射到 dataset2026 → 输出
    """
    print("=" * 60)
    print("Wait Attitude Classification — wait1 & wait2")
    print("=" * 60)

    # 加载数据
    print("\n[1/3] 加载数据...")
    msg = pd.read_excel(MESSAGE_FILE)
    ds = pd.read_excel(DATASET_FILE)
    print(f"  消息数据: {msg.shape[0]} 条消息")
    print(f"  数据集:   {ds.shape[0]} 行")

    # 构建分类
    print("\n[2/3] 构建 wait 分类...")
    W = build_wait_classification()

    n_tr0 = sum(1 for pc in W if W[pc].get(0) is not None)
    n_tr1 = sum(1 for pc in W if W[pc].get(1) is not None)
    print(f"  TR=0 分类: {n_tr0} 人")
    print(f"  TR=1 分类: {n_tr1} 人")

    # 构建映射
    wait_tr0_map = {pc: W[pc][0] for pc in W if W[pc].get(0) is not None}
    wait_tr1_map = {pc: W[pc][1] for pc in W if W[pc].get(1) is not None}

    ds['wait1'] = ds['subject_code'].map(wait_tr0_map)
    ds['wait2'] = ds['subject_code'].map(wait_tr1_map)

    # 未匹配到分类的默认为 0（没有相关消息或未参与对话）
    ds['wait1'] = ds['wait1'].fillna(0).astype(int)
    ds['wait2'] = ds['wait2'].fillna(0).astype(int)

    # 保存
    print("\n[3/3] 保存结果...")
    ds.to_excel(OUTPUT_FILE, index=False)
    print(f"  结果已保存至: {OUTPUT_FILE}")

    # 统计摘要
    print("\n" + "=" * 60)
    print("分类结果摘要")
    print("=" * 60)

    for col, label in [('wait1', 'TR=0 (纯风险)'), ('wait2', 'TR=1 (延迟风险)')]:
        vc = ds[col].value_counts().sort_index()
        total = len(ds)
        print(f"\n{label}:")
        labels = {-1: '愿意等待 (-1)', 0: '未提及/中立 (0)', 1: '不喜欢等待 (1)'}
        for val in [-1, 0, 1]:
            count = vc.get(val, 0)
            print(f"  {labels[val]}: {count} ({count/total*100:.1f}%)")

    # 交叉表
    print("\n--- wait1 × wait2 交叉表 ---")
    ct = pd.crosstab(ds['wait1'], ds['wait2'], dropna=False, margins=True)
    print(ct.to_string())

    # TR=1 详细列表
    print("\n--- TR=1 wait2 != 0 详情 ---")
    non_zero = ds[ds['wait2'] != 0][['subject_code', 'session_code', 'wait2']]
    for _, row in non_zero.iterrows():
        label = '愿意等待' if row['wait2'] == -1 else '不喜欢等待'
        print(f"  {row['subject_code']} ({row['session_code']}): {label}")

    return ds


if __name__ == '__main__':
    ds = apply_wait_classification()
