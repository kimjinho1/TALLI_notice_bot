from dotenv import load_dotenv
import os 
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App

load_dotenv(verbose=True)
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
channel_id = os.getenv("SLACK_CHANNEL_ID")

def send_slack_message(message):
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e}")
        return None

df = pd.read_csv('result/CRA-23-04-29.csv')
cols = df.columns.tolist()
for i in range(len(df)):
    message = ""
    for col in cols:
        message += f"{col}: {df.loc[i, col]}\n"
    print(message)
    send_slack_message(message)
    exit()