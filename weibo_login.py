# coding=utf-8
# provide the weibo login class
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import time
import logging
from weibo import Client
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from code_verification import verify_user

APP_KEY = '3544297892'
APP_SECRET = '4e49761d581b7f80e0954a984e32a242'
CALLBACK_URI = 'http://lifecity.sinaapp.com'
APP_DATA = (APP_KEY, APP_SECRET, CALLBACK_URI)

class WeiboLogin():
    def __init__(self, username, passwd, driver):
        self.username = username
        self.passwd = passwd
        self.driver = driver

    def login(self):
        '''
        try a mount of time until successfully log in
        '''
        while True:
            if self.login_once():
                return True
            else:
                logging.info('trying another time to login... pls wait')
                continue

    def login_once(self):
        self.driver.get('http://www.weibo.com/login.php')
        try:
            WebDriverWait(self.driver, 10).until(
                    lambda x: x.find_element_by_css_selector('div.info_list')
                    )
            # logging.info self.driver.page_source
            self.driver.maximize_window()
            user_input = self.driver.find_element_by_xpath('//div[@node-type="normal_form"]//input[@name="username"]')

            # logging.info user_input.get_attribute('action-data')
            user_input.click()
            user_input.clear()
            user_input.send_keys(self.username)

            passwd_input = self.driver.find_element_by_xpath('//div[@node-type="normal_form"]//input[@name="password"]')
            passwd_input.click()
            passwd_input.clear()
            # logging.info passwd_input
            passwd_input.send_keys(self.passwd)

            submit_button = self.driver.find_element_by_xpath('//div[@node-type="normal_form"]//a[@class="W_btn_g"]')

            self.driver.get_screenshot_as_file('./screenshot/screenshot.png')
        except TimeoutException:
            logging.info('load login page failed')
            return False

        logging.info('user name: {}'.format(user_input.get_attribute('value')))
        logging.info('passwd: {}'.format(passwd_input.get_attribute('value')))
        time.sleep(1) # wait the page to load the verification code
        verify_user(self.driver, 'login')

        submit_button.click()
        try:
            WebDriverWait(self.driver, 10).until(
                    lambda x: x.find_element_by_class_name('WB_left_nav')
                    )
            logging.info('login success')
            return True

        except TimeoutException:
            logging.info('login failed: {}'.format(self.driver.current_url))
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
            # logging.info driver.pagself.e_source
            submit_button = self.driver.find_element_by_css_selector('p.oauth_formbtn').find_element_by_tag_name('a')

            submit_button.click()
        except TimeoutException:
            # there is no submit button, so the user may have authorized the app
            logging.info('the user has authorized the app')

        # parse the code
        # logging.info driver.current_url
        query_str = urllib.parse.urlparse(self.driver.current_url).query
        code = urllib.parse.parse_qs(query_str)['code']

        c.set_code(code)
        logging.info('authorize the app success! code, {}'.format(code))
        return c

def test():
    pass

if __name__ == '__main__':
    test()
