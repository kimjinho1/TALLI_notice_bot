from datetime import datetime, timedelta


def get_yesterday_date():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%y/%m/%d")


def get_current_date():
    now = datetime.now()
    return now.strftime("%y/%m/%d")


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


def text_filter(text):
    text = text.strip().replace("\\xa0", " ").replace("\n", '')
    while (text.find("  ") != -1):
        text = text.replace("  ", " ")
    return text
