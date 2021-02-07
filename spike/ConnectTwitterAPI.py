# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 09:28:54 2021

@author: Jian Cao

Collect Tweets from Twitter API (Stream, REST, Lab-COVID19)
"""

## Set environment ------------------------------------------------------------
# import os
import time
import json
import requests
import uuid
from datetime import datetime, timedelta
from requests import HTTPError, ConnectionError
from JianTwitterAPI import JianTwitterAPI
from TwitterAPI import TwitterAPI, TwitterConnectionError, TwitterRequestError 

## Define class ---------------------------------------------------------------
class ConnectTwitterAPI:
    """Object that connects Twitter API (Stream, REST, Lab-COVID19)
    Functions:
        
    """
    
    def __init__(self, consumer_key, consumer_secret,
                 access_token_key, access_token_secret):
        if (not consumer_key or not consumer_secret or not
                 access_token_key or not access_token_secret):
            raise ValueError('COMSUMER KEY&SECRET, ACCESS KEY&SECRET are needed.')
        
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret


    def GetBearerToken(self, key, secret):
        response = requests.post("https://api.twitter.com/oauth2/token",
                                 auth=(key, secret),
                                 data={'grant_type': 'client_credentials'},
                                 headers={"User-Agent": "BEBOBEBOP"})
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            raise Exception("Bearer token error")
        body = response.json()
        print("Bearer token is ready.")
        return body['access_token']


    def _get_ready(self):
        self.twitter_api = None
        self.bearer_token = None
        if 'stream_v1' in self.api_type:
            self.twitter_api = TwitterAPI(self.consumer_key,
                                         self.consumer_secret,
                                         self.access_token_key,
                                         self.access_token_secret)
            print('Stream API v1.1 is ready.')
        if 'rest_v1' in self.api_type:
            self.twitter_api = TwitterAPI(self.consumer_key,
                                         self.consumer_secret,
                                         auth_type='oAuth2')
            print('REST API v1.1 is ready.')
        if 'lab_covid19' in self.api_type:
            self.twitter_api = JianTwitterAPI(self.consumer_key,
                                         self.consumer_secret,
                                         auth_type='oAuth2')
            print('Lab API COVID19 is ready.')
        if any(x in self.api_type for x in ['stream_v2', 'rest_v2']): # modify this to use TwitterAPI
            self.bearer_token = self.GetBearerToken(self.consumer_key,
                                                    self.consumer_secret)


    def _request_stream_v1(self):
        if any(x not in self.input_dict for x in
               ['keywords']):
            raise ValueError('KEYWORDS is needed.')
        # prepare params 
        params = {'track': self.input_dict['keywords']} # add more rules in the params as needed
        # make request
        response = self.twitter_api.request('statuses/filter', params)
        return(response)


    def _request_rest_v1(self):
        if any(x not in self.input_dict for x in
               ['keywords', 'max_id', 'since_id']):
            raise ValueError('KEYWORDS, MAX_ID, and SINCE_ID are needed.')
        # prepare params
        keywords = '(' + ') OR ('.join(self.input_dict['keywords']) + ')'
        params = {'q': keywords,
                 'max_id': self.input_dict['max_id'],
                 'since_id': self.input_dict['since_id'],
                 'count': 100,
                 'tweet_mode': 'extended'}
        if 'tweets_per_qry' in self.input_dict:
            params['count'] = self.input_dict['tweets_per_qry']
        # make request
        response = self.twitter_api.request('search/tweets', params)
        return(response)


    def _request_lab_covid19(self):
        if any(x not in self.input_dict for x in
               ['partition']):
            raise ValueError('PARTITION is needed.')
        # prepare params
        params = {'partition': self.input_dict['partition']}
        # make request
        response = self.twitter_api.request('labs/1/tweets/stream/covid19',
                                            params)
        return(response)


    def _collect_tweets(self):
        if 'rest_v1' in self.api_type:
            n_tweets = 0
            response = self._request_rest_v1()
            self.request_headers = response.headers
            if not response.json() or 'statuses' not in response.json():
                raise TypeError ('"statuses" not in response.json().')
            tweets = response.json()['statuses']
            n_tweets = len(tweets)
            for tweet in tweets:
                self._data_outlet(tweet)
            if n_tweets == 0:
                print('No more tweets found.')
                self._data_outlet(None)
                return(False)
            self.tweet_count += n_tweets
            print('Downloaded {} tweets.'.format(self.tweet_count))
            self.input_dict['max_id'] = tweet['id'] - 1
        
        if any(x in self.api_type for x in ['stream_v1', 'lab_covid19']):
            if 'stream_v1' in self.api_type:
                response = self._request_stream_v1()
            else:
                response = self._request_lab_covid19()
            if response.status_code != 200:
                print(response.headers)
                raise ConnectionError(response.text)
            self.request_headers = response.headers
            print('Collecting tweets...')
            for item in response:
                if 'text' in item:
                    self._data_outlet(tweet)
                elif 'disconnect' in item:
                    event = item['disconnect']
                    if event['code'] in [2,5,6,7]:
                        raise Exception(event['reason']) # something needs to be fixed before re-connecting
                    else:
                        print(('Disconnect Code: ' + event['code'] +
                              '. Reason: ' + event['reason']))
                        return(True) # temporary interruption, re-try request
        return(True)


    def _data_outlet(self, tweet):
        if 'local' in self.outlet_type:
            if any(x not in self.input_dict for x in
                   ['file_prefix', 'download_path']):
                raise ValueError('FILE_PREFIX, DOWNLOAD_PATH are needed.')
            # append tweet
            if tweet:
                self.tweets.append(tweet)
            # determine if a file is ready
            if 'count' in self.outlet_type:
                file_is_ready = len(self.tweets) >= self.tweets_per_file
            else:
                if not isinstance(self.file_timer, datetime):
                    self.file_timer = datetime.now()
                file_is_ready = (datetime.now() - self.file_timer >=
                                 self.minutes_per_file)
            # file is not ready, continue adding tweets
            if not file_is_ready and tweet:
                return(None)
            # save file
            tweet_time = self.tweets[-1]['created_at']
            time_format = '%a %b %d %H:%M:%S %z %Y'
            if 'v2' in self.api_type:
                tweet_time = tweet_time[:-5]
                time_format = '%Y-%m-%dT%H:%M:%S'
            file_time = datetime.strptime(tweet_time,
                                          time_format)
            file_name = (self.input_dict['file_prefix'] + 
                        file_time.strftime("-%Y-%m-%d-%H-%M-%S-") +
                        str(uuid.uuid4()) + 
                        '.txt')
            with open(self.input_dict['download_path'] +
                      file_name, 'w') as file:
                file.write(json.dumps(self.tweets))
            if 'count' in self.outlet_type:
                print(file_name + ' is saved.')
            else:
                print('{} ----- {} tweets'.format(str(file_time),
                      str(len(self.tweets))))
            # clean self.tweets
            self.tweets = []


    def Start(self, input_dict,
              api_type = 'stream_v1',
              outlet_type = 'local'):
        """Start the monitor
        Parameters:     
           input_dict (dict): dict of input parameters 
                               (parameters, start_id, end_id, etc).
           api_type (str): type of API: stream, REST, lab-covid19
           outlet_type (str): type of outlet: local disk, pubsub,
                               kinesis, Oracle stream.
        Returns:     
           None
        """ 
        
        if not api_type or not outlet_type:
            raise ValueError('API_TYPE and OUTLET_TYPE are needed.')
        self.input_dict = input_dict
        self.api_type = api_type.lower()
        self.outlet_type = outlet_type.lower()
        self._get_ready()
        if 'count' in self.outlet_type:
            self.tweets_per_file = 15000
            self.tweet_count = 0
            if 'tweets_per_file' in self.input_dict:
                self.tweets_per_file = self.input_dict['tweets_per_file']
        else:
            self.minutes_per_file = timedelta(minutes = 15)
            self.file_timer = None
            if 'minutes_per_file' in self.input_dict:
                self.minutes_per_file = timedelta(
                        minutes = int(self.input_dict['minutes_per_file']))
        self.tweets = []
        # start monitor
        last_error = datetime.now()
        error_count = 0
        go = True
        while go:
            retry = False
            try:
                go = self._collect_tweets()
            except IOError as ioe:
                print('[Caught IOError]\n' + str(ioe))
                retry = True
            except HTTPError as he:
                print('[Caught HTTPError]\n' + str(he))
                retry = True
            except ConnectionError as ce:
                print('[Caught ConnectionError]\n' + str(ce))
                retry = True
            except TypeError as te:
                print('[Caught TimeoutError]\n' + str(te))
                retry = True
            except TwitterConnectionError as tce:
                print('[Caught TwitterConnectionError]\n' + str(tce))
                retry = True
            except TwitterRequestError as tre:
                print('[Caught TwitterRequestError]\n' + str(tre))
                retry = True
            # retry strategy                    need to re-write this
            if not retry:
                if 'rest_v1' in self.api_type:
                    time.sleep(2.1)
                continue
            print(self.request_headers)
            if datetime.now() - last_error > timedelta(seconds = 900):
                error_count = 0
            wait = min(0.25 * 2**error_count, 30)
            last_error = datetime.now()
            error_count += 1
            print('Wait {} seconds before retrying...'.format(wait))
            time.sleep(wait)
            


                


