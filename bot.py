import tweepy
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# OpenAIクライアント初期化
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Twitter API認証
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# 対象アカウント
TARGET_USERNAME = "ReHuman_parkour"

# ChatGPTで返信生成（OpenAI v1形式）
def generate_reply(tweet_text):
    prompt = f"このツイートに誠実で鋭い日本語のリプライを作成してください:\n\n{tweet_text}"
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたはX（旧Twitter）上で魅力的な返事をする知的なBotです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# メイン処理
try:
    user = client.get_user(username=TARGET_USERNAME)
    tweets = client.get_users_tweets(id=user.data.id, max_results=5)

    if tweets.data:
        latest_tweet = tweets.data[0]
        reply = generate_reply(latest_tweet.text)
        client.create_tweet(in_reply_to_tweet_id=latest_tweet.id, text=reply)
        print("送信済みリプライ：", reply)
    else:
        print("ツイートが見つかりませんでした。")

except tweepy.TooManyRequests:
    print("リクエストが多すぎます。15分待機します。")
    time.sleep(900)

except Exception as e:
    print("予期しないエラー：", str(e))