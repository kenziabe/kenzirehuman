import tweepy
import openai
import os
import time
from dotenv import load_dotenv

load_dotenv()

# APIキー読み込み
openai.api_key = os.getenv("OPENAI_API_KEY")

client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_KEY_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

TARGET_USERNAME = "ReHuman_parkour"

def generate_reply(tweet_text):
    prompt = f"このツイートに誠実で鋭い日本語のリプライを作成してください:\n\n{tweet_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

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