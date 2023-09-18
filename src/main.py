from Saramin import Saramin
from SlackBot import SlackBot

if __name__ == "__main__":
    # day(today: 오늘만, all: 전부)
    # save(true: csv 저장 O, false: csv 저장 X)
    # saramin = Saramin(day="all", save=True)
    saramin = Saramin(day="today", save=False)
    saramin.crawling()
    file_path = saramin.save_all_data_to_csv()

    slack_bot = SlackBot()
    if file_path != "":
        # 채용 공고 존재함 -> 파일 전송
        slack_bot.send_file(file_path)
    else:
        # 채용 공고 없음 -> 메시지 전송
        slack_bot.send_message("오늘은 등록된 공고가 없습니다!")
