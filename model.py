# 以下実行後、リスタートが必要
#!pip install --upgrade google-cloud-vision
from google.cloud import vision

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


def make_num(num):
    N = list(num)
    M = []  # 数値を入れる
    for n in N:
        try:
            M.append(int(n))
        except:
            continue
    return int("".join(str(i) for i in M))


def detect_text(path):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print(texts[0].description)
    # print("Texts:")
    y_sum = []
    for text in texts[10:]:
        if (
            "合計" in text.description
            or "合" in text.description
            or "計" in text.description
            or "上計" in text.description
            or "利用" in text.description
            or "Pay" in text.description
            or "P" in text.description
            or "a" in text.description
            or "y" in text.description
        ):
            # print(text.bounding_poly)
            # print(text.bounding_poly.vertices[0])
            # print(type(text.bounding_poly.vertices[0].y))
            y_sum.append(
                [text.bounding_poly.vertices[0].y, text.bounding_poly.vertices[2].y]
            )
            # print(f'\n"{text.description}"')
            # print()
    Sum = []
    # print(len(y_sum))
    for Y in y_sum:
        for text in texts[10:]:
            if (
                Y[0] <= text.bounding_poly.vertices[0].y <= Y[1]
                or Y[0] <= text.bounding_poly.vertices[2].y <= Y[1]
            ):
                if "," in text.description:
                    Sum.append(text.description.replace(",", ""))
                elif "." in text.description:
                    Sum.append(text.description.replace(".", ""))
                else:
                    Sum.append(text.description)

    n_sum = process_string(Sum)


    n_sum.reverse()
    element_counts = Counter(n_sum)
    max_element, max_count = element_counts.most_common(1)[0]
    if max_count > 1:
        return max_element
    else:
        return max(n_sum)


