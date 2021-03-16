import ntplib
import time
from datetime import datetime
import os
import random
import json
import configparser
from lxml import etree
import requests
import re
import logging
import logging.handlers  # 导入logging模块后并不会自动导入其子模块handlers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36",
    "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14"
]


# DESCRIPTION:用于logging模块的初始化配置
# INPUT:  None
# OUTPUT: None
# AUTHOR: XuKaikai@2021.03.12
def log_config():
    log_filename = 'jd_log.log'  # 默认的配置文件名称
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)  # 设置默认打印等级

    # 设置默认打印格式[线程][时间][行号][等级]
    formatter = logging.Formatter(
        '[%(process)d:%(threadName)s][%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s]: %(message)s'
    )

    # 控制台打印信息输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # log文件信息输出
    file_handler = logging.handlers.RotatingFileHandler(log_filename,
                                                        maxBytes=104857600,
                                                        backupCount=5,
                                                        encoding='utf8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


log_config()
log = logging.getLogger()


# DESCRIPTION: 生成config类，用于读取和存储JDHelper应用中的各种配置信息
# INPUT:
#   file_name:  name of config file
# OUTPUT:   None
# AUTHOR:   XuKaikai@2021.03.12
class jd_config(object):
    def __init__(self, file_name='config.ini'):
        self.file_name = file_name
        # 将配置文件路径添加到搜索路径中
        self.path = os.path.join(os.path.realpath(os.getcwd()), self.file_name)
        if not (os.path.exists(self.path)):
            raise FileNotFoundError('No such file: config.ini in %s' %
                                    os.path.realpath(os.getcwd()))

        self.config = configparser.ConfigParser()
        self.config.read(self.path, encoding='utf8')

    def get_config(self, section, name):
        config = self.config.get(section, name)
        config = config.replace('?', '%')
        log.info('读取配置:' + section + '->' + name + ': ' + config)
        return config

    def set_config(self, section, name, value):
        # ini 配置文件不允许写入%, 不知道是为何，可能跟注释有关？
        # 所以暂时先用?代替%，读出是作反变换
        value = value.replace('%', '?')
        self.config.set(section, name, value)
        self.config.write(open(self.file_name, "w", encoding='utf8'))
        assert self.config.get(section, name) == value  # 判断是否写入成功
        log.info('设置配置:' + section + '-.' + name + '=' + value)


config = jd_config()


class Timer(object):
    def __init__(self, sleep_interval=0.05):
        # '2018-09-28 22:45:50.000'
        self.buy_time = datetime.strptime(
            config.get_config('config', 'buy_time'), "%Y-%m-%d %H:%M:%S.%f")
        self.sleep_interval = sleep_interval
        self.diff = self.time_diff()

    def time_diff(self):
        try:
            # 通过ping命令估计与服务器的延时
            result = os.popen('ping a.jd.com')
            res = result.read()
            txt = re.search('平均 = \d+', res).group(0)
            start = txt.rfind('=')
            delay = int(txt[start + 1:])
        except Exception as e:
            log.error(e)
            delay = 0
        log.info('与服务器链路时差为{}ms'.format(delay))

        # 获取服务器时间
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)

        server_time = int(js["serverTime"]) + delay
        local_time = int(time.time() * 1000)
        log.info('服务器时间 - 本地时间 = {}ms'.format(server_time - local_time))
        return server_time - local_time

    # DESCRIPTION : 从京东同步时间
    # INPUT:    NONE
    # OUTPUT:   NONE
    # AUTHOR:   XuKaikai@2021.3.15
    def time_sync(self):
        try:
            # 通过ping命令估计与服务器的延时
            result = os.popen('ping a.jd.com')
            res = result.read()
            txt = re.search('平均 = \d+', res).group(0)
            start = txt.rfind('=')
            delay = int(txt[start + 1:])
        except Exception as e:
            log.error(e)
            delay = 0
        log.info('与服务器链路时差为{}ms'.format(delay))

        # 获取服务器时间
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)

        server_time = int(js["serverTime"]) + delay
        local_time = int(time.time() * 1000)
        log.info('服务器时间 - 本地时间 = {}ms'.format(server_time - local_time))

        if server_time - local_time > 0:
            server_time = server_time + 1000

        _time = time.strftime('%X', time.localtime(server_time / 1000))
        # 将服务器获取到的时间更新为当前时间
        os.system('time {}'.format(_time))
        log.info('已同步系统时间: ' + time.strftime('%s' % (_time)))

    def start(self):
        buy_time_ms = int(
            time.mktime(self.buy_time.timetuple()) * 1000.0 +
            self.buy_time.microsecond / 1000)
        log.info('正在等待到达设定时间:%s(%s)' % (self.buy_time, buy_time_ms))

        while True:
            now = time.time() * 1000 + self.diff
            if now >= buy_time_ms:
                log.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)
                log.info('现在时间:' + str(now))


# DESCRIPTION : 使用NTP服务器同步系统时间
# INPUT:    NONE
# OUTPUT:   NONE
# AUTHOR:   XuKaikai@2021.3.7
def ntp_sync():
    c = ntplib.NTPClient()  # 新建NTP客户端
    ntp_pool = [
        'pool.ntp.org',
        'ntp1.aliyun.com',
        'edu.ntp.org.cn',
        'cn.pool.ntp.org',
        'cn.ntp.org.cn',
        'ntp2.aliyun.com',
        'tw.pool.ntp.org',
    ]

    responses = []
    for domain in ntp_pool:
        try:
            responses.append(c.request(domain))
        except ntplib.NTPException as e:
            log.error(e)
    ts = max([rsp.tx_time for rsp in responses])

    log.info([rsp.tx_time for rsp in responses])

    _date = time.strftime('%Y-%m-%d', time.localtime(ts))
    _time = time.strftime('%X', time.localtime(ts))

    # 将从NTP服务器获取到的时间更新为当前时间
    os.system('date {} && time {}'.format(_date, _time))
    log.info('已同步系统时间: ' + time.strftime('%s %s' % (_date, _time)))


# DESCRIPTION: 由于京东服务器返回的信息很多都是由jQuery
#   包裹的json串，所以需要单独把json串部分截取出来
# INPUT:
#   s:  服务器返回的字符串
# OUTPUT: 经过json格式化的字符串,是字典形式的
# AUTHOR: XuKaikai@2021.03.12
def parse_json(s: str) -> str:
    start = s.find('{')
    end = s.rfind('}') + 1
    return json.loads(s[start:end])


# DESCRIPTION : 根据cookies信息构造会话
# INPUT:    NONE
# OUTPUT:   NONE
# AUTHOR:   XuKaikai@2021.3.7
def session():
    cookies = config.get_config('config', 'cookies')  # 从配置文件读取cookies信息
    # 未读取到cookies信息时，使用浏览器登录一次
    if not (cookies) or cookies == '""':
        log.info('cookies为空')
        cookies = login_by_browser(config.get_config('config', 'user_name'),
                                   config.get_config('config', 'password'))

    # 构造cookjar
    d_cookies = {}
    for item in cookies.split(';'):
        name, value = item.split('=')
        d_cookies[name] = value

    cookiejar = requests.utils.cookiejar_from_dict(d_cookies)

    # 构造session
    s = requests.session()
    s.headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Connection": "keep-alive"
    }
    s.cookies = cookiejar
    return s


# DESCRIPTION: 返回商品名称信息
# INPUT:    None
# OUTPUT:   商品名称信息
# AUTHOR:   XuKaikai@2021.03.12
def get_sku_title():
    """获取商品名称"""
    url = 'https://item.jd.com/{}.html'.format(
        config.get_config('config', 'sku_id'))
    s = session()
    rsp = s.get(url)
    x_data = etree.HTML(rsp.text)
    sku_title = x_data.xpath('/html/head/title/text()')
    return sku_title[0]


def send_wechat(message):
    """推送信息到微信"""
    url = 'http://sc.ftqq.com/{}.send'.format(
        config.get_config('messenger', 'sckey'))
    payload = {"text": '抢购结果', "desp": message}
    requests.get(url, params=payload)


def login_by_browser(user_name: str, password: str) -> str:
    # 调用浏览器进行登录以保存cookies信息
    wd = webdriver.Firefox()
    wd.get('https://passport.jd.com/new/login.aspx')

    login_ele = WebDriverWait(wd, 60).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "login-tab-r")))  # 等待账号登录显示, 使用账号登录
    login_ele.click()

    try:
        # input_login = wd.find_element_by_id('username')  # 找到用户名输入框
        log.info('正在输入用户名')
        input_login = WebDriverWait(wd, 60).until(
            EC.presence_of_element_located((By.ID, "loginname")))  # 等待登录界面加载完成
        input_login.clear()  # 先清除输入框中的内容
        input_login.send_keys(user_name)  # 输入用户名

        log.info('正在输入密码')
        input_password = wd.find_element_by_id('nloginpwd')  # 找到密码输入框
        input_password.clear()  # 先清除输入框中的内容
        input_password.send_keys(password)

        button_login = wd.find_element_by_id('loginsubmit')  # 找到登录按钮
        button_login.click()  # 点击登录

        log.info('请在页面完成验证码操作：')
        try:
            WebDriverWait(wd, 300).until(
                EC.presence_of_element_located((By.ID, "ttbar-login")))
        except (NoSuchElementException, TimeoutException):
            log.error('登录失败')
        log.info('登录成功')

        # 读取浏览器的cookies并将其保存到配置文件中
        cookies_str = []
        cookies = wd.get_cookies()
        for cookie in cookies:
            cookies_str.append(cookie.get('name') + '=' + cookie.get('value'))
        cookies = ';'.join(cookies_str)
        log.info('从浏览器读取到cookies信息：' + cookies)
        config.set_config('config', 'cookies', cookies)

        wd.close()
        return cookies
    except Exception as e:
        log.error(e)
        log.error('页面登录失败')