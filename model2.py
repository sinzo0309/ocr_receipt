# 以下実行後、リスタートが必要
#!pip install --upgrade google-cloud-vision
from google.cloud import vision
import sys

GOOGLE_CLOUD_VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate?key="

from google.oauth2 import service_account
from collections import Counter


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

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    # print(texts[0].description)
    # print("Texts:")
    y2 = 0
    y1 = 0
    Sum = []
    flag = True
    for text in texts:
        if ("消費税" in text.description or "税" in text.description) and flag:
            y1 = text.bounding_poly.vertices[0].y

        if ("消費税" in text.description or "税" in text.description) and not flag:
            y2 = text.bounding_poly.vertices[2].y
        flag = False
        if "合計" in text.description:
            ysum1 = text.bounding_poly.vertices[0].y
            ysum2 = text.bounding_poly.vertices[2].y
    print(ysum1, ysum2, y1, y2)
    if y1 == 0 or y2 == 0:
        print("yes")
        for text in texts:
            print(111111, text.description, text.bounding_poly.vertices[0])
            if (
                ysum1 - 10 <= text.bounding_poly.vertices[0].y <= ysum2 + 10
                or ysum1 - 10 <= text.bounding_poly.vertices[2].y <= ysum2 + 10
            ):
                print("yes")
                if "," in text.description:
                    Sum.append(text.description.replace(",", ""))
                elif "." in text.description:
                    Sum.append(text.description.replace(".", ""))
                else:
                    Sum.append(text.description)
            print(Sum)
            n_sum = process_string(Sum)
            print(n_sum)
            # print(max(n_sum))
            return max(n_sum)
    print(n_sum)
    if y2 == 0:
        y2 = texts[-1].bounding_poly.vertices[2].y

    for text in texts[10:]:
        if (
            y1 <= text.bounding_poly.vertices[0].y <= y2
            or y1 <= text.bounding_poly.vertices[2].y <= y2
        ):
            if "," in text.description:
                Sum.append(text.description.replace(",", ""))
            elif "." in text.description:
                Sum.append(text.description.replace(".", ""))
            else:
                Sum.append(text.description)

    n_sum = process_string(Sum)
    print(n_sum)
    print(max(n_sum))
    return max(n_sum)
