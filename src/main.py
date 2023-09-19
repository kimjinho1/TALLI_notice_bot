from Saramin import Saramin
from SlackBot import SlackBot
from bigquery import *

if __name__ == "__main__":
    # day(today: 오늘만, all: 전부)
    # save(true: csv 저장 O, false: csv 저장 X)
    # saramin = Saramin(day="all", save=True)
    saramin = Saramin(day="today", save=False)
    saramin.crawling()
    file_path = saramin.save_all_data_to_csv()

    slack_bot = SlackBot()
    # 채용 공고 존재
    if file_path != "":
        # GCP BigQudry에 업로드
        insert_position(file_path)

        # Slack에 csv 파일 전송
        slack_bot.send_file(file_path)

        os.remove(file_path)
    # 채용 공고 없음 -> "공고 없음" 메시지 전송
    else:
        slack_bot.send_message("오늘은 등록된 공고가 없습니다!")

    os.rmdir("result/")
