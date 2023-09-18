from datetime import datetime, timedelta


# 어제 날짜 얻기
def get_yesterday_date():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%y/%m/%d")


# 오늘 날짜 얻기
def get_current_date():
    now = datetime.now()
    return now.strftime("%y/%m/%d")


# 같은 요일인지 확인
def check_same_day(job_day_text):
    create_or_update, date = job_day_text.split()
    # 등록일, 수정일 확인 -> 등록일만 체크
    if create_or_update == "수정일":
        return False
    # 등록일일 경우 date를 확인 -> 현재 날짜와 같은지 확인
    today_date = get_current_date()
    if create_or_update == "등록일" and date != today_date:
        return False
    return True


# 텍스트 필터링
def text_filter(text):
    text = text.strip().replace("\\xa0", " ").replace("\n", "")
    while text.find("  ") != -1:
        text = text.replace("  ", " ")
    if text[-1] == ",":
        text = text[:-1]
    return text


def job_location_filter(text):
    text = text_filter(text)
    text_li = text.split()
    maybe_zip_code = text_li[0].strip()
    if maybe_zip_code[0] == "(" and maybe_zip_code[-1] == ")":
        text = " ".join(text_li[1:])
    return text


def contact_info_filter(text):
    if len(text) == 9:
        text = text[:2] + "-" + text[2:5] + "-" + text[5:]
    return text


def experience_filter(text):
    if "무관" in text or ("신입" in text and "경력" in text):
        return "경력 무관"
    elif "신입" in text:
        return "신입"
    elif "경력" in text:
        return "경력"
    return "경력 무관"


def education_filter(text):
    if ("대졸(2,3년제)" in text) or ("3년" in text) or ("2년" in text):
        return "초대졸 이상 (2, 3년제)"
    elif "대졸(4년제)" in text:
        return "대졸 이상 (4년제)"
    elif ("고교졸업" in text) or ("고졸" in text):
        return "고졸 이상"
    return "학력무관"


def job_type_filter(text):
    if ("아르바이트" in text) or ("알바" in text):
        return "아르바이트"
    elif "인턴" in text:
        return "인턴"
    elif "프리랜서" in text:
        return "프리랜서"
    elif "계약" in text:
        return "계약직"
    elif "정규" in text:
        return "정규직"
    return "정규직1234"
