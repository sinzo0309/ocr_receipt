import json
import os
import re

from google.cloud import vision

credentials_data = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


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
    for line in lines:
        texts = [i[2] for i in line]
        texts = "".join(texts)
        # bounds = [i[3] for i in line]
        print(texts)
    return [1, "12月13日", 1]
    """
    if str(max(n_sum))[0] == "4" and int(str(max(n_sum))[1:]) in Sum:
        return [max(n_sum)[1:], date_process(date), detail]

    elif str(max(n_sum))[0] == "1" and int(str(max(n_sum))[1:]) in Sum:
        return [max(n_sum)[1:], date_process(date), detail]

    else:
        return [max(n_sum), date_process(date), detail]
    """