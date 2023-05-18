from Saramin import Saramin
from SlackBot import SlackBot

if __name__ == "__main__":
    # day(today: 오늘만, all: 전부)
    # save(true: csv 저장 O, false: csv 저장 X)
    # saramin = Saramin(day="today", save=True)
    saramin = Saramin(day="today", save=False)
    saramin.crawling()
    file_path = saramin.save_all_data_to_csv()
    slack_bot = SlackBot()
    # 파일로 전송
    slack_bot.send_file(file_path)
    # 메시지로 전송
    # for df in data:
        # slack_bot.send_all_message(df)
