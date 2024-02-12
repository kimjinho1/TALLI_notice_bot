import os
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
from datetime import datetime
import textwrap

from utils import getLogger

load_dotenv(verbose=True)

logger = getLogger("bigquery")

# 서비스 계정 인증 정보가 담긴 JSON 파일 경로
KEY_PATH = os.getenv("KEY_PATH")
# Credentials 객체 생성
credentials = Credentials.from_service_account_file(KEY_PATH)
# 빅쿼리 클라이언트 객체 생성
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# 채용 공고 테이블 ID
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
bigquery_position_table_id = f"{PROJECT_ID}.{DATASET_ID}.position"


def get_all_positions_df():
    query = textwrap.dedent(
        f"""
        SELECT *
        FROM `{bigquery_position_table_id}`
    """
    )
    try:
        positions_df = client.query(query).to_dataframe()
        logger.info(
            f"Get all position dataframe from big-query | total: {len(positions_df)}"
        )
        return positions_df
    except Exception as e:
        logger.error(f"Error get all position dataframe from big-query")
        logger.error(e)
        return None


def get_all_positions():
    query = textwrap.dedent(
        f"""
        SELECT *
        FROM `{bigquery_position_table_id}`
    """
    )
    try:
        positions = client.query(query).to_dataframe().to_dict(orient="records")
        logger.info(f"Get all position list from big-query | total: {len(positions)}")
        return positions
    except Exception as e:
        logger.error(f"Error get all position list from big-query")
        logger.error(e)
        return []


# BigQuery에 채용 공고 데이터 추가(CSV 파일)
def insert_positions_by_csv(file_path):
    df = pd.read_csv(file_path, encoding="utf-8")
    if len(df) == 0:
        return

    # TODO이유를 모르겠는데 종종 null로 채워지는 경우가 있어서 들어간 로직 => 이유 찾고 수정 필요함
    df.fillna("X", inplace=True)

    # 테이블 객체 생성
    table = client.get_table(bigquery_position_table_id)

    try:
        # 데이터프레임을 테이블에 삽입
        job_config = bigquery.LoadJobConfig()
        job = client.load_table_from_dataframe(df, table, job_config=job_config)

        # Wait for the job to complete
        job.result()
        logger.info(f"{len(df)} position data insertion using csv successfully.")

    except Exception as e:
        logger.error(f"Errors during position insertion using csv")
        logger.error(e)


# BigQuery에 채용 공고 데이터 일괄 추가
def insert_positions(positions):
    if len(positions) == 0:
        return

    df = pd.DataFrame(positions)

    # TODO이유를 모르겠는데 종종 null로 채워지는 경우가 있어서 들어간 로직 => 이유 찾고 수정 필요함
    df.fillna("X", inplace=True)

    # 테이블 객체 생성
    table = client.get_table(bigquery_position_table_id)

    try:
        # 데이터프레임을 테이블에 삽입
        job_config = bigquery.LoadJobConfig()
        job = client.load_table_from_dataframe(df, table, job_config=job_config)

        # Wait for the job to complete
        job.result()
        logger.info(f"{len(df)} position data insertion successfully.")

    except Exception as e:
        logger.error(f"Errors during position insertion")
        logger.error(e)


# BigQuery 채용 공고 데이터 삭제
def delete_position(id):
    query = textwrap.dedent(
        f"""
        DELETE FROM `{bigquery_position_table_id}`
        WHERE id = '{id}'
    """
    )

    results = client.query_and_wait(query)
    # TODO 실제로 삭제된 개수를 가져옫도록 수정 필요
    # logger.info(f"{results.total_rows} position data deleted successfully.")
    logger.info(f"1 position data deleted successfully.")

    # return results.total_rows
    return 1


# BigQuery 채용 공고 데이터 삭제
def delete_positions(positions):
    if len(positions) == 0:
        return 0

    id_list = ", ".join([f"'{str(id)}'" for id in positions])
    logger.info(f"Delete positions: total: {len(positions)}, id_list: [{id_list}]")
    query = textwrap.dedent(
        f"""
        DELETE FROM `{bigquery_position_table_id}`
        WHERE id IN ({id_list})
    """
    )

    results = client.query_and_wait(query)
    # TODO 실제로 삭제된 개수를 가져옫도록 수정 필요
    # logger.info(f"{results.total_rows} positions deleted successfully.")
    logger.info(f"{len(positions)} positions deleted successfully.")

    # return results.total_rows
    return len(positions)


def remove_duplicated_positions():
    positions = get_all_positions()

    unique_urls = set()
    unique_title = set()
    duplicate_position_ids = set()

    logger.info(f"Start check duplicated postion")

    for position in positions:
        url = position["url"]
        title = position["title"]
        if url not in unique_urls:
            unique_urls.add(url)
        elif title not in unique_title:
            unique_title.add(title)
        else:
            duplicate_position_ids.add(position["id"])

    if duplicate_position_ids:
        logger.info(f"{len(duplicate_position_ids)} duplicated positions detected.")
        delete_positions(duplicate_position_ids)
    else:
        logger.info(f"Duplicated positions not detected.")

    return len(duplicate_position_ids)


def get_potentially_removed_positions():
    positions = get_all_positions()

    closed_positions_by_time = set()
    positions_without_deadline = []
    current_date_time = datetime.now()

    for position in positions:
        id = position["id"]
        deadline = position["deadline"]
        if "채용" in deadline:
            positions_without_deadline.append(position)
            continue
        deadline_date_time = datetime.strptime(deadline, "%Y.%m.%d %H:%M")
        if current_date_time > deadline_date_time:
            closed_positions_by_time.add(id)

    logger.info(f"{len(closed_positions_by_time)} closed positions detected.")
    logger.info(
        f"{len(positions_without_deadline)} positions without deadline detected."
    )

    return closed_positions_by_time, positions_without_deadline
