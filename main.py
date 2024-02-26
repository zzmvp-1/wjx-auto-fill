import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import requests
import utils
import config
import sys

# 问卷链接
url = config.url

# 每题选项的比例
prob = config.prob

# 填空题答案
answerList = config.answerList

# 填写份数
epochs = config.epochs

# IP API代提取链接
api = config.api

# UA库
UA = config.UA

option = webdriver.EdgeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('useAutomationExtension', False)

if __name__ == "__main__":

    for epoch in range(epochs):
        
        # 通过API链接爬取IP，这里根据自己的情况进行修改
        ip = requests.get(api).text
        # 修改IP
        option.add_argument('--proxy-server={}'.format(ip))

        driver = webdriver.Edge(options=option)
        # 修改User-Agent
        num = random.randint(0, 2)
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": UA[num]})
        # 将webdriver属性置为undefined
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                               {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})

        driver.get(url)
        
        # 题号
        index = 1
        # 获取题目数量
        questions = driver.find_elements(By.CLASS_NAME, "field.ui-field-contain")
        for i in range(1, len(questions) + 1):
            xpath = '//*[@id="div{}"]'.format(i)
            question = driver.find_element(By.XPATH, xpath)
            # 获取题目类型
            flag = question.get_attribute("type")
            if flag == '2':
                index = utils.fill_blank(driver, i, answerList, index)
                time.sleep(1)
            elif flag == '3':
                index = utils.single_choice(driver, i, prob, index)
                time.sleep(1)
            elif flag == '4':
                index = utils.multi_choice(driver, i, prob, index)
                time.sleep(1)
            elif flag == '5':
                index = utils.single_scale(driver, i, prob, index)
                time.sleep(1)
            elif flag == '6':
                xpath = '//*[@id="div{}"]/div[1]/div[2]/span'.format(i)
                if driver.find_element(By.XPATH, xpath).text.find("【") != -1:
                    index = utils.multi_matrix_scale(driver, i, prob, index, num)
                    time.sleep(1)
                else:
                    index = utils.single_matrix_scale(driver, i, prob, index, num)
                    time.sleep(1)
            elif flag == '7':
                index = utils.select(driver, i, prob, index)
                time.sleep(1)
            elif flag == '8':
                index = utils.single_slide(driver, i, prob, index)
                time.sleep(2)
            elif flag == '11':
                index = utils.sort(driver, i, prob, index)
                time.sleep(1)
            elif flag == '12':
                index = utils.multi_slide(driver, i, prob, index)
                time.sleep(1)
            else:
                print("没有该题型")
                sys.exit(0)
                
        time.sleep(1)
        submit_button = driver.find_element(By.XPATH, '//*[@id="ctlNext"]')
        submit_button.click()
        time.sleep(1)

        # 请点击智能验证码进行验证！
        try:
            comfirm = driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a')
            comfirm.click()
            time.sleep(1)
        except Exception as e:
            print(e)

        # 点击按钮开始智能验证
        try:
            button = driver.find_element(By.XPATH, '//*[@id="SM_BTN_WRAPPER_1"]')
            button.click()
            time.sleep(0.5)
        except Exception as e:
            print(e)

        # 滑块验证
        try:
            slider = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
            time.sleep(0.3)
            if str(slider.text).startswith("请按住滑块，拖动到最右边"):
                width = slider.size.get('width')
                ActionChains(driver).drag_and_drop_by_offset(slider, width, 0).perform()
                time.sleep(1)
        except Exception as e:
            print(e)

        time.sleep(3)
        driver.quit()
        print("已完成{}份".format(epoch))
        
    print("全部完成{}份填写".format(epochs))
