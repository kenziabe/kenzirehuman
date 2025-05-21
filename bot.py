import tweepy
import openai
import os
from dotenv import load_dotenv

# .env 読み込み
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

# リプライ対象のアカウント名
TARGET_USERNAME = "ReHuman_parkour"

# 最新ツイートを取得
user = client.get_user(username=TARGET_USERNAME)
tweets = client.get_users_tweets(id=user.data.id, max_results=5)
latest_tweet = tweets.data[0]

# ChatGPTで返信生成
def generate_reply(tweet_text):
    prompt = f"このツイートに、誠実かつ鋭い日本語のリプライを返してください:\n\n{tweet_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

# 返信投稿
reply = generate_reply(latest_tweet.text)
client.create_tweet(in_reply_to_tweet_id=latest_tweet.id, text=reply)

print("送信済みリプライ：", reply)