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