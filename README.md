# Introduction
This repo includes a python file (streaming.py) that creates a Twitter API v2 Filtered Stream, then sends the streamed tweets to a Tinybird Data Source. There are several .pipe files that generate APIs from analytics on the tweets.

For more information about this project, check out [this blog post](https://www.tinybird.co/blog-posts/world-cup-sentiment).

# Get Started

## Create a Tinybird Workspace
Go to https://ui.tinybird.co/signup and create an account (if you don't have one). Create a Workspace, and then save your host (e.g. https://api.us-east.tinybird.co) and token as environment variables.

## Auth stuff
First, define your various tokens (Twitter/Tinybird) as environment variables (or handle the tokens however you want).

```python
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_KEY_SECRET = os.environ['TWITTER_API_KEY_SECRET']
TWITTER_BEARER_TOKEN = os.environ['TWITTER_BEARER_TOKEN']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
TB_TOKEN = os.environ['TB_TOKEN']
TB_HOST = os.environ['TB_HOST']
```

Note if you initialize a Tinybird data project using the [Tinybird CLI](https://www.tinybird.co/docs/quick-start-cli.html) you can access the host and token in the .tinyb file that gets created when you initialize a Tinybird data project and authenticate.

## Filtered Stream rules
The rules are set in the `set_filter()` function. The single rule in this code is in line 113 of streaming.py:

```python
rule = 'WorldCup OR "World Cup" OR Qatar2022 OR FIFA'
```

Change it as you see fit. See [this](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule) for more info about creating rules.
Keep in mind your tweet cap - a broad rule can eat into it very quickly!

## Stream tweets
Run the python script to start streaming tweets to Tinybird using the events API.

```bash
python3 streaming.py
```

## Creating APIs
There are several APIs already created as a part of the Tinybird data project. Feel free to explore them or create your own.

# Questions?
Check out the [Tinybird Docs](https://www.tinybird.co/docs) or give us a shout on [Slack](https://www.tinybird.co/join-our-slack-community)
