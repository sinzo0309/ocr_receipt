import os

# PyOCRを読み込む
from PIL import Image
import pyocr
import pyocr.builders
import re


def cashfinder(lines):
    y_indices = []

    # Initialize an empty list to store the cash amounts
    money_list = []

    # Iterate over the lines
    for line in lines:
        # If "消費税" or "消" is in the line, store the y-index
        if "消費税" in line.content or "消" in line.content:
            y_indices.append(line.position[1][1])

    # Iterate over the lines again
    for line in lines:
        # If the y-index is near one of the stored y-indices
        if any(abs(line.position[1][1] - y_index) <= 10 for y_index in y_indices):
            # Find any numbers in the line
            numbers = re.findall(r"\d+", line.content)
            # If there are any numbers, add them to the money_list
            if numbers:
                money_list.extend(numbers)

    # Return the money_list
    return money_list


def date_process(date):
    new_date = ""
    for i, term in enumerate(date):
        try:
            if term == "年":
                new_date += date[i - 5 : i] + "年"
            elif term == "月":
                new_date += date[i - 3 : i] + "月"
            elif term == "日":
                new_date += date[i - 3 : i] + "日"
        except:
            continue
    return new_date


def process_string(S):
    result = []
    # print()
    # print(S)
    number = ""
    for s in S:
        # print(s)
        if s.isdigit():
            # print(1111)
            number += str(s)
            # print(number)
        elif (s == " " or s == "," or s == ".") and len(number) != 0:
            # print(2222)
            # print(number)
            continue
        else:
            if len(number) > 0:
                result.append(int(number))
                number = ""
            # print(3333)
            continue
    if len(number) > 0:
        result.append(int(number))
    # print()
    return result


def detect_text(img_path):
    # Tesseract-OCRの実行ファイルと言語データのパスを指定
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR"
    TESSDATA_PATH = r"C:\Program Files\Tesseract-OCR\tessdata"

    os.environ["PATH"] += os.pathsep + TESSERACT_PATH
    os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH
    if TESSERACT_PATH not in os.environ["PATH"].split(os.pathsep):
        print("Yes")
        os.environ["PATH"] += os.pathsep + TESSERACT_PATH

    tools = pyocr.get_available_tools()
    print(tools)
    # 日本語のパラメータを指定
    # result = pytesseract.image_to_string(img, lang="jpn")
    file_path = img_path
    lang = "jpn"

    tool = pyocr.get_available_tools()[0]
    text = tool.image_to_string(
        Image.open(file_path), lang=lang, builder=pyocr.builders.LineBoxBuilder()
    )
    print(text)
    money = []
    date = ""

    for txt in text:
        print(txt.content)
        if (
            "合計" in txt.content
            or "計" in txt.content
            or "合" in txt.content
            or "消費" in txt.content
            or "費税" in txt.content
        ):
            money += process_string(txt.content)
        if "年" in txt.content or "月" in txt.content or "日" in txt.content:
            date += txt.content

    print(money)
    print("ここまでがモデルの部分")
    print("###################")
    if money:
        print(111111111111111)
        return [max(money), date]
    else:
        print(2222222222222)
        money = cashfinder(text)
        print(money)
        cash = max(money)
        return [cash, date]
