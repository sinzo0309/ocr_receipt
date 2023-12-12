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
        return None

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    # print(texts[0].description)
    date = ""
    flag = True
    F = True
    b = False
    detail = ""
    pattern = re.compile(r"[ぁ-んァ-ンー]+")
    nword = [
        "月",
        "日",
        "金",
        "火",
        "水",
        "木",
        "土",
        "税込",
        "小計",
        "品",
        "合計",
        "レジ",
        "レシート",
        "小",
        "計",
        "内",
        "消費",
        "税",
        "対",
        "象",
        "消費",
        "税",
        "バーコード",
        "決済",
        "支払",
        "伝票",
        "番号",
        "支",
        "払",
        "バー",
        "コード",
        "外",
        "等",
    ]
    temp = ""
    japanese_pattern = re.compile(r"[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]+")
    for text in texts[1:]:
        print(text.description)
        if b:
            # matches = re.findall(pattern, text.description)
            # result = "".join(matches)
            temp += text.description
            if not text.description in nword and bool(
                japanese_pattern.search(text.description)
            ):
                detail += str(text.description) + ","
        if (
            "合計" in text.description
            or "消費税" in text.description
            or "合" in text.description
        ) and F:
            F = False
            y1 = text.bounding_poly.vertices[0].y
            y2 = text.bounding_poly.vertices[2].y
            b = False
        if ("年" in text.description or "月" in text.description) and flag:
            b = True
            ydate1 = text.bounding_poly.vertices[0].y
            ydate2 = text.bounding_poly.vertices[2].y
            flag = False
    try:
        for text in texts[1:]:
            if (
                ydate1 - 1 <= text.bounding_poly.vertices[0].y <= ydate2 + 1
                or ydate1 - 1 <= text.bounding_poly.vertices[2].y <= ydate2 + 1
            ):
                date += text.description
                # print(date)
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
    print(Sum)
    n_sum = process_string(Sum)
    print("$$$$$$$$$$$$$$$$$")
    print(temp)
    print("$$$$$$$$$$$$$$$$$")
    matches = re.findall(r"[^\d¥※%()]+", temp)
    detail = ""
    # 結果を表示
    print("&&&&&&&&&&&&&&&&&")
    for match in matches:
        if match.strip() not in nword:
            detail += match.strip() + ","
            print(match.strip())
    if str(max(n_sum))[0] == "4" and int(str(max(n_sum))[1:]) in Sum:
        return [max(n_sum)[1:], date_process(date), detail]

    elif str(max(n_sum))[0] == "1" and int(str(max(n_sum))[1:]) in Sum:
        return [max(n_sum)[1:], date_process(date), detail]

    else:
        return [max(n_sum), date_process(date), detail]
