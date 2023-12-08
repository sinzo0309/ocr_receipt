import json
import os
import re

from google.cloud import vision

credentials_data = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def date_process(date):
    new_date = ""
    for i, term in enumerate(date):
        try:
            if term == "年":
                new_date += date[i - 4 : i] + "年"
            elif term == "月":
                new_date += date[i - 2 : i] + "月"
            elif term == "日":
                new_date += date[i - 2 : i] + "日"
        except:
            continue
    print(new_date)
    return new_date


def process_string(S):
    result = []

    for s in S:
        if s[0] == "4":
            result.append(int(s))
        elif s.isdigit():
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
    print(texts[0].description)
    date = ""
    flag = True
    F = True
    for text in texts[1:]:
        # print(text.description)
        if ("合計" in text.description or "消費税" in text.description) and F:
            F = False
            print("############")
            print(text.description)
            print("############")
            y1 = text.bounding_poly.vertices[0].y
            y2 = text.bounding_poly.vertices[2].y
        if ("年" in text.description or "月" in text.description) and flag:
            ydate1 = text.bounding_poly.vertices[0].y
            ydate2 = text.bounding_poly.vertices[2].y
            flag = False
    try:
        for text in texts[1:]:
            if (
                ydate1 - 3 <= text.bounding_poly.vertices[0].y <= ydate2 + 3
                or ydate1 - 3 <= text.bounding_poly.vertices[2].y <= ydate2 + 3
            ):
                date += text.description
                print(date)
    except:
        pass
    Sum = []

    for text in texts[10:]:
        try:
            if (
                y1 - 5 <= text.bounding_poly.vertices[0].y <= y2 + 5
                or y1 - 5 <= text.bounding_poly.vertices[2].y <= y2 + 5
            ):
                # print(text.description)
                result = re.sub(r"\D", "", text.description)
                Sum.append(result)
                print(result, "result")

                if "," in text.description:
                    Sum.append(text.description.replace(",", ""))
                elif "." in text.description:
                    Sum.append(text.description.replace(".", ""))
                elif " " in text.description:
                    Sum.append(text.description.replace(" ", ""))
                else:
                    Sum.append(text.description)
        except:
            continue

    print("Sum", Sum)
    n_sum = process_string(Sum)
    return [max(n_sum), date]
