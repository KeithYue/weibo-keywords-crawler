# coding=utf-8
from urllib.request import urlopen

# This module is for code verification

def test():
    w = WeiboCodeVerifiction('http://s.weibo.com/ajax/pincode/pin?type=sass&ts=1405065840')


class WeiboCodeVerifiction():
    '''
    weibo code verification
    '''

    def __init__(self, image_url):
        '''
        image url: the url of the image in the Internet
        '''
        self.image_url = image_url

        # read the image content
        image_content = urlopen(self.image_url).read()
        print(image_content[:10])
        print(type(image_content))

if __name__ == '__main__':
    test()
