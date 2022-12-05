import tweepy
import json
from datetime import datetime
import requests
from io import StringIO
import time
from threading import Timer
import sys
import os

TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_KEY_SECRET = os.environ['TWITTER_API_KEY_SECRET']
TWITTER_BEARER_TOKEN = os.environ['TWITTER_BEARER_TOKEN']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
TB_TOKEN = os.environ['TB_TOKEN']
TB_HOST = os.environ['TB_HOST']


class TinybirdApiSink():
    def __init__(self, host, token, datasource):
        super().__init__()
        self.token = token
        self.host = host
        self.datasource = datasource
        self.url = f'{self.host}/v0/events'
        self.reset()
        self.wait = False

    def reset(self):
        self.chunk = StringIO()

    def append(self, value):
        try:
            self.chunk.write(json.dumps(value) + '\n')
        except Exception as e:
            print(e)

    def tell(self):
        return self.chunk.tell()

    def flush(self):
        self.wait = True
        data = self.chunk.getvalue()
        self.reset()
        params = {
            'name': self.datasource,
            'token': self.token,
            'host': self.host
        }

        ok = False
        try:
            response = requests.post(self.url, params=params, data=data)
            print('flush response')
            print(response.text)
            ok = response.status_code < 400
            self.wait = False
            return ok
        except Exception as e:
            self.wait = False
            print(e)
            return 

class MyStreamingClient(tweepy.StreamingClient):

    def __init__(self, name, bearer_token, datasource, token, host):
        super().__init__(bearer_token)
        self.name = name
        self.bearer_token = bearer_token
        self.datasource = datasource
        self.token = token
        self.host = host
        self.sink = TinybirdApiSink(host, token, datasource)
        self.wait_on_rate_limit=True
        self.chunk_size=1024*10
        self.records = 0
        self.timer = None
        self.timer_start = None
        self.tr_timer = None
        self.tr_timer_start = None
        self.max_wait_records = 10000
        self.max_wait_bytes = 1024*1024*1
        self.max_wait_seconds = 10
    
    def append(self, record):
        if self.records % 100 == 0:
            print('append')
        self.sink.append(record)
        self.records += 1
        if self.records < self.max_wait_records and self.sink.tell() < self.max_wait_bytes:
            if not self.timer:
                self.timer_start = time.monotonic()
                self.timer = Timer(self.max_wait_seconds, self.flush)
                self.timer.name = f"f{self.name}_timer"
                self.timer.start()
        else:
            self.flush()

    def flush(self):
        print('flush')
        if self.timer:
            self.timer.cancel()
            self.timer = None
            self.timer_start = None
        if not self.records:
            return
        self.sink.flush()
        self.records = 0
    
    def set_filter(self):
        print('set filter rules')
        rule = 'WorldCup OR "World Cup" OR Qatar2022 OR FIFA'
        self.add_rules(tweepy.StreamRule(value = rule))


    def on_data(self, raw_data):
        while self.sink.wait:
            print('wait flush')
            time.sleep(1)
        
        super().on_data(raw_data)
        json_data = json.loads(raw_data)
        tweet = json_data['data']

        if 'created_at' not in tweet:
            timestamp  = datetime.now()
        else: timestamp = datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        text = tweet['text']

        tt = {
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'tweet': text,
        }
        
        self.append(tt)


def connect():
    try:
        streaming_client = MyStreamingClient('sc', TWITTER_BEARER_TOKEN, 'tweets_match', TB_TOKEN, TB_HOST)
        print('created client')
        if streaming_client.get_rules().data == None:
            streaming_client.set_filter()
        else:
            streaming_client.delete_rules(d.id for d in streaming_client.get_rules().data)
            streaming_client.set_filter()
        streaming_client.filter(tweet_fields=['text', 'created_at'])
    except KeyboardInterrupt as e:
        print('Stopped')
        streaming_client.disconnect()
        exit()
    except Exception as e:
        print(e)
        streaming_client.disconnect()


while True:
    print('connect')
    try:
        connect()
    except Exception as e:
        exit()
