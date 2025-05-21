import tweepy
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# .envから環境変数を読み込む
load_dotenv()

# OpenAIクライアント初期化（gpt-3.5使用中）
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Twitter APIクライアント
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# リプライ対象のアカウント
TARGET_USERNAME = "ReHuman_parkour"

# ChatGPTでリプライを生成
def generate_reply(tweet_text):
    prompt = f"このツイートに誠実で鋭い日本語のリプライを作成してください:\n\n{tweet_text}"
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # GPT-4解放後に "gpt-4" に変更OK
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
    print("リクエスト過多。15分休憩します。")
    time.sleep(900)

except Exception as e:
    print("予期しないエラー：", str(e))