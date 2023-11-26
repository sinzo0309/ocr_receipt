import os

# PyOCRを読み込む
from PIL import Image
import pyocr
import pyocr.builders
import cv2


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


def detect_text(img_path, ksize):
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
    # print(text)
    money = []
    for txt in text:
        print(txt.content)
        if "合計" in txt.content or "計" in txt.content or "合" in txt.content:
            money += process_string(txt.content)

    print(money)
    return max(money)
