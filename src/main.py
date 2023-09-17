from Saramin import Saramin
from SlackBot import SlackBot

if __name__ == "__main__":
    # day(today: 오늘만, all: 전부)
    # save(true: csv 저장 O, false: csv 저장 X)
    saramin = Saramin(day="all", save=True)
    # saramin = Saramin(day="today", save=False)
    saramin.crawling()
    file_path = saramin.save_all_data_to_csv()

    exit()
    # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46592408&location=ts&searchword=%EB%B3%B4%ED%97%98%EC%8B%AC%EC%82%AC&searchType=search&paid_fl=n&search_uuid=e1cb7765-3457-45dc-8d51-df54a61995b2
    # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46512518&location=ts&searchword=CRA&searchType=search&paid_fl=n&search_uuid=bf65d6ab-334c-47f1-99c2-3d0ca857364b

    slack_bot = SlackBot()
    if (file_path != ""): 
        # 채용 공고 존재함 -> 파일 전송
        slack_bot.send_file(file_path)
    else:
        # 채용 공고 없음 -> 메시지 전송
        slack_bot.send_message("오늘은 등록된 공고가 없습니다!")
