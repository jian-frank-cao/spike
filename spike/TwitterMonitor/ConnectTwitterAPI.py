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
import multiprocessing
from datetime import datetime, timedelta
from requests import HTTPError, ConnectionError
from TwitterAPI import TwitterAPI, TwitterConnectionError, TwitterRequestError

## Define class ---------------------------------------------------------------
class ConnectTwitterAPI:
    """Object that connects Twitter API (Stream, REST, Lab-COVID19)
    Functions:
        StartMonitor(input_dict, api_type, outlet_type)
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


    def GetBearerToken(self, key, secret):  # might not be necessary if use TwitterAPI
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
        # check input
        if not any([x == self.api_type for 
                x in ['stream_v1', 'rest_v1', 'lab_covid19']]): # add stream_v2, rest_v2
            raise Exception('API ' + self.api_type + 
                            ' is not currently supported')
        if not any([x == self.outlet_type for 
                x in ['local', 'local_count']]): # add pubsub, kinesis, oracle stream
            raise Exception('OUTLET ' + self.outlet_type + 
                            ' is not currently supported')

        # authorization
        if self.api_type == 'stream_v1':
            self.twitter_api = TwitterAPI(self.consumer_key,
                                         self.consumer_secret,
                                         self.access_token_key,
                                         self.access_token_secret)
            print('oAuth1 is ready.')
        if any(x == self.api_type for x in ['rest_v1', 'lab_covid19']):
            self.twitter_api = TwitterAPI(self.consumer_key,
                                         self.consumer_secret,
                                         auth_type='oAuth2')
            print('oAuth2 is ready.')
        if any(x == self.api_type for x in ['stream_v2', 'rest_v2']): # modify this to use TwitterAPI
            self.bearer_token = self.GetBearerToken(self.consumer_key,
                                                    self.consumer_secret)
        
        # prepare requests
        if self.api_type == 'stream_v1':
            if any(x not in self.input_dict for x in
               ['keywords']):
                raise ValueError('KEYWORDS is needed.')
            self.resource = 'statuses/filter'
            self.params = {'track': self.input_dict['keywords']} # add more rules in the params as needed
        
        if self.api_type == 'rest_v1':
            if any(x not in self.input_dict for x in
                   ['keywords', 'max_id', 'since_id']):
                raise ValueError('KEYWORDS, MAX_ID, and SINCE_ID are needed.')
            keywords = '(' + ') OR ('.join(self.input_dict['keywords']) + ')'
            self.resource = 'search/tweets'
            self.params = {'q': keywords,
                     'max_id': self.input_dict['max_id'],
                     'since_id': self.input_dict['since_id'],
                     'count': 100,
                     'tweet_mode': 'extended'}
            if 'tweets_per_qry' in self.input_dict:
                self.params['count'] = self.input_dict['tweets_per_qry']
            self.tweet_downloaded = 0
        
        if self.api_type == 'lab_covid19':
            if any(x not in self.input_dict for x in
                   ['partition']):
                raise ValueError('PARTITION is needed.')
            self.params = {'partition': self.input_dict['partition']}
            self.resource = 'labs/1/tweets/stream/covid19'
        
        # prepare outlet
        if not hasattr(self, 'pipe_in') or not hasattr(self, 'pipe_out'):
            self.pipe_in, self.pipe_out = multiprocessing.Pipe()
        if ('local' in self.outlet_type and 
            not hasattr(self, 'tweets')):
            self.tweets = []
            self.tweet_count = 0
        if self.outlet_type == 'local_count':
            self.tweets_per_file = 15000
            if 'tweets_per_file' in self.input_dict:
                self.tweets_per_file = self.input_dict['tweets_per_file']
        if self.outlet_type == 'local':
            self.minutes_per_file = timedelta(minutes = 15)
            if 'minutes_per_file' in self.input_dict:
                self.minutes_per_file = timedelta(
                    minutes = float(self.input_dict['minutes_per_file']))
        if any(x not in self.input_dict for x in
               ['file_prefix', 'download_path']):
            raise ValueError('FILE_PREFIX, DOWNLOAD_PATH are needed.')


    def _request_stream_v1(self):
        self.response = self.twitter_api.request(self.resource,
                                                 self.params)
        if 'stream_v1' in self.api_type:
            print('Connected to Stream API v1.1.')
            print('First 10 keywords: ' +
                  ', '.join(self.input_dict['keywords'][:10]) + '.')
        else:
            print(('Connected to Lab API COVID19 partition ' +
                   str(self.input_dict['partition'])))
        print('Collecting tweets...')
        for tweet in self.response:
            if 'text' in tweet:
                self.pipe_in.send(tweet)
            elif 'disconnect' in tweet:
                event = tweet['disconnect']
                if event['code'] in [2,5,6,7]:
                    raise Exception(event['reason']) # something needs to be fixed before re-connecting
                else:
                    print(('Disconnect Code: ' + event['code'] +
                          '. Reason: ' + event['reason']))
                    return(True) # temporary interruption, re-try request
        return(True) # stream stopped with no reason, re-try request


    def _request_rest_v1(self):
        self.response = self.twitter_api.request(self.resource,
                                                 self.params)
        if (not self.response.json() or 
            'statuses' not in self.response.json()):
            raise TypeError ('"statuses" not in response.json().')
        tweets = self.response.json()['statuses']
        n_tweets = len(tweets)
        for tweet in tweets:
            self.pipe_in.send(tweet)
        if n_tweets == 0:
            print('No more tweets found.')
            self.pipe_in.send("FINISHED")
            return(False)
        self.tweet_downloaded += n_tweets
        print('Downloaded {} tweets.'.format(self.tweet_downloaded))
        self.input_dict['max_id'] = tweet['id'] - 1
        return(True)


    def _collect_tweets(self):
        last_error = None
        go = True
        while go:
            retry = False
            try:
                if any(x in self.api_type for 
                       x in ['stream_v1', 'lab_covid19']):
                    go = self._request_stream_v1()
                if 'rest_v1' in self.api_type:
                    go = self._request_rest_v1()
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
                print('[Caught TypeError]\n' + str(te))
                retry = True
            except TwitterConnectionError as tce:
                print('[Caught TwitterConnectionError]\n' + str(tce))
                retry = True
            except TwitterRequestError as tre:
                print('[Caught TwitterRequestError]\n' + str(tre))
                retry = True
            # retry strategy 
            if not retry:
                if 'rest_v1' in self.api_type:
                    time.sleep(2.1)
                continue
            print(self.response.headers)
            self.response.close()
            if not last_error:
                last_error = datetime.now()
                error_count = 0
            if datetime.now() - last_error > timedelta(seconds = 900):
                error_count = 0
            wait = min(0.25 * 2**error_count, 30)
            last_error = datetime.now()
            error_count += 1
            print('Wait {} seconds before retrying...'.format(wait))
            time.sleep(wait)

            
    def _save_locally(self):
        if self.outlet_type == 'local' and not hasattr(self, 'file_timer'):
            self.file_timer = datetime.now() + self.minutes_per_file
        print('Start saving tweets into local TXT files...')
        while True:
            tweet = self.pipe_out.recv()
            if tweet == "FINISHED":
                return(False)
            self.tweets.append(tweet)
            self.tweet_count += 1
            # determine if the file is ready
            file_is_ready = False
            if 'count' in self.outlet_type:
                file_is_ready = self.tweet_count >= self.tweets_per_file
            else:
                file_is_ready = datetime.now() >= self.file_timer
            # file is not ready, continue adding tweets
            if not file_is_ready:
                continue
            # save file
            self.file_timer = datetime.now() + self.minutes_per_file
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
            # confirmation message
            if 'count' in self.outlet_type:
                print(file_name + ' is saved.')
            else:
                print('{} ----- {} tweets'.format(str(file_time),
                      str(len(self.tweets))))
            # check stall warnings
            if ('warning' in self.tweets[0] and
                'percent_full' in tweet['warning']):
                if tweet['warning']['percent_full'] > 0: # change threshold when debugging is done.
                    print('Warning: the queue is ' + 
                          str(tweet['warning']['percent_full']) + '% full.')
            # clean self.tweets
            self.tweets = []
            self.tweet_count = 0
        return(True) # stopped with no reason, re-trying


    def _tweet_outlet(self):
        time.sleep(0.25)
        go = True
        while go:
            if 'local' in self.outlet_type:
                go = self._save_locally() # find errors that may occur
            """
            retry = False
            try:
                if 'local' in self.outlet_type:
                    go = self._save_locally()
            except: # find errors that may occur
                retry = True
                pass
            # retry strategy   # find better retry strategy
            if not retry:
                continue
            print('Tweet outlet failed, resetting...')
            time.sleep(0.25)"""


    def StartMonitor(self, input_dict,
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
        
        if not input_dict or not api_type or not outlet_type:
            raise ValueError('INPUT_DICT, API_TYPE and ' +
                             'OUTLET_TYPE are needed.')
        
        # get ready
        self.input_dict = input_dict
        self.api_type = api_type.lower()
        self.outlet_type = outlet_type.lower()
        self._get_ready()
        
        # start monitor
        self.tweets_in = multiprocessing.Process(target = self._collect_tweets,
                                            args=())
        self.tweets_out = multiprocessing.Process(target = self._tweet_outlet,
                                            args=())
        self.tweets_in.start()
        self.tweets_out.start()
        
    	# finish up
        self.tweets_in.join()
        self.tweets_out.join()
        self.pipe_in.close()
        self.pipe_out.close()
        
        

            


                


