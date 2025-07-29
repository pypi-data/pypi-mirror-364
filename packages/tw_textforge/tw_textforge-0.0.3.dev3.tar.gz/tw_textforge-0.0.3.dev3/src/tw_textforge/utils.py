import re
import pyperclip

def extract_questions(raw_text):
    # 分割題號與題幹
    pattern = re.compile(
        r'(?P<qnum>\d+)\.\s*(?P<question>.+?)\n(?P<options>(?:\([A-E]\).+?\n)+)',
        re.MULTILINE | re.DOTALL
    )

    results = []

    for match in pattern.finditer(raw_text):
        question = match.group("question").strip()
        options_block = match.group("options")

        quoted_question = f'"{question}"'

        # 提取選項內容
        options = re.findall(r'\([A-E]\)(.+)', options_block)
        cleaned_options = [opt.strip() for opt in options]

        # 每題一列：問題 + 選項們
        results.append('\t'.join([quoted_question] + cleaned_options))
    if pyperclip.determine_clipboard():
        try:
            pyperclip.copy('\n'.join(results))
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
    return results

def extract_answers(data):
    """
    從給定的資料中提取題號和答案對應關係，並返回排序後的列表。
    
    example:
    data = ```
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
    ```
    # 輸出格式僅包含答案
    for num, ans in extract_answers(data):
        print(f"{ans}")
    # 輸出格式包含題號和答案
    for num, ans in extract_answers(data):
        print(f"{num}. {ans}")
    """
    # 用正則表達式抓取所有 題號-答案 配對
    pairs = re.findall(r'(\d+)\s+([A-E]+)', data)
    # 按題號排序
    pairs = sorted([(int(num), ans) for num, ans in pairs], key=lambda x: x[0])
    if pyperclip.determine_clipboard():
        try:
            pyperclip.copy('\n'.join([f"{ans}" for num, ans in pairs]))
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
    return pairs