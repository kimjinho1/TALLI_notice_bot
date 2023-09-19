import os
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.cloud import bigquery

load_dotenv(verbose=True)

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


# BigQuery에 채용 공고 데이터 추가
def insert_position(file_path):
    df = pd.read_csv(file_path, encoding="utf-8")

    # 테이블 객체 생성
    table = client.get_table(bigquery_position_table_id)

    # 데이터프레임을 테이블에 삽입
    client.load_table_from_dataframe(df, table)


def check_position():
    query = f"""
        SELECT *
        FROM `{bigquery_position_table_id}`
    """
    check = client.query(query).to_dataframe()
    print(check)
