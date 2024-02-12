import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

load_dotenv(verbose=True)

import certifi
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
ssl_context = ssl.create_default_context(cafile=certifi.where())


class SlackBot:
    def __init__(self):
        self.app = App(token=os.getenv("SLACK_BOT_TOKEN"))
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"), ssl=ssl_context)
        self.cnt = 1

    # 메시지 생성
    def make_message(self, df, idx):
        message = f"# {self.cnt}번째\n"
        cols = df.columns.tolist()
        for col in cols:
            if col == "url":
                message += f"{col}: `{df.loc[idx, col]}`\n"
            else:
                message += f"{col}: {df.loc[idx, col]}\n"
        return message

    # 메시지 전송
    def send_message(self, message):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id, text=message
            )
            return response
        except SlackApiError as error:
            print(f"Error sending message: {error}")
            return None

    # 모든 메시지 전송
    def send_all_message(self, df):
        for i in range(len(df)):
            if i >= 10:
                return
            message = self.make_message(df, i)
            self.send_message(message)
            self.cnt += 1
            time.sleep(30)

    # 파일 전송
    def send_file(self, file_path):
        try:
            response = self.client.files_upload_v2(
                channel=self.channel_id,
                file=file_path,
            )
            return response
        except SlackApiError as error:
            print(f"Error sending message: {error}")
            return None
