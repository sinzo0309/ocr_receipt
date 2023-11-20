# 以下実行後、リスタートが必要
#!pip install --upgrade google-cloud-vision
GOOGLE_CLOUD_VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate?key="

import os

# from google.oauth2 import service_account
from collections import Counter
from google.cloud import vision

key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def process_string(S):
    result = []

    for s in S:
        if s.isdigit():
            result.append(int(s))
        else:
            if s[1:].isdigit():
                result.append(int(s[1:]))
            elif s[:-1].isdigit():
                result.append(int(s[:-1]))
    return result


def detect_text(path):
    """Detects text in the file."""
    try:
        # client = vision.ImageAnnotatorClient()
        client = vision.ImageAnnotatorClient.from_service_account_file(key_path)
    # ここに問題のあるコード
    except Exception as e:
        # エラー発生時にログを出力
        print(f"Error: {str(e)}")
    # traceback.print_exc()
    # client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print(texts[0].description)
    for text in texts[1:]:
        if "合計" in text.description or "計" in text.description:
            y1 = text.bounding_poly.vertices[0].y
            y2 = text.bounding_poly.vertices[2].y
    Sum = []

    for text in texts[10:]:
        if (
            y1 - 5 <= text.bounding_poly.vertices[0].y <= y2 + 5
            or y1 - 5 <= text.bounding_poly.vertices[2].y <= y2 + 5
        ):
            if "," in text.description:
                Sum.append(text.description.replace(",", ""))
            elif "." in text.description:
                Sum.append(text.description.replace(".", ""))
            elif " " in text.description:
                Sum.append(text.description.replace(" ", ""))
            else:
                Sum.append(text.description)

    n_sum = process_string(Sum)
    print(n_sum)
    print(max(n_sum))
    return max(n_sum)
