import os
import sys

# PyOCRを読み込む
from PIL import Image
import pyocr
import pytesseract
import pyocr.builders


def detect_text(img_path):
    # Tesseract-OCRの実行ファイルと言語データのパスを指定
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    # custom_config = r'--tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'

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

    print("file_path:", file_path)
    print("lang: ", lang)
    print("----------")
    print(text)
    # print(result)
    """
    # Tesseractのインストール場所をOSに教える
    tesseract_path = "C:\Program Files\Tesseract-OCR"
    if tesseract_path not in os.environ["PATH"].split(os.pathsep):
        print("Yes")
        os.environ["PATH"] += os.pathsep + tesseract_path

    # OCRエンジンを取得する
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("OCRエンジンが指定されていません")
        sys.exit(1)
    else:
        tool = tools[0]

    # 画像の読み込み
    img = Image.open(img_path)

    # 文字を読み取る
    builder = pyocr.builders.TextBuilder(tesseract_layout=6)
    result = tool.image_to_string(img, lang="jpn", builder=builder)

    print(result)
    """
    return 1
