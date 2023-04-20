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
    # today_date = get_current_date()
    today_date = get_yesterday_date()
    if create_or_update == "등록일" and date != today_date:
        return False
    return True

def text_filter(text):
    text = text.strip().replace("\\xa0", " ").replace("\n", '')
    while (text.find("  ") != -1):
        text = text.replace("  ", " ")
    return text

def print_data(data):
    print("url:", data["url"])
    print("기업명:", data["기업명"])
    print("공고명:", data["공고명"])
    print("스크랩 수:", data["스크랩 수"])
    print("경력:", data["경력"])
    print("학력:", data["학력"])
    print("근무형태:", data["근무형태"])
    print("급여:", data["급여"])
    print("근무지역:", data["근무지역"])
    print("필수사항:", data["필수사항"])
    print("우대사항:", data["우대사항"])
    print("접수 시작일:", data["접수 시작일"])
    print("접수 마감일:", data["접수 마감일"])

if __name__ == "__main__":
    print(get_yesterday_date())
    print(get_current_date())