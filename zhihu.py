# -*- coding: utf-8 -*-
# 需求 1.使用代理 2.抓取知乎关键字保存JSON文件到本地
# QUESTION1 post的是captcha_style 但是实际上是captcha
import requests
import time
import os
import random
import json
from bs4 import BeautifulSoup
# 禁用安全请求警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


#获取代理
def zhproxy():
    proxies = [{'http': 'http://1175.155.24.30:808'},
               {'http': 'http://115.220.1.13:808'},
               {'http': 'http://175.155.25.50:808'},
               {'http': 'http://113.71.115.166:808'},
               {'http': 'http://175.155.25.42:808'}]

    #随机提取proxy，如果检测失败则删除，成功则返回
    for i in range(len(proxies)):
        proxy = random.choice(proxies)
        try:
            if requests.get('http://www.baidu.com', proxies=proxy,timeout=10).status_code == 200:
                return proxy
        except:
            proxies.remove(proxy)
            continue

# 获取验证码
def captcha(captcha_data):
    with open("知乎验证码.gif", "wb") as f:
        f.write(captcha_data)
    text = input("请输入验证码：")
    return text


def zhlogin():
    # 登陆知乎
    # post信息：_xsrf=d89527cccf6398cc4cbf36688173415c&password=passwordpassword&captcha_type=cn&email=23333@qq.com
    # 获取首页登录需要的信息 同时保存cookie
    sess = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}

    html = sess.get('https://www.zhihu.com/#signin', headers=headers,verify = False).text
    soup = BeautifulSoup(html, 'lxml')
    xsrf = soup.find('input', attrs={'name': '_xsrf'}).get('value')

    # 获取验证码
    captcha_url = "https://www.zhihu.com/captcha.gif?r=%d&type=login" % (time.time() * 1000)
    captcha_data = sess.get(captcha_url, headers=headers).content
    text = captcha(captcha_data)
    os.remove('知乎验证码.gif')

    data = {
        '_xsrf': xsrf,
        "email": input('请输入你的email账号：'),
        "password":input('请输入你的密码'),
        "captcha": text}
    # 向登陆服务器进行验证，验证通过后进行查询
    proxy = zhproxy()
    response = sess.post('https://www.zhihu.com/login/email', data=data, headers=headers
                         ,proxies=proxy)

    # 进行关键字查询，获取10页的内容
    findtext = [x for x in input('输入要查找的内容以<，>分隔:').split('，')]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}

    response = sess.get('https://www.zhihu.com/r/search?q=%s&correction=0&type=content&offset=100' % findtext
        ,headers=headers,proxies=proxy,verify = False)

    # 将回答保存到本地保存（先将unicode转换成utf-8，然后禁用ascii）
    for answer in findtext:
        answerpath = 'd:/study/知乎%s.json' %answer
        with open(answerpath, 'w') as f:
            encod = json.loads(response.text,encoding='utf-8')
            jsond = json.dumps(encod,ensure_ascii=False)
            ##response.text.encode('utf-8')(变成bytes不能用）
            f.write(jsond)

zhlogin()
