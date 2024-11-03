import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import requests
import utils
import config
from threading import Thread

# 问卷链接
url = config.url

# 每题选项的比例
prob = config.prob

# 填空题答案
answerList = config.answerList

# 填写份数
epochs = config.epochs

# IP代理池
api = config.api

# UA库
UA = config.UA

option = webdriver.EdgeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('useAutomationExtension', False)

if __name__ == '__main__':
    curCount = 0
    errCount = 0

    for epoch in range(epochs):

        ip = requests.get(api).text
        # 修改IP
        option.add_argument('--proxy-server={}'.format(ip))

        option.add_experimental_option('detach', True)

        driver = webdriver.Edge(options=option)
        # 修改User-Agent
        # num = random.randint(0, 2)
        num = 0
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": UA[num]})
        # 将webdriver属性置为undefined
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                               {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})

        driver.get(url)
        time.sleep(0.3)
        # 你已经回答过部分题目，是否继续作答
        try:
            time.sleep(0.3)
            comfirm = driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a[1]')
            comfirm.click()
            time.sleep(0.2)
        except Exception as e:
            pass

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
                time.sleep(0.3)
            elif flag == '3':
                index = utils.single_choice(driver, i, prob, index)
                time.sleep(0.3)
            elif flag == '4':
                index = utils.multi_choice(driver, i, prob, index)
                time.sleep(0.3)
            elif flag == '5':
                index = utils.single_scale(driver, i, prob, index)
                time.sleep(0.3)
            elif flag == '6':
                xpath = '//*[@id="div{}"]/div[1]/div[2]/span'.format(i)
                if driver.find_element(By.XPATH, xpath).text.find("【") != -1:
                    index = utils.multi_matrix_scale(driver, i, prob, index, num)
                    time.sleep(0.3)
                else:
                    index = utils.single_matrix_scale(driver, i, prob, index, num)
                    time.sleep(0.3)
            elif flag == '7':
                index = utils.select(driver, i, prob, index)
                time.sleep(0.3)
            elif flag == '8':
                index = utils.single_slide(driver, i, prob, index)
                time.sleep(0.3)
            elif flag == '11':
                index = utils.sort(driver, i, prob, index)
                time.sleep(0.3)
            elif flag == '12':
                index = utils.multi_slide(driver, i, prob, index)
                time.sleep(0.3)
            else:
                print("没有该题型")
                break

        time.sleep(0.3)
        submit_button = driver.find_element(By.XPATH, '//*[@id="ctlNext"]')
        submit_button.click()
        time.sleep(0.3)

        # 请点击智能验证码进行验证！
        try:
            comfirm = driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a')
            comfirm.click()
            time.sleep(0.5)
        except Exception as e:
            pass

        # 点击按钮开始智能验证
        try:
            button = driver.find_element(By.XPATH, '//*[@id="SM_BTN_WRAPPER_1"]')
            button.click()
            time.sleep(3)
        except Exception as e:
            pass

        # 滑块验证
        try:
            slider1 = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
            if str(slider1.text).startswith("请按住滑块，拖动到最右边"):
                width = slider1.size.get('width')
                slider = driver.find_element(By.XPATH, '//*[@id="nc_1_n1z"]')
                ActionChains(driver).drag_and_drop_by_offset(slider, width, 0).perform()
                time.sleep(3)
        except Exception as e:
            pass

        time.sleep(3)
        url1 = driver.current_url  # 表示问卷填写完成后跳转的链接，一旦跳转说明填写成功
        if url != url1:
            curCount += 1
            print("已完成{}份".format(curCount))
        else:
            errCount += 1
        driver.quit()
        time.sleep(1)

    print("全部完成{}份填写".format(epochs), "成功了{}份".format(curCount), "失败了{}份".format(errCount))
