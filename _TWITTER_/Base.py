#BASE.modules._Twitter_.Base

import asyncio, twitter, time, requests

async def ensure_connection(BASE):
	oauth = twitter.OAuth(
						#OAuth(token, token_key, con_secret, con_secret_key)
						BASE.access.Twitter.api_token,
						BASE.access.Twitter.api_token_key,
						BASE.access.Twitter.consumer_key,
						BASE.access.Twitter.consumer_secret
						)

	return twitter.Twitter(auth=oauth)

async def send_tweet(BASE, tweet):
	api = await ensure_connection(BASE)
	api.statuses.update(status=tweet[:140])
