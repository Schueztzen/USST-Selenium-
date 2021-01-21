# -*- coding:utf-8 -*-
"""
    Editor:Schuetzen
    Date:2021.01.19
"""
import logging
import time
from time import sleep
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


# 创建用户对象
class User:
    student_id = "********"  # 学号
    student_psd = "********"  # 密码
    position = ("***", "***")  # 位置
    SCKEY = "***"  # api接口
    set_time = [(9, 20)]    # 设置打卡时间
    max_attempt = 5  # 最大失败次数


def login():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 浏览器静默模式
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--start-maximized')  # 浏览器最大化
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    # noinspection PyBroadException
    try:
        url = "http://myportal.usst.edu.cn"
        page1 = driver.get(url)
        user_name_input = driver.find_element_by_css_selector("#username")
        user_name_input.send_keys(User.student_id)
        user_psd_input = driver.find_element_by_css_selector("#password")
        user_psd_input.send_keys(User.student_psd)
    except:
        logger.info("open webpage failed, please check connection")
        # print("open webpage failed, please check connection")

    logger.info("successfully open webpage")
    # print("successfully open webpage")

    # 登录
    login_button = driver.find_element_by_css_selector('#casLoginForm > p:nth-child(5) > button')
    ActionChains(driver).move_to_element(login_button).click(login_button).perform()
    driver.implicitly_wait(2)

    fail_cnt = 0
    while True:
        location_button = driver.find_elements_by_css_selector(
            '#root > div > div.wrapper.wrapper-header.wrapper-default-theme > div > div > a > img')
        if len(location_button) > 0:
            logger.info("log in successfully")
            # print("log in successfully")
            return True, driver
        else:
            # 出现密码错误提示框
            if len(driver.find_elements_by_css_selector('#msg')) > 0:
                send_message("failed, please check your id or password")
                logger.info("failed, please check your id or password")
                exit(0)

            # 若只是反应慢，重试
            if fail_cnt >= User.max_attempt:
                send_message("time out, failed times have over max attempt times")
                logger.info("time out, failed times have over max attempt times ")
                return False, None
            time.sleep(10)
            driver.get("http://myportal.usst.edu.cn/sopplus/student/index.html")
            logger.info("time out, please try again")
            print("time out, please try again")
            fail_cnt += 1


def check_in():
    login_flag, driver = login()
    if not login_flag:
        return

    url = "http://10.1.11.131:8600/#/dform/genericForm/Yvo3gjIo"
    driver.get(url)

    time.sleep(1)
    driver.switch_to.window(driver.window_handles[0])

    # 点击提交
    driver.implicitly_wait(3)

    while True:
        # noinspection PyBroadException
        try:
            confirm_button = driver.find_element_by_css_selector(
                '#root > div > div.formUrl___3h-2H > div.formBack___2bxfC > div:nth-child(5) > button')
            ActionChains(driver).move_to_element(confirm_button).click(confirm_button).perform()
            # noinspection PyBroadException
            try:
                driver.switch_to.window(driver.window_handles[0])
                check_confirm = driver.find_element_by_css_selector(
                    '#root > div > div > p > p.formTopText___1z45f')
                result = 'Successfully Processed'
                break
            except NoSuchElementException as reason:
                result = f'failed: {reason}'
                logger.info(result)
                return False
        except:
            # noinspection PyBroadException
            try:
                confirm_button = driver.find_element_by_css_selector('#root > div > div.formUrl___3h-2H > div')
                reason = driver.find_element_by_css_selector('div > div > div > span:nth-child(2)').text
                result = f'failed: {reason}'
                break
            except:
                time.sleep(1)

    # ActionChains(driver).move_to_element(confirm_button).click(confirm_button).perform()
    driver.implicitly_wait(3)

    logger.info(result)

    local_date = datetime.date.today()
    send_message(f"{local_date} {result}")
    sleep(60)
    driver.quit()
    logger.info("Process finished")


# 发送微信推送
def send_message(msg):
    if User.SCKEY == "":
        return
    payload = {'text': msg}
    requests.get(f"https://sc.ftqq.com/{User.SCKEY}.send", params=payload)


# 每日打卡
def main():
    logger.info("checking now, please wait...")
    flag, browser = login()
    browser.quit()
    if not flag:
        exit(0)
    while True:
        while True:
            time_up = False
            now = datetime.datetime.now()
            for hour, minute in User.set_time:
                if now.hour == hour and now.minute == minute:
                    time_up = True
                if time_up:
                    break
                logger.info(f"it's not time, please wait! Local time is {now}")
                sleep(30)
            logger.info("time up, checking now")
            check_in()


if __name__ == "__main__":
    log_file = "log.log"
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    logger = logging.getLogger("main")
    fh = logging.FileHandler(log_file, mode='w')
    fh.setFormatter(formatter)
    ch = logging.StreamHandler()
    ch = logging.StreamHandler()
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    # check_in()
    main()

