import random
import sys
import time
import requests
import json
from utils import log, config, parse_json, session, get_sku_title, send_wechat, ntp_sync, Timer
from concurrent.futures import ProcessPoolExecutor


class JDHelper(object):
    def __init__(self):
        self.config = config
        self.session = session()
        self.purchase_num = 1
        self.sku_id = self.config.get_config('config', 'sku_id')
        self.order_data = dict()
        self.init_info = dict()
        self.timers = Timer()

        log.info('正在同步系统时间')
        # self.timers.time_sync()

    # DESCRIPTION: 调用多个进程异步执行抢购程序
    # INPUT:
    #   work_count: 异步程序个数
    # OUTPUT:
    # AUTHOR:2021.03.13
    def pool_executor(self, work_count=1):
        with ProcessPoolExecutor(work_count) as pool:
            for i in range(work_count):
                pool.submit(self.flash_sale)

    # DESCRIPTION: 获取用户购物车，用以验证登录是否成功
    # INPUT:    None
    # OUTPUT:   None
    # Author:   XuKaikai@2021.03.12
    def login(self):
        for flag in range(1, 3):
            try:
                targetURL = 'https://order.jd.com/center/list.action'
                payload = {
                    'rid': str(int(time.time() * 1000)),
                }
                resp = self.session.get(url=targetURL,
                                        params=payload,
                                        allow_redirects=False)
                if resp.status_code == requests.codes.OK:
                    log.info('校验是否登录[成功]')
                    log.info('用户:{}'.format(self.get_username()))
                    return True
                else:
                    log.info('校验是否登录[失败]')
                    log.info('请重新输入cookie')
                    time.sleep(1)
                    continue
            except Exception as e:
                log.error(e)
                log.info('第【%s】次失败请重新获取cookie', flag)
                time.sleep(1)
                continue
        sys.exit(1)

    # DESCRIPTION: 预约抢购
    # INPUT:    None
    # OUTPUT:   None
    # AUTHOR:   XuKaikai@2021.03.13
    def reserve(self):
        self.login()
        log.info('登录成功')

        log.info('商品名称:{}'.format(get_sku_title()))

        url = 'https://yushou.jd.com/youshouinfo.action?'
        payload = {
            'callback': 'fetchJSON',
            'sku': self.sku_id,
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }

        log.info('正在进行预约')
        rsp = self.session.get(url=url, params=payload, headers=headers)
        log.debug(rsp.text)
        rsp_json = parse_json(rsp.text)
        reserve_url = rsp_json.get('url')
        # self.timers.start()
        while True:
            try:
                self.session.get(url='https:' + reserve_url)
                log.info('预约成功，已获得抢购资格 / 您已成功预约过了，无需重复预约')
                if config.get_config('messenger', 'enable') == 'true':
                    success_message = "预约成功，已获得抢购资格 / 您已成功预约过了，无需重复预约"
                    send_wechat(success_message)
                break
            except Exception as e:
                log.error('预约失败正在重试...')

    # DESCRIPTION: 通过向服务器发送特定报文用以验证登录是否成功
    # INPUT:    None
    # OUTPUT:   cookies文件对应的用户名
    # Author:   XuKaikai@2021.03.12
    def get_username(self):
        url = 'https://passport.jd.com/user/petName/getUserInfoForMiniJd.action'
        payload = {
            'callback': 'jQuery'.format(random.randint(1000000, 9999999)),
            '_': str(int(time.time() * 1000)),
        }

        headers = {'Referer': 'https://order.jd.com/center/list.action'}

        rsp = self.session.get(url=url, params=payload, headers=headers)
        try_count = 5
        while not rsp.text.startswith('jQuery'):
            try_count = try_count - 1
            if try_count > 0:
                rsp = self.session.get(url=url,
                                       params=payload,
                                       headers=headers)
            else:
                break

        return parse_json(rsp.text).get('nickName')

    # DESCRIPTION:抢购程序
    # INPUT:    None
    # OUTPU:    抢购结果
    # AUTHOR:   2021.03.13
    def flash_sale(self):
        self.login()
        log.info('登录成功')
        while True:
            try:
                if not (self.checkout()):
                    continue
                if not (self.submit_order()):
                    continue
                else:
                    sys.exit(0)
            except Exception as e:
                log.info('抢购发生异常，稍后继续执行:', e)
            time.sleep(random.randint(10, 100) / 1000)

    # DESCRIPTION:添加抢购商品到购物车，然后抢购开始后直接进结算页面
    # INPUT:    None
    # OUTPUT:   None
    # AUTHOR:   XuKaikai@2021.03.13
    def toCart(self):
        log.info('正在访问商品的抢购连接......')
        url = 'https://cart.jd.com/gate.action'
        payload = {
            'pcount': self.purchase_num,
            'ptype': '1',
            'pid': self.sku_id
        }
        headers = {
            'Host': 'cart.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        rsp = self.session.get(url=url, params=payload, headers=headers)
        if rsp.status_code == requests.codes.OK:
            log.info('成功加入购物')
        else:
            log.error('添加购物车失败，状态码：' + str(rsp.status_code))
        return True

    # DESCRIPTION: 访问抢购订单结算页面
    # INPUT:    None
    # OUTPUT:   None
    # AUTHOR:   XuKaikai@2021.03.13
    def checkout(self):
        url = 'https://trade.jd.com/shopping/order/getOrderInfo.action'
        headers = {
            'Host': 'trade.jd.com',
            'Referer': 'https://cart.jd.com/cart_index/',
        }

        rsp = self.session.get(url=url, headers=headers)
        if rsp.status_code == requests.codes.OK:
            log.info('去结算')
            return True
        else:
            log.error('访问订单结算页面失败，状态码：' + str(rsp.status_code) + ' 正在重试...')
            return False

    # DESCRIPTION: 提交抢购订单
    # INPUT：   None
    # OUTPUT:   抢购结果
    # AUTHOR:   XuKaikai@03.13
    def submit_order(self):
        url = 'https://trade.jd.com/shopping/order/submitOrder.action?='
        payload = {'presaleStockSign': '1'}
        headers = {
            'Host': 'trade.jd.com',
            'Referer':
            'https://trade.jd.com/shopping/order/getOrderInfo.action',
        }
        rsp = self.session.get(url=url, params=payload, headers=headers)
        if rsp.status_code == requests.codes.OK:
            log.info('正在提交订单...')
        else:
            log.error('订单提交失败，状态码：' + str(rsp.status_code) + ' 正在重试...')

        try:
            rsp_json = json.loads(rsp.text)
        except Exception as e:
            log.error('提交订单失败，请稍后重试')
            return False
        if rsp_json.get('success'):
            order_id = rsp_json.get('orderId')
            log.info('抢购成功，订单号:{},'.format(order_id))
            if config.get_config('messenger', 'enable') == 'true':
                success_message = "抢购成功，订单号:{}, 请尽快到PC端进行付款".format(order_id)
                send_wechat(success_message)
            return True
        else:
            log.info('抢购失败，返回信息:{}'.format(rsp_json))
            return False