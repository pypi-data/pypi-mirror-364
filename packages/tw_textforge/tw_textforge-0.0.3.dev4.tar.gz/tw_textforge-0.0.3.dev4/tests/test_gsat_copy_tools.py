import pytest

def test_gsat_copy_tools():
    import tw_textforge.utils as tools
    text = """
11.	文中羿與嫦娥言語失和的原因，最可能的選項是：
(A)羿不務正業，只知狩獵遊樂而不照顧嫦娥
(B)羿的狩獵成果，無法滿足嫦娥的生活所需
(C)嫦娥不想再過僕傭簇擁的生活，羿卻不然
(D)嫦娥掌握家中大權，把羿當成僕傭來使喚
12.	下列關於文中描寫的敘述，**不恰當**的選項是：
(A)嫦娥「風似地往外走」，意在強調嫦娥的輕盈敏捷
(B)「羿在垃圾堆邊懶懶地下了馬」，暗喻羿的困頓處境
(C)木榻「鋪著脫毛的舊豹皮」，暗指羿被現實生活不斷消磨
(D)「她們（使女）都在苦笑」，其實是羿個人內心感受的投射
"""
    result = tools.extract_questions(text)
    
    target_result = ['"文中羿與嫦娥言語失和的原因，最可能的選項是："\t羿不務正業，只知狩獵遊樂而不照顧嫦娥\t羿的狩獵成果，無法滿足嫦娥的生活所需\t嫦娥不想再過僕傭簇擁的生活，羿卻不然\t嫦娥掌握家中大權，把羿當成僕傭來使喚',
 '"下列關於文中描寫的敘述，**不恰當**的選項是："\t嫦娥「風似地往外走」，意在強調嫦娥的輕盈敏捷\t「羿在垃圾堆邊懶懶地下了馬」，暗喻羿的困頓處境\t木榻「鋪著脫毛的舊豹皮」，暗指羿被現實生活不斷消磨\t「她們（使女）都在苦笑」，其實是羿個人內心感受的投射']
    
    if result is None:
        pytest.fail("extract_questions returned None")
    elif not isinstance(result, list):
        pytest.fail("extract_questions did not return a list")
    elif len(result) < 2:
        pytest.fail("extract_questions returned an empty list or insufficient data")
    if result != target_result:
        pytest.fail(f"extract_questions did not return the expected result. Got: {result}, Expected: {target_result}")
    else:
        print("Extracted questions match the target result.")

    data = """
題號 答案 題號 答案 題號 答案
1 C 21 B 41 ABC
2 B 22 B 42 DE
3 C 23 D
4 B 24 C
5 B 25 D
6 D 26 A
7 D 27 A
8 B 28 B
9 C 29 D
10 C 30 A
11 C 31 C
12 A 32 D
13 D 33 C
14 A 34 A
15 D 35 BC
16 A 36 BCD
17 A 37 CE
18 C 38 ABE
19 B 39 ABC
20 D 40 BDE
"""
    answers = tools.extract_answers(data)
    target_answers = ['C',
 'B',
 'C',
 'B',
 'B',
 'D',
 'D',
 'B',
 'C',
 'C',
 'C',
 'A',
 'D',
 'A',
 'D',
 'A',
 'A',
 'C',
 'B',
 'D',
 'B',
 'B',
 'D',
 'C',
 'D',
 'A',
 'A',
 'B',
 'D',
 'A',
 'C',
 'D',
 'C',
 'A',
 'BC',
 'BCD',
 'CE',
 'ABE',
 'ABC',
 'BDE',
 'ABC',
 'DE']
    
    if answers is None:
        pytest.fail("extract_answers returned None")
    elif not isinstance(answers, list):
        pytest.fail("extract_answers did not return a list")
    elif len(answers) < 42:
        pytest.fail("extract_answers returned an empty list or insufficient data")
    if answers != target_answers:
        pytest.fail(f"extract_answers did not return the expected result. Got: {answers}, Expected: {target_answers}")
    else:
        print("Extracted answers match the target result.")