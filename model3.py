import json
import os
import re

from google.cloud import vision

credentials_data = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


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
        credentials = json.loads(credentials_data)
        client = vision.ImageAnnotatorClient.from_service_account_info(credentials)
    except Exception as e:
        return None

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    # print(texts[0].description)
    date = ""
    for text in texts[1:]:
        flag = True
        print(text.description)
        if "合計" in text.description or "計" in text.description:
            y1 = text.bounding_poly.vertices[0].y
            y2 = text.bounding_poly.vertices[2].y
        elif (
            "年" in text.description
            or "月" in text.description
            or "日" in text.description
        ) and flag:
            ydate1 = text.bounding_poly.vertices[0].y
            ydate2 = text.bounding_poly.vertices[2].y
            flag = False
    for text in texts[1:]:
        if (
            ydate1 <= text.bounding_poly.vertices[0].y <= ydate2
            or ydate1 <= text.bounding_poly.vertices[2].y <= ydate2
        ):
            date += text.description
            print(date)
    Sum = []

    for text in texts[10:]:
        if (
            y1 - 5 <= text.bounding_poly.vertices[0].y <= y2 + 5
            or y1 - 5 <= text.bounding_poly.vertices[2].y <= y2 + 5
        ):
            # print(text.description)
            result = re.sub(r"\D", "", text.description)
            Sum.append(result)
            # print(result)
            if "," in text.description:
                Sum.append(text.description.replace(",", ""))
            elif "." in text.description:
                Sum.append(text.description.replace(".", ""))
            elif " " in text.description:
                Sum.append(text.description.replace(" ", ""))
            else:
                Sum.append(text.description)

    # print(Sum)
    n_sum = process_string(Sum)
    return [max(n_sum), date]
