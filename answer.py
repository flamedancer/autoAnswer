"""

1. pip install BeautifulSoup selenium
2. 需要 浏览器支持 当前用的是 google浏览器  需要下载对应浏览器版本号驱动到 driver_dir  下载地址 https://registry.npmmirror.com/binary.html?path=chromedriver/
"""


import os
from bs4 import BeautifulSoup
import datetime
result_dir = '/Users/flame/Downloads/合规答题/'
driver_dir = '/Users/flame/Downloads'


# title =>    options => { a => }   answers => []  answer_options => []
questions = {}
# 控制答题时间 不能太快
answer_time = 0 * 60.0 # 秒


def get_sample_files():
    return ["{}{}".format(result_dir, filename) for filename in os.listdir(result_dir) if filename.endswith('.html')]


def collection(file_path):
    soup = BeautifulSoup(open(file_path))
    all_warp = list(soup.find_all(**{'class': "item-wrap"})) + list(soup.find_all(**{'class': "checking-item-container"}))
    new_add_num = 0
    for item_wrap in all_warp:
        question_title = item_wrap.find(**{'class': "question-title"}).get_text().split('、', 1)[1].strip()
        # print(question_title)
        options = {}
        if '判断题' not in item_wrap.find(**{'class': 'quetion-type'}).get_text():
            for option_item_after in item_wrap.find_all(**{'class': "option-item-after"}):
                option = option_item_after.get_text().strip().split('.', 1)
                options[option[0].strip()] = option[1].strip()
                # print(option)
        else:
            for option_item_after in item_wrap.find_all(**{'class': "checking-option__container"}):
                option = option_item_after.get_text().strip()
                options[option] = option
                # print(option)
        answer_options = [option.strip() for option in item_wrap.find(**{'class': "right-answer"}).get_text().split('、')]
        answers = [options[answer_option] for answer_option in answer_options]
        # if question_title == '进口押汇、进口代收押汇、出口托收押汇融资资金只能用于支付货款，不得挪作他用。':
        #     print(file_path)
        #     input()
            
        if question_title not in questions:
            questions[question_title] = {
                'title': question_title,
                'options': options,
                'answer_options': answer_options,
                'answers': answers,
            }
            # print('new_question:', question_title)
            print('当前题目数:', len(questions))
            new_add_num += 1
    print(file_path)
    print('解析获得题目数：', new_add_num)


def do_load_questions():
    for file in get_sample_files():
        collection(file)
    print('题库共有题目数：', len(questions))



from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selenium.webdriver import ActionChains, DesiredCapabilities
import time
import os
import sys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class AutoBrowser:
    def __init__(self):
        options = Options()
        options.add_experimental_option("prefs", {
            "download.default_directory": result_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        self.driver = webdriver.Chrome(chrome_options=options)

        self.devicePixelRatio = self.driver.execute_script("""return (window.devicePixelRatio)""")

    def click_elem(self, elem):
        # elem.click()
        actions = ActionChains(self.driver)
        actions.move_to_element(elem)
        actions.click(elem)
        actions.perform()

    def show_ele(self, ele):
        self.driver.execute_script("arguments[0].scrollIntoView();", ele)



    def find_and_click(self, class_name):
        WebDriverWait(self.driver, 10000).until(
            EC.visibility_of_element_located((By.CLASS_NAME, class_name))
        )
        print("find ", class_name)
        item = self.driver.find_element(By.CLASS_NAME, class_name)
        item.click()


    def login(self):
        """
        登录百度推广后台
        :return:
        """
        self.driver.get("https://appmoxybx5v3148.h5.xiaoeknow.com/evaluation_wechat/examination/introduce/ex_63624d5eb9206_loJmUWKd")
        self.find_and_click('start-exam-btn')
        self.find_and_click("right-button")


    def scroll(self):
        self.driver.execute_script("window.scrollBy(0,500)")

    def has_choiced(self, ele):
        class_names = ['single-exam-radio-active', 'check-i-active']
        choiced = []
        for class_name in class_names:
            choiced += ele.find_elements(By.CLASS_NAME, class_name)
        return len(choiced)

    def do_answer(self):
        WebDriverWait(self.driver, 10000).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'question-container'))
        )
        index = 0
        has_answer = 0
        wrap_names = ['item-wrap', 'checking-item-container']
        miss_questions = set()

        for wrap_name in wrap_names:
            for item_wrap in self.driver.find_elements(By.CLASS_NAME, wrap_name):
                time.sleep(answer_time / 50.0)
                self.show_ele(item_wrap)
                # time.sleep(1)
                print('find item_wrap', wrap_name)
                # WebDriverWait(self.driver, 10000).until(
                #     EC.visibility_of_element_located((By.CLASS_NAME, "question-title")))
                # print('find question-title')
                try:
                    index, question_title = item_wrap.find_element(By.CLASS_NAME, "question-title").text.split('、', 1)
                    index = int(index.strip())
                except:
                    try:
                        question_title = item_wrap.find_element(By.ID, "_flag4unlimit").text
                        index += 1
                    except:
                        print('do continue')
                        continue
                question_title = question_title.strip()
                print(index, question_title)
                if question_title in questions:
                    print("命中：： ", questions[question_title]['answers'])
                    has_answer += 1
                else:
                    miss_questions.add(question_title)
                if '判断题' not in item_wrap.find_element(By.CLASS_NAME, "quetion-type").text:
                    option_class = "option-item"
                    for option_item_after in item_wrap.find_elements(By.CLASS_NAME, option_class):
                        option = option_item_after.text.strip().split('.', 1)
                        print(option)
                        if question_title in questions:
                            if option[1].strip() in questions[question_title]['answers'] and not self.has_choiced(option_item_after):
                                self.click_elem(option_item_after)
                        else:
                            # if option[0].strip() in ['A', 'B', 'C', 'D']:
                            if not self.has_choiced(option_item_after):
                                self.click_elem(option_item_after)

                else:
                    option_class = "checking-option__container"
                    for option_item_after in item_wrap.find_elements(By.CLASS_NAME, option_class):
                        option = option_item_after.text.strip()
                        print(option)
                        if question_title in questions:
                            if option in questions[question_title]['answers']:
                                self.click_elem(option_item_after)
                        else:
                            if option == '正确':
                                self.click_elem(option_item_after)


        # time.sleep(1000000)
        print("$$$$$$4", index, has_answer, has_answer * 1.0 / index)
        print("$$$$获得新题目数：", index - has_answer, len(miss_questions))
        for miss_question in miss_questions:
            print("miss...:", miss_question)


    def submit(self):
        self.scroll()
        # time.sleep(2)
        self.click_elem(self.driver.find_element(By.CLASS_NAME, "submit-button"))
        WebDriverWait(self.driver, 10000).until(      
            EC.visibility_of_element_located((By.CLASS_NAME, "test-button")))


    def close_win_bnt(self):
        try:
            bnt = self.driver.find_element(By.CSS_SELECTOR, '[src="https://commonresource-1252524126.cdn.xiaoeknow.com/image/l88zsge30jle.png"]')
            bnt.click()
        except:
            pass

    def save_rst(self):
        self.close_win_bnt()
        res = self.driver.execute_script('return document.documentElement.outerHTML')
        new_file = '{}{}.html'.format(result_dir, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        with open(new_file, 'w', newline='') as f:   # 根据5楼的评论，添加newline=''
            f.write(res)
        return new_file

    def next_answer(self):
        # input()
        self.click_elem(self.driver.find_element(By.CLASS_NAME, "test-button"))



    def release(self):
        self.driver.close()


if __name__ == '__main__':
    # do_load_questions()
    # collection(result_dir + '20221115213507.html')
    os.environ['PATH'] = os.path.sep + driver_dir
    do_load_questions()

    auto_browser = AutoBrowser()
    try:
        auto_browser.login()
        while 1:
            auto_browser.do_answer()
            if answer_time < 120:
                input()
            auto_browser.submit()
            # input()
            new_file = auto_browser.save_rst()
            collection(new_file)
            auto_browser.next_answer()
    finally:
        # pass
        auto_browser.release()

