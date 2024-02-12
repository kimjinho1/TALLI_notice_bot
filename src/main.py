from Saramin import Saramin
from SlackBot import SlackBot
from bigquery import *
from utils import get_current_date
import shutil

slack_bot = SlackBot()


if __name__ == "__main__":
    # day(today: 오늘만, all: 전부)
    day = "today"
    # day = "all"

    # save(true: keyward 별 csv 저장 O, false: keyword 별 csv 저장 X)
    # saramin = Saramin(day, save=True)
    saramin = Saramin(day, save=False)
    try:
        # 중복 채용 공고 삭제(title, url)
        remove_cnt_by_duplicate = remove_duplicated_positions()

        # 저장된 채용 공고들 마감 여부 확인 -> 마감 되었을 시 삭제
        closed_positions_by_time, positions_without_deadline = (
            get_potentially_removed_positions()
        )
        closed_positions_by_company = saramin.get_closed_positions(
            positions_without_deadline
        )
        remove_cnt_by_time = delete_positions(closed_positions_by_time)
        remove_cnt_by_company = delete_positions(closed_positions_by_company)

        # 저장된 채용 공고들 업데이트 여부 확인 -> 업데이트 되었을 시 삭제 후 다시 추가
        positions = get_all_positions()
        updated_position_ids, updated_positions = saramin.get_updated_positions(
            positions
        )
        remove_cnt_for_update = delete_positions(updated_position_ids)
        insert_positions(updated_positions)

        res = textwrap.dedent(
            f"""
            삭제된 공고 개수(기한 지남): {remove_cnt_by_time}
            삭제된 공고 개수(채용 마감): {remove_cnt_by_company}
            삭제된 중복 채용 공고 개수: {remove_cnt_by_duplicate}
            수정된 채용 공고 개수: {len(updated_position_ids)}
        """
        )

        saramin.crawling()
        file_path = saramin.save_all_data_to_csv()

        slack_bot.send_message(res)

    except Exception as e:
        print(e)
        print("크롤링 중 에러가 발생했습니다!")
        # slack_bot.send_message("크롤링 중 에러가 발생했습니다!")

    try:
        # 채용 공고 존재
        if file_path != "":
            # GCP BigQudry에 업로드
            insert_positions_by_csv(file_path)

            # Slack에 csv 파일 전송
            slack_bot.send_file(file_path)
            today = get_current_date(sep="-")
            saramin_log_file_path = os.path.join("log", today, "saramin.log")
            bigquery_log_file_path = os.path.join("log", today, "bigquery.log")
            slack_bot.send_file(saramin_log_file_path)
            slack_bot.send_file(bigquery_log_file_path)

            shutil.rmtree("result/")
        # 채용 공고 없음 -> "공고 없음" 메시지 전송
        else:
            print("오늘은 등록된 공고가 없습니다!")
            slack_bot.send_message("오늘은 등록된 공고가 없습니다!")
    except Exception as e:
        print(e)
        print("크롤링 이후 에러가 발생했습니다!\n")
        # slack_bot.send_message("크롤링 이후 에러가 발생했습니다!\n")
