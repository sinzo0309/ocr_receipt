import json
import os
import re

from google.cloud import vision

credentials_data = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def gen_detail(detail):
    # print("matchmatchmatch")
    text = ""
    pattern = r"([^\d¥]*)(¥[\d,]+)"
    matches = re.findall(pattern, detail)
    for match in matches:
        # print(match)
        product_name = match[0].strip()
        price = match[1]
        text += "商品名:" + product_name + "価格:" + price + " "
    # print("matchmatchmatch")
    return text


def gen_cash(cash):
    Sum = []
    number = ""
    # print("%%%%%%%%%%%%%%%%")
    for c in cash:  # 文字列からひとつづつ抜き出す
        # print("c", c)
        if c.isdigit():  # 数字の場合
            number += str(c)
            # print("number", number)
        else:  # 数字じゃなかった場合
            if c == "," or c == "." or c == " ":
                continue
            elif len(number) > 0:
                Sum.append(int(number))
                number = ""
    if number:
        Sum.append(int(number))
    # print("合計", max(Sum))
    return max(Sum)  # 合計金額候補の中で、合計金額が購入点数を超えないという仮定の上


def get_sorted_lines(response):
    document = response.full_text_annotation
    bounds = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        x = symbol.bounding_box.vertices[0].x
                        y = symbol.bounding_box.vertices[0].y
                        text = symbol.text
                        bounds.append([x, y, text, symbol.bounding_box])
    bounds.sort(key=lambda x: x[1])
    old_y = -1
    line = []
    lines = []
    threshold = 1
    for bound in bounds:
        x = bound[0]
        y = bound[1]
        if old_y == -1:
            old_y = y
        elif old_y - threshold <= y <= old_y + threshold:
            old_y = y
        else:
            old_y = -1
            line.sort(key=lambda x: x[0])
            lines.append(line)
            line = []
        line.append(bound)
    line.sort(key=lambda x: x[0])
    lines.append(line)
    return lines


def date_process(date):
    new_date = ""
    for i, term in enumerate(date):
        try:
            if term == "年":
                new_date += date[i - 4 : i + 1]

            elif term == "月":
                new_date += date[i - 2 : i + 1]

            elif term == "日":
                new_date += date[i - 2 : i + 1]
                break

        except:
            continue
    return new_date


def check_mark(textbox, sumation):
    for i in textbox:
        if sumation in i:
            return True

    else:
        return False


def process_string(S):
    result = []

    for s in S:
        try:
            if len(s) > 0:
                if s[0] == "4":
                    result.append(int(s))
                if s.isdigit():
                    result.append(int(s))
                if s[1:].isdigit():
                    result.append(int(s[1:]))
                if s[:-1].isdigit():
                    result.append(int(s[:-1]))
        except:
            continue
    return result


def detect_text(path):
    """Detects text in the file."""
    try:
        credentials = json.loads(credentials_data)
        client = vision.ImageAnnotatorClient.from_service_account_info(credentials)
    except Exception as e:
        print("credentials error")
        print(e)
        return None

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    lines = get_sorted_lines(response)
    print("1##################1")
    T = False
    detail = ""
    textbox = []
    i = 5
    F = False
    a = True
    for line in lines:
        texts = [i[2] for i in line]
        texts = "".join(texts)
        # bounds = [i[3] for i in line]
        print(texts)
        if "小計" in texts:
            T = False
            # print("detail終了")
        if T:  # 購入日付と小計の間に購入品目が書かれがち
            # print(detail)
            detail += " " + texts
        if "年" and "月" and "日" in texts and a:
            date = texts
            T = True
            a = False
            # print("detail開始")
        if "合計" in texts:
            n = gen_cash(texts)
            # print("合計", n)
            F = True
        if F and i >= 0:
            textbox.append(texts)
            i -= 5

    print("1##################1")
    """if str(n)[0] == "4" and check_mark(textbox, str(n)[1:]):
        return [int(str(n[1:])), date_process(date), detail]"""
    # print(detail)
    detail = gen_detail(detail)
    # print("matchmatchmatch")
    # print(detail)
    return [n, date_process(date), detail]
