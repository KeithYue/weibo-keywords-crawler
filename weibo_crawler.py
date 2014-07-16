# coding=utf-8
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import re
import time
import datetime
import sys
import random
import json
import codecs
import requests
import os
from PIL import Image
from io import BytesIO
from bson import json_util
from bs4 import BeautifulSoup
from weibo import Client
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from code_verification import verify_user
from weibo_comments_crawler import WeiboCommentsCrawler

search_domain = 's.weibo.com'
weibo_type = ('hot', 'time')

# setup browser driver
# driver = webdriver.PhantomJS()
# driver.set_window_size(1440, 900)

# config the app data for authorization
APP_KEY = '3544297892'
APP_SECRET = '4e49761d581b7f80e0954a984e32a242'
CALLBACK_URI = 'http://lifecity.sinaapp.com'
APP_DATA = (APP_KEY, APP_SECRET, CALLBACK_URI)

USER_NAME = '14714320465'
PASSWD = '5805880'


def save_source(html_content):
    '''
    this function is used for debugging
    '''
    file_path = './screenshot/error.html'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return

class WeiboLogin():
    def __init__(self, username, passwd, driver):
        self.username = username
        self.passwd = passwd
        self.driver = driver

    def login(self):
        self.driver.get('http://www.weibo.com/login.php')
        try:
            WebDriverWait(self.driver, 10).until(
                    lambda x: x.find_element_by_css_selector('div.info_list')
                    )
            # print self.driver.page_source
            self.driver.maximize_window()
            user_input = self.driver.find_element_by_xpath('//div[@node-type="normal_form"]//input[@name="username"]')

            # print user_input.get_attribute('action-data')
            user_input.click()
            user_input.clear()
            user_input.send_keys(self.username)

            passwd_input = self.driver.find_element_by_xpath('//div[@node-type="normal_form"]//input[@name="password"]')
            passwd_input.click()
            passwd_input.clear()
            # print passwd_input
            passwd_input.send_keys(self.passwd)

            submit_button = self.driver.find_element_by_xpath('//div[@node-type="normal_form"]//a[@class="W_btn_g"]')

            self.driver.get_screenshot_as_file('./screenshot/screenshot.png')
        except TimeoutException:
            print('load login page failed')
            return False

        print('user name', user_input.get_attribute('value'))
        print('passwd', passwd_input.get_attribute('value'))
        submit_button.click()
        try:
            WebDriverWait(self.driver, 10).until(
                    lambda x: x.find_element_by_class_name('WB_left_nav')
                    )
            print('login success')
            return True

        except TimeoutException:
            print('login failed', self.driver.current_url)
            self.driver.get_screenshot_as_file('./screenshot/login_failed.png')
            return False

    def authorize_app(self, app_data = APP_DATA):
        '''
        authorize the app
        return the client for invoding weibo api
        must be invoked after the login function
        '''
        c = Client(*app_data)
        self.driver.get(c.authorize_url)
        try:
            WebDriverWait(self.driver, 10).until(
                    lambda x: x.find_element_by_css_selector('div.oauth_login_submit')
                    )
            # print driver.pagself.e_source
            submit_button = self.driver.find_element_by_css_selector('p.oauth_formbtn').find_element_by_tag_name('a')

            submit_button.click()
        except TimeoutException:
            # there is no submit button, so the user may have authorized the app
            print('the user has authorized the app')

        # parse the code
        # print driver.current_url
        query_str = urllib.parse.urlparse(self.driver.current_url).query
        code = urllib.parse.parse_qs(query_str)['code']

        c.set_code(code)
        print('authorize the app success! code,', code)
        return c

class WeiboCrawler():
    '''
    crawl weibo using keywords
    '''
    def __init__(self, search_key, user_name=USER_NAME, passwd=PASSWD):
        # login to sinaweibo
        self.driver = webdriver.PhantomJS()
        self.wl = WeiboLogin(user_name, passwd, self.driver) # the interface for authorization

        if self.wl.login():
            print('login successfully')
        else:
            print('login faied')
            sys.exit(1)
        self.sk = search_key.strip()
        return

    def __del__(self):
        self.driver.quit()
        return

    def crawl(self, page_count=1, comments=False):
        '''
        crawl the weibo using the keywords

        page_count: how many pages would be crawled
        '''
        self.results = []
        # get the mids from each result page
        pages = list(range(1, page_count+1))
        random.shuffle(pages)

        for t in ('hot', 'time'):
            for i in pages:
                url_to_crawl = self.get_search_url(i)
                print('crawling page', i, url_to_crawl)
                self.driver.get(url_to_crawl)
                # wait the page loading the content
                try:
                    element = WebDriverWait(self.driver, 5).until(
                            lambda x: x.find_elements_by_class_name('feed_list')
                            )
                except TimeoutException:
                    print('there is no weibo content in', url_to_crawl)
                    print('you are considered as a robot')
                    print(self.driver.current_url)
                    self.driver.get_screenshot_as_file('./screenshot/error.png')

                    # let user input the verification code
                    verify_user(self.driver)
                    # break


                weibo_list = self.get_weibo_list(self.driver.page_source) # mid is used to crawl the original weibo content, using batch mode
                self.results.extend(weibo_list)

                # sleep some time to prevent hitting too much
                # time.sleep(1)
            else: continue
            break

        # for r in results:
        #     print_dict(r)
        print('total result', len(self.results))


        if comments:
            print('crawling the comments')
            self.crawl_comments()
        return

    def get_search_url(self, page=1, w_type='hot'):
        '''
        compose a search url based on page_num and weibo type
        '''
        # print('generating the url')
        url=''
        url += 'http://'
        url += search_domain
        url += '/wb'
        url += urllib.parse.quote('/'+self.sk)
        url += '&'
        url += urllib.parse.urlencode([
            ('page', page),
            ('xsort', w_type)
            ])

        return url


    def get_weibo_list(self, content):
        '''
        parse the weibo content in the current result page
        content: the source page of the keywords result

        return: a list of weibo object
        '''
        weibo_list = []
        soup = BeautifulSoup(content, 'html5lib')
        for t in soup.find_all('dl', class_='feed_list'):
            if t.has_attr('mid'):
                weibo = self.parse_weibo(t)
                if weibo:
                    weibo_list.append(weibo)
        print(len(weibo_list))
        return weibo_list

    def parse_weibo(self, t):
        '''
        parse weibo object from html
        t: the tag object that has weibo content

        Return weibo object
        '''
        weibo = {}

        try:
            weibo['keywords'] = self.sk.split(' ') #keywords is a list of words
            weibo['mid'] = t['mid']

            # the user name
            weibo['screen_name'] = t.find(name='dt', class_='face').find('a').get('title')
            weibo['user_profile'] = t.find(name='dt', class_='face').find('a').get('href')

            # the content of weibo
            weibo['text'] = t.find(name='dd', class_='content').find('em').get_text().strip()
            # the source url of the weibo
            weibo['source_url'] = t.find(name='a', class_='date').get('href').strip()
            print(weibo['source_url'])

            # print(weibo['text'])

            # meta data
            epoch_length = len(str(int(time.time())))
            time_str = t.find('dd', class_='content').find('p', class_='info W_linkb W_textb').find(name='a', class_='date').get('date')[0:epoch_length]
            time_now = time.localtime(int(time_str))
            weibo['created_at'] = datetime.datetime(*time_now[0:6])
            weibo['source'] = t.find('dd', class_='content').find('p', class_='info W_linkb W_textb').find('a', rel='nofollow').string.strip()

            pop_str = t.find('dd', class_='content').find('p', class_='info W_linkb W_textb').find('span').get_text().strip().replace('\n', '')

            pop_type = {
                    # key: source representation, value: attr
                    '赞': 'like_count',
                    '转发': 'repost_count',
                    '评论': 'comment_count'
                    }
            for key in list(pop_type.keys()):
                pattern = re.compile(r'.*(%s\((\d+)\)).*' % key)
                match = pattern.match(pop_str)
                if match:
                    # print match.group(1)
                    # print match.group(2)
                    weibo[pop_type[key]] = int(match.group(2))
                else:
                    # print key, 'not found.'
                    weibo[pop_type[key]] = 0

        except Exception as e:
            print(e)
            return None

        # print_dict(weibo)
        return weibo

    def save(self, dist_dir='result'):
        '''
        save the search results to file
        '''
        if dist_dir not in os.listdir(os.curdir):
            os.mkdir(dist_dir)
        for w in self.results:
            file_name = ''.join([
                    '_'.join([k for k in w['keywords']]),
                    w['mid']
                    ])
            file_name += '.txt'
            f = codecs.open(os.path.join(dist_dir, file_name), 'w', 'utf-8')
            json.dump(w, f, ensure_ascii = False, default=json_util.default, indent = 2)
            # print(w['text'])
            print('writed to file', file_name)
        return

    def crawl_comments(self):
        '''
        crawl the comments after getting all the results and update the results list --> self
        '''
        client = self.wl.authorize_app()
        if client:
            for w in self.results:
                # print(w['mid'])
                w['comments'] = []
                crawler = WeiboCommentsCrawler(client, weibo_mid = w['mid'])
                r = crawler.crawl()

                # filter out the unrelated fields
                for c in r:
                    c.pop('status')
                w['comments'].extend(r)
        else:
            print('认证失败，不能获取评论列表')
        return

def print_dict(d):
    '''
    print the fields of dictionary

    d: dict
    '''
    for key in d:
        print('{}:'.format(key), end=' ')
        if type(d[key]) == list:
            for i in d[key]:
                print(i, end=' ')
        else:
            print(d[key], end=' ')
        print()
    return


def test():
    wc = WeiboCrawler('火影忍者', USER_NAME, PASSWD)
    wc.crawl(50, comments = False)
    wc.save()
    # wl = WeiboLogin(USER_NAME, PASSWD, driver)
    # c = wl.authorize_app(APP_DATA)
    # print c.get('users/show', uid=1282440983)

if __name__ == '__main__':
    test()
