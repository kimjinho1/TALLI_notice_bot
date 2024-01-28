from Saramin import Saramin
from SlackBot import SlackBot
from bigquery import *
import shutil

if __name__ == "__main__":
    slack_bot = SlackBot()

    try:
        # day(today: 오늘만, all: 전부)
        # save(true: csv 저장 O, false: csv 저장 X)
        # saramin = Saramin(day="all", save=True)
        saramin = Saramin(day="today", save=False)

        # 기존에 저장되어 있던 채용 공고들 모두 확인(마감, 내용 수정)
        # 마감은 삭제, 수정의 경우에는 업데이트가 아니라 공고 삭제 후 다시 추가
        # check_position()

        saramin.crawling()
        file_path = saramin.save_all_data_to_csv()

    except:
        print("크롤링 중 에러가 발생했습니다!")
        slack_bot.send_message("크롤링 중 에러가 발생했습니다!")

    try:
        # 채용 공고 존재
        if file_path != "":
            # GCP BigQudry에 업로드
            insert_position(file_path)

            # Slack에 csv 파일 전송
            slack_bot.send_file(file_path)

            shutil.rmtree("result/")
        # 채용 공고 없음 -> "공고 없음" 메시지 전송
        else:
            print("오늘은 등록된 공고가 없습니다!")
            slack_bot.send_message("오늘은 등록된 공고가 없습니다!")
    
    except:
        print("크롤링 이후 에러가 발생했습니다!\n")
        slack_bot.send_message("크롤링 이후 에러가 발생했습니다!\n")
