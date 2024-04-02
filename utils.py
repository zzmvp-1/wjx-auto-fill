import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import numpy

# 选取答案
def select_answer(answerList):
    length = len(answerList)
    index = random.randint(0, length - 1)
    return answerList[index]

# 简答题题 type=2
def fill_blank(driver, id, answerList, idx):
    xpath = '//*[@id="div{}"]/div[2]/textarea'.format(id)
    # text = select_answer(answerList)
    num = random.randint(0, len(answerList.get(idx))-1)
    text = answerList.get(idx)[num]
    driver.find_element(By.XPATH, xpath).send_keys(text)
    idx += 1
    return idx

# 归一化比例
def preprocess_prob(prob, length):
    if len(prob)==0:
        prob = numpy.ones(length)
    return [i/sum(prob) for i in prob]

# 单选 type=3
def single_choice(driver, id, prob, idx):
    xpath = '//*[@id="div{}"]/div[2]/div'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    # 如果没有传入比例，默认为等比例
    p = preprocess_prob(prob.get(idx), len(answers))
    choice = numpy.random.choice(a=numpy.arange(1, len(answers) + 1), p=p)
    xpath = '//*[@id="div{}"]/div[2]/div[{}]'.format(id, choice)
    # driver.find_element(By.XPATH, xpath).click()
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, xpath)).click().perform()
    idx += 1
    return idx

# 多选 type=4
def multi_choice(driver, id, prob, idx):
    xpath = '//*[@id="div{}"]/div[2]/div'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(idx), len(answers))
    # 多选的数量
    # 概率为0的选项个数
    count = sum(1 for i in p if i == 0)
    n = random.randint(1, len(answers)-count)
    q_selects = numpy.random.choice(a=numpy.arange(1, len(answers)+1), size=n, replace=False, p=p)
    for j in q_selects:
        driver.find_element(By.XPATH, '//*[@id="div{}"]/div[2]/div[{}]'.format(id, j)).click()
    idx += 1
    return idx

# 单量表题 type=5
def single_scale(driver, id, prob, idx):
    xpath = '//*[@id="div{}"]/div[2]/div/ul/li'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(idx), len(answers))
    choice = numpy.random.choice(a=numpy.arange(1, len(answers) + 1), p=p)
    xpath = '//*[@id="div{}"]/div[2]/div/ul/li[{}]'.format(id, choice)
    driver.find_element(By.XPATH, xpath).click()
    idx += 1
    return idx

# 矩阵量表 type=6
# 单选
def single_matrix_scale(driver, id, prob, idx, num):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = (len(driver.find_elements(By.XPATH, xpath)) - 1) / 2
    for i in range(1, int(q_len) + 1):
        xpath = '//*[@id="drv{}_{}"]/td'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        # 判断是浏览器还是QQ、微信
        if num == 0:
            p = preprocess_prob(prob.get(idx), len(answers) - 1)
            choice = numpy.random.choice(a=numpy.arange(1, len(answers)), p=p)
        else:
            p = preprocess_prob(prob.get(idx), len(answers))
            choice = numpy.random.choice(a=numpy.arange(0, len(answers)), p=p)
        xpath = '//*[@id="drv{}_{}"]/td[{}]'.format(id, i, choice + 1)
        time.sleep(0.5)
        driver.find_element(By.XPATH, xpath).click()
        idx += 1
    return idx

# 多选
def multi_matrix_scale(driver, id, prob, idx, num):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = (len(driver.find_elements(By.XPATH, xpath))-1)/2
    for i in range(1, int(q_len)+1):
        xpath = '//*[@id="drv{}_{}"]/td'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        # 判断是浏览器还是QQ、微信
        if num == 0:
            p = preprocess_prob(prob.get(idx), len(answers) - 1)
            # 多选的数量
            # 概率为0的选项个数
            count = sum(1 for i in p if i == 0)
            n = random.randint(1, len(answers) - 1 - count)
            q_selects = numpy.random.choice(a=numpy.arange(1, len(answers)), size=n, replace=False, p=p)
        else:
            p = preprocess_prob(prob.get(idx), len(answers))
            # 多选的数量
            # 概率为0的选项个数
            count = sum(1 for i in p if i == 0)
            n = random.randint(1, len(answers) - count)
            q_selects = numpy.random.choice(a=numpy.arange(0, len(answers)), size=n, replace=False, p=p)

        for q_select in q_selects:
            xpath = '//*[@id="drv{}_{}"]/td[{}]'.format(id, i, q_select+1)
            driver.find_element(By.XPATH, xpath).click()
        idx += 1
    return idx

# 下拉框 type=7
def select(driver, id, prob, idx):
    xpath = '//*[@id="div{}"]/div[2]'.format(id)
    driver.find_element(By.XPATH, xpath).click()
    xpath = "//*[@id='select2-q{}-results']/li".format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    # 有一个“请选择”,所以len-1
    p = preprocess_prob(prob.get(idx), len(answers) - 1)
    choice = numpy.random.choice(a=numpy.arange(1, len(answers)), p=p)
    xpath = "//*[@id='select2-q{}-results']/li[{}]".format(id, choice+1)
    driver.find_element(By.XPATH, xpath).click()
    idx += 1
    return idx

# 滑动条 type=8
def single_slide(driver, id, prob, idx):
    xpath = '//*[@id="jsrs_q{}"]/div[3]/div'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    p = preprocess_prob(prob.get(idx), len(answers)-1)
    choice = numpy.random.choice(a=numpy.arange(0, len(answers)-1), p=p)
    score = choice * 100/len(answers) + random.uniform(0, 100/len(answers))
    text = score * 614/100 + 10
    xpath = '//*[@id="jsrs_q{}"]/div[1]'.format(id)
    element = driver.find_element(By.XPATH, xpath)
    ActionChains(driver).move_to_element_with_offset(element, text, 0).click().perform()
    idx += 1
    return idx

# 多滑条 type=9
def multi_slide(driver, id, prob, idx):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = len(driver.find_elements(By.XPATH, xpath))/2
    for i in range(0, int(q_len)):
        xpath = '//*[@id="jsrs_q{}_{}"]/div[3]/div'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        p = preprocess_prob(prob.get(idx), len(answers) - 1)
        choice = numpy.random.choice(a=numpy.arange(0, len(answers) - 1), p=p)
        score = choice * 100 / len(answers) + random.uniform(0, 100 / len(answers))
        text = score * 614 / 100 + 10
        xpath = '//*[@id="jsrs_q{}_{}"]/div[1]'.format(id, i)
        element = driver.find_element(By.XPATH, xpath)
        ActionChains(driver).move_to_element_with_offset(element, text, 0).click().perform()
        idx += 1
    return idx

def add_one(lists, num, index):
    for i in range(index, len(lists)):
        if lists[i] < num:
            lists[i] += 1
    return lists

# 排序题 type=11
def sort(driver, id, prob, idx):
    xpath = '//*[@id="div{}"]/ul/li'.format(id)
    answers = driver.find_elements(By.XPATH, xpath)
    order = prob.get(idx)[:]
    for i in range(len(order)):
        index = order[i]
        xpath = '//*[@id="div{}"]/ul/li[{}]'.format(id, index)
        driver.find_element(By.XPATH, xpath).click()
        time.sleep(0.5)
        order = add_one(order, index, i)
    idx += 1
    return idx

# 分配题 type=12  暂时还没有完成
def distribute(driver, id, prob, idx):
    xpath = '//*[@id="divRefTab{}"]/tbody/tr'.format(id)
    q_len = len(driver.find_elements(By.XPATH, xpath))/2
    for i in range(0, int(q_len)):
        xpath = '//*[@id="jsrs_q{}_{}"]/div[3]/div'.format(id, i)
        answers = driver.find_elements(By.XPATH, xpath)
        p = preprocess_prob(prob.get(idx), len(answers) - 1)
        choice = numpy.random.choice(a=numpy.arange(0, len(answers) - 1), p=p)
        score = choice * 100 / len(answers) + random.uniform(0, 100 / len(answers))
        text = score * 614 / 100 + 10
        xpath = '//*[@id="jsrs_q{}_{}"]/div[1]'.format(id, i)
        element = driver.find_element(By.XPATH, xpath)
        ActionChains(driver).move_to_element_with_offset(element, text, 0).click().perform()
        idx +=1
    return idx
