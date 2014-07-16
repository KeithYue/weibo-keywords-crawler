# coding=utf-8
import base64
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from io import StringIO, BytesIO
from threading import Lock

# This module is for code verification

get_image_data = '''
function getBase64Image(img) {
    // Create an empty canvas element
    var canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;

    // Copy the image contents to the canvas
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);

    // Get the data-URL formatted image
    // Firefox supports PNG and JPEG. You could check img.src to
    // guess the original format, but be aware the using "image/jpg"
    // will re-encode the image.
    var dataURL = canvas.toDataURL("image/png");

    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
    // return dataURL;
}

code_img = document.querySelector('img[node-type="yzm_img"]');
// code_img = document.querySelector('img');
data_URL = getBase64Image(code_img);

return data_URL;
'''



def test():
    driver = webdriver.PhantomJS()
    driver.get('http://s.weibo.com/ajax/pincode/pin?type=sass&ts=1405404856')
    verify_user(driver)
    return

def get_img(base64_str):
    '''
    convert the base64 string to png image --> PIL.Image
    '''
    base64_bytes = base64.b64decode(base64_str)
    image_bytes_io = BytesIO(base64_bytes)
    image = Image.open(image_bytes_io)
    return image

def get_code(img):
    '''
    given an image, return its code
    '''
    img.show()
    verification_code = input('Please input the verificaiont code: ')
    return verification_code



def verify_user(driver):
    '''
    when the driver shows the verification code, load the code in the browser and input the code-->the code

    driver: the current driver which comes into the verification code
    '''
    while True:
        feed = driver.find_elements_by_class_name('feed_list')
        if len(feed) == 0:
            # there is no feed in this page, meaning you need to input the code
            code_png = get_img(driver.execute_script(get_image_data))

            INPUT_LOCK.acquire()
            try:
                verification_code = get_code(code_png)# this action needs to be primitive
            finally:
                INPUT_LOCK.release()

            # need to close the image

            code_input = driver.find_element_by_xpath('//input[@node-type="yzm_input"]')
            code_input.click()
            code_input.send_keys(verification_code.strip())

            submit_button = driver.find_element_by_xpath('//a[@node-type="yzm_submit"]')
            submit_button.click()
            time.sleep(5)

            driver.get_screenshot_as_file('./screenshot/after_verfiy.png')
        else:
            break

    print('verification completed!')
    return

INPUT_LOCK = Lock() # Every time there would be only one input propmt for users

if __name__ == '__main__':
    test()
