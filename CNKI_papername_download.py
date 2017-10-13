#!/usr/bin/env Python
# coding=utf-8
import  os
import uniout
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def browser_init(isWait):
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': 'C:\\Users\\Halouccr\\Desktop\\CNKI'}
    options.add_experimental_option('prefs', prefs)

    browser = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)
    browser.maximize_window()  #最大化屏幕
    #browser.set_window_size(500,500)
    if isWait:
        browser.implicitly_wait(10)
    return browser

def getKeywordDownloadLink(browser,keyword):

    link=browser.find_element_by_link_text(keyword)
    url = link.get_attribute('href')
    url_part = url.split('&')[3:6]
    url_str = '&'.join(url_part)
    down_url = 'http://kns.cnki.net/KCMS/detail/detail.aspx?' + url_str

    return down_url

def do_download(driver,url,fail_downLoadUrl):

    driver.get(url)
    paper_title = driver.title[:-7]
    print u"准备下载:"+ paper_title,

    try:
        download_button = WebDriverWait(driver,3).until \
        (EC.presence_of_element_located((By.ID,"pdfDown")))

    except Exception as e:
        download_button = WebDriverWait(driver,5).until \
        (EC.presence_of_element_located((By.XPATH,u"//a[contains(text(),'整本下载')]")))

    download_button.send_keys(Keys.ENTER)
    alert_present_judge_do_some()(driver,url,fail_downLoadUrl)

    sleep(5)  #本意是等待下载完成，应该使用显示等待，没有找到合适的等待条件 针对下载页面全空


class alert_present_do_nothing(object):

    def __init__(self):
        pass

    def __call__(self, driver):
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass

class alert_present_judge_do_some():

    def __init__(self):
        pass

    def __call__(self, driver,url,fail_downLoadUrl):
        try:
            alert = driver.switch_to.alert
            #slepp(1)
            print alert.text
            if alert.text == "当前用户并发数已满!":
                print u"    当前用户并发数已满!下载失败"
            alert.accept()
            fail_downLoadUrl.append(url)
        except:
            print u"    没弹窗，下载成功"

class searchKey(alert_present_do_nothing):

    def __init__(self):
        pass

    def search(self,keyword):
        browser.get("http://kns.cnki.net/kns/brief/default_result.aspx")
        try:
            element = WebDriverWait(browser,10).until \
            (EC.presence_of_element_located((By.ID,"txt_1_value1")))
            element.send_keys(keyword)
            print u"搜索:%s" %keyword
        except:
            print u"浏览器出bug"
        browser.find_element_by_id('btnSearch').click()
        browser.switch_to.frame('iframeResult')


if __name__=="__main__":

    fail_downLoadUrl=[]         #记录下下载失败的网站

    browser = browser_init(True)

    file = open("downfile.txt")
    lineDatas = file.readlines();
    print u"总共要下载%d篇论文" %len(lineDatas);

    for line in lineDatas:
        keyword=line.strip('\n').decode('gbk')
        new_search = searchKey()
        new_search.search(keyword)
        Link = getKeywordDownloadLink(browser,keyword)
        do_download(browser,Link,fail_downLoadUrl)
    file.close()
    browser.quit()

    for n in range(3):
        if len(fail_downLoadUrl) !=0:
            print u"第%d次重新下载:" %(n)
            browser = browser_init(True)
            paper_downloadLinks=fail_downLoadUrl
            fail_downLoadUrl=[]
            do_download(browser, paper_downloadLinks, fail_downLoadUrl)
            browser.quit()
        else:
            break

    if fail_downLoadUrl:
        print fail_downLoadUrl
        with open("fail_download.txt","w") as f:
            f.writelines(fail_downLoadUrl)