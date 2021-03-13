# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 17:07:44 2021

@author: Jian Cao

Collect Tweets from Twitter API
"""

## Set environment ------------------------------------------------------------
import time
import json
import requests
import uuid
import multiprocessing
from datetime import datetime, timedelta
from requests import HTTPError, ConnectionError
from TwitterAPI import TwitterAPI, TwitterConnectionError, TwitterRequestError

TWEET_EXPANSIONS = ['author_id', 'referenced_tweets.id', 'in_reply_to_user_id',
              'attachments.media_keys', 'attachments.poll_ids', 
              'geo.place_id', 'entities.mentions.username',
              'referenced_tweets.id.author_id', 'pinned_tweet_id']

TWEET_MEDIA_FIELDS = ['duration_ms', 'height', 'media_key',
                      'preview_image_url', 'type', 'url', 'width',
                      'public_metrics', 'non_public_metrics',
                      'organic_metrics', 'promoted_metrics']

TWEET_PLACE_FIELDS = ['contained_within', 'country', 'country_code',
                      'full_name', 'geo', 'id', 'name', 'place_type']

TWEET_POLL_FIELDS = ['duration_minutes', 'end_datetime', 'id',
                     'options', 'voting_status']

TWEET_FIELDS = ['attachments', 'author_id', 'context_annotations',
                'conversation_id', 'created_at', 'entities', 'geo',
                'id', 'in_reply_to_user_id', 'lang', 'non_public_metrics',
                'public_metrics', 'organic_metrics', 'promoted_metrics',
                'possibly_sensitive', 'referenced_tweets', 'reply_settings',
                'source', 'text', 'withheld']

TWEET_USER_FIELDS = ['created_at', 'description', 'entities',
                     'location', 'name', 'pinned_tweet_id',
                     'profile_image_url', 'protected', 'public_metrics',
                     'url', 'username', 'verified', 'withheld']

RESOURCES = {
    'SearchTweets.v1': {'resource': 'search/tweets',
                        'params_required': ['q'],
                        'params_optional': ['geocode', 'lang', 'locale',
                                            'result_type', 'count', 'until',
                                            'since_id', 'max_id', 
                                            'include_entities'],
                        'params_default': {'count': 100,
                                           'include_entities': 'true'},
                        'auth_type': 'oAuth2',
                        'api_version': '1.1',
                        'rate_limit': 450, # per 15 minutes (900 seconds)
                        'stream': False},
    
    'UserTimeLine.v1': {'resource': 'statuses/user_timeline',
                        'params_required': None,
                        'params_optional': ['user_id', 'screen_name',
                                            'since_id', 'max_id',
                                            'count', 'trim_user',
                                            'exclude_replies', 'include_rts'],
                        'params_default': {'count': 200,
                                           'trim_user': 'false',
                                           'exclude_replies': 'false',
                                           'include_rts': 'true'},
                        'auth_type': 'oAuth2',
                        'api_version': '1.1',
                        'rate_limit': 1500, # per 15 minutes (900 seconds)
                        'stream': False},
    
    'FilteredStream.v1':{'resource': 'statuses/filter',
                        'params_required': None,
                        'params_optional': ['follow', 'track',
                                            'locations', 'delimited',
                                            'stall_warnings'],
                        'params_default': {'delimited': 'length',
                                           'stall_warnings': 'true'},
                        'auth_type': 'oAuth1',
                        'api_version': '1.1',
                        'stream': True},
                        
    'Lab-Covid19':     {'resource': 'labs/1/tweets/stream/covid19',
                        'params_required': ['partition'],
                        'params_optional': None,
                        'params_default': None,
                        'auth_type': 'oAuth2',
                        'api_version': '1.1',
                        'stream': True},
                        
    'SearchTweets.v2': {'resource': 'tweets/search/recent',
                        'params_required': ['query'],
                        'params_optional': ['since_id', 'until_id',
                                            'start_time', 'end_time',
                                            'expansions', 'max_results',
                                            'media.fields', 'place.fields',
                                            'poll.fields', 'tweet.fields',
                                            'user.fields', 'next_token'],
                        'params_default': {'expansions': TWEET_EXPANSIONS,
                                           'max_results': 100,
                                           'media.fields': TWEET_MEDIA_FIELDS,
                                           'place.fields': TWEET_PLACE_FIELDS,
                                           'poll.fields': TWEET_POLL_FIELDS,
                                           'tweet.fields': TWEET_FIELDS,
                                           'user.fields': TWEET_USER_FIELDS},
                        'auth_type': 'oAuth2',
                        'api_version': '2',
                        'rate_limit': 450, # per 15 minutes (900 seconds)
                        'stream': False},
                                           
    'UserTimeLine.v2': {'resource': 'users/:PARAM/tweets',
                        'params_required': ['id'],
                        'params_optional': ['since_id', 'until_id',
                                            'start_time', 'end_time',
                                            'expansions', 'max_results',
                                            'media.fields', 'place.fields',
                                            'poll.fields', 'tweet.fields',
                                            'user.fields', 'pagination_token',
                                            'exclude'],
                        'params_default': {'expansions': TWEET_EXPANSIONS,
                                           'max_results': 100,
                                           'media.fields': TWEET_MEDIA_FIELDS,
                                           'place.fields': TWEET_PLACE_FIELDS,
                                           'poll.fields': TWEET_POLL_FIELDS,
                                           'tweet.fields': TWEET_FIELDS,
                                           'user.fields': TWEET_USER_FIELDS},
                        'auth_type': 'oAuth2',
                        'api_version': '2',
                        'rate_limit': 1500, # per 15 minutes (900 seconds)
                        'stream': False},
                                           
    'FilteredStream.v2':{'resource': 'tweets/search/stream',
                         'rules': 'tweets/search/stream/rules',
                        'params_required': ['id'],
                        'params_optional': ['expansions', 'media.fields',
                                            'place.fields', 'poll.fields',
                                            'tweet.fields','user.fields',],
                        'params_default': {'expansions': TWEET_EXPANSIONS,
                                           'media.fields': TWEET_MEDIA_FIELDS,
                                           'place.fields': TWEET_PLACE_FIELDS,
                                           'poll.fields': TWEET_POLL_FIELDS,
                                           'tweet.fields': TWEET_FIELDS,
                                           'user.fields': TWEET_USER_FIELDS},
                        'auth_type': 'oAuth2',
                        'api_version': '2',
                        'rate_limit': 50, # per 15 minutes (900 seconds)
                        'stream': True},
}
