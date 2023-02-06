import configparser as ConfigParser
import io
import praw
import time
import json
import requests
import traceback

POLL_TIME = 5 # PRAW has a model for polling, but Im too lazy to learn it


def send_slack_msg(msg, webhook_url):
    slack_msg = {"text": msg}
    response = requests.post(webhook_url, data=json.dumps(slack_msg),
            headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise Exception


if __name__ == "__main__":
    with open("api-keys.ini", "r") as f:
        config_data = f.read()

    config = ConfigParser.ConfigParser()
    config.read('api-keys.ini')

    reddit_id = config.get("reddit", "reddit_id")
    reddit_secret = config.get("reddit", "reddit_secret")
    reddit_post = config.get("reddit", "reddit_post")
    slack_webhook = config.items("slack")
    reddit = praw.Reddit(
            user_agent="rd2 milb bot", 
            client_id=reddit_id, client_secret=reddit_secret)

    old_comments = []

    submission = reddit.submission(url = reddit_post)
    for comment in submission.comments:
        old_comments.append(comment.id)


    while True:
        try:
            submission = reddit.submission(url = reddit_post)
            for comment in submission.comments:
                if comment.id not in old_comments:
                    slack_msg = comment.body + \
                            '\n<http://reddit.com' + comment.permalink + '|Link>'
                    for keys, webhook in slack_webhook:
                        send_slack_msg(slack_msg, webhook)
                    old_comments.append(comment.id)
            time.sleep(POLL_TIME)
        #except qpraw.prawcore.exceptions.RequestException:
        except:
            print("Reddit timeout most likely")
            traceback.print_exc()
            time.sleep(10)
