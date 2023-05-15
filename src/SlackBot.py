import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv(verbose=True)


class SlackBot:
    def __init__(self):
        self.app = App(token=os.getenv("SLACK_BOT_TOKEN"))
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    def make_message(self, df, idx):
        message = ""
        cols = df.columns.tolist()
        for col in cols:
            message += f"{col}: {df.loc[idx, col]}\n"
        return message

    def send_message(self, message):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
            return response
        except SlackApiError as e:
            print(f"Error sending message: {e}")
            return None

    def send_all_message(self, df):
        for i in range(len(df)):
            if (i >= 20):
                return
            message = self.make_message(df, i)
            self.send_message(message)
