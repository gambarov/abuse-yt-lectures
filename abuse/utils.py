from selenium import webdriver
import time
import datetime


def get_video_duration(driver: webdriver.Chrome):
    duration = driver.find_elements_by_xpath(
        "//span[@class='ytp-time-duration']")[0].text
    x = time.strptime(duration, '%M:%S')
    result = datetime.timedelta(
        minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
    return int(result)
