import random
import sys
import time
import requests
from utils import log, config, parse_json, session, get_sku_title, send_wechat, ntp_sync, Timer
from concurrent.futures import ProcessPoolExecutor


class JDHelper(object):
    def __init__(self):
        self.config = config
        self.session = session()
        self.purchase_num = 1
        self.sku_id = self.config.get_config('config', 'sku_id')
        self.sell_url = dict()
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
                self.request_sell_url()
                self.request_checkout_page()
                self.submit_order()
            except Exception as e:
                log.info('抢购发生异常，稍后继续执行:', e)
            time.sleep(random.randint(10, 100) / 1000)

    # DESCRIPTION: 请求抢购页面URL：
    # INPUT:    None
    # OUTPUT:   None
    # AUTHOR:   XuKaikai@2021.03.13
    def get_sell_url(self):
        url = 'https://itemko.jd.com/itemShowBtn'
        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'skuId': self.sku_id,
            'from': 'pc',
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'Host': 'itemko.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        while True:
            rsp = self.session.get(url=url, headers=headers, params=payload)
            log.debug(rsp.text)
            rsp_json = parse_json(rsp.text)
            if rsp_json.get('url'):
                # https://divide.jd.com/user_routing?skuId=8654289&sn=c3f4ececd8461f0e4d7267e96a91e0e0&from=pc
                router_url = 'https:' + rsp_json.get('url')
                # https://marathon.jd.com/captcha.html?skuId=8654289&sn=c3f4ececd8461f0e4d7267e96a91e0e0&from=pc
                purchase_url = router_url.replace('divide',
                                                  'marathon').replace(
                                                      'user_routing',
                                                      'captcha.html')
                log.info("抢购链接获取成功: %s", purchase_url)
                return purchase_url
            else:
                log.info("抢购链接获取失败，稍后自动重试")
                time.sleep(random.randint(100, 300) / 1000)

    # DESCRIPTION:获取结算页面URL,用于设置cookies
    # INPUT:    None
    # OUTPUT:   None
    # AUTHOR:   XuKaikai@2021.03.13
    def request_sell_url(self):
        log.info('用户:{}'.format(self.get_username()))
        log.info('商品名称:{}'.format(get_sku_title()))
        self.timers.start()
        self.sell_url[self.sku_id] = self.get_sell_url()
        log.info('访问商品的抢购连接...')
        headers = {
            'Host': 'marathon.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        self.session.get(url=self.sell_url.get(self.sku_id),
                         headers=headers,
                         allow_redirects=False)

    # DESCRIPTION: 访问抢购订单结算页面
    # INPUT:    None
    # OUTPUT:   None
    # AUTHOR:   XuKaikai@2021.03.13
    def request_checkout_page(self):
        log.info('访问抢购订单结算页面...')
        url = 'https://marathon.jd.com/seckill/seckill.action'
        payload = {
            'skuId': self.sku_id,
            'num': self.purchase_num,
            'rid': int(time.time())
        }
        headers = {
            'Host': 'marathon.jd.com',
            'Referer': 'https://item.jd.com/{}.html'.format(self.sku_id),
        }
        self.session.get(url=url,
                         params=payload,
                         headers=headers,
                         allow_redirects=False)

    # DESCRIPTION:获取秒杀初始化信息(包括地址、发票、token等)
    # INPUT:    None
    # RETURN:   初始化信息组成的dict
    # AUTHOR:   XuKaikai@2021.03.13
    def _get_init_info(self):
        log.info('获取秒杀初始化信息...')
        url = 'https://marathon.jd.com/seckillnew/orderService/pc/init.action'
        data = {
            'sku': self.sku_id,
            'num': self.purchase_num,
            'isModifyAddress': 'false',
        }
        headers = {
            'Host': 'marathon.jd.com',
        }
        rsp = self.session.post(url=url, data=data, headers=headers)
        log.debug(rsp.text)
        return parse_json(rsp.text)

    # DESCRIPTION: 生成提交抢购订单所需的请求体参数
    # INPUT:    None
    # RETURN:   请求体参数组成的dict
    # AUTHOR：  XuKaikai@2021.03.13
    def _get_order_data(self):
        log.info('生成提交抢购订单所需参数...')
        # 获取用户秒杀初始化信息
        self._init_info[self.sku_id] = self._get_init_info()
        init_info = self._init_info.get(self.sku_id)
        default_address = init_info['addressList'][0]  # 默认地址dict
        invoice_info = init_info.get('invoiceInfo', {})  # 默认发票信息dict, 有可能不返回
        token = init_info['token']
        data = {
            'skuId': self.sku_id,
            'num': self.purchase_num,
            'addressId': default_address['id'],
            'yuShou': 'true',
            'isModifyAddress': 'false',
            'name': default_address['name'],
            'provinceId': default_address['provinceId'],
            'cityId': default_address['cityId'],
            'countyId': default_address['countyId'],
            'townId': default_address['townId'],
            'addressDetail': default_address['addressDetail'],
            'mobile': default_address['mobile'],
            'mobileKey': default_address['mobileKey'],
            'email': default_address.get('email', ''),
            'postCode': '',
            'invoiceTitle': invoice_info.get('invoiceTitle', -1),
            'invoiceCompanyName': '',
            'invoiceContent': invoice_info.get('invoiceContentType', 1),
            'invoiceTaxpayerNO': '',
            'invoiceEmail': '',
            'invoicePhone': invoice_info.get('invoicePhone', ''),
            'invoicePhoneKey': invoice_info.get('invoicePhoneKey', ''),
            'invoice': 'true' if invoice_info else 'false',
            'password': '',
            'codTimeType': 3,
            'paymentType': 4,
            'areaCode': '',
            'overseas': 0,
            'phone': '',
            'eid': config.get_config('config', 'eid'),
            'fp': config.get_config('config', 'fp'),
            'token': token,
            'pru': ''
        }
        return data

    # DESCRIPTION: 提交抢购订单
    # INPUT：   None
    # OUTPUT:   抢购结果
    # AUTHOR:   XuKaikai@03.13
    def submit_order(self):
        url = 'https://marathon.jd.com/seckillnew/orderService/pc/submitOrder.action'
        payload = {
            'skuId': self.sku_id,
        }
        self.order_data[self.sku_id] = self._get_order_data()
        log.info('提交抢购订单...')
        headers = {
            'Host':
            'marathon.jd.com',
            'Referer':
            'https://marathon.jd.com/seckill/seckill.action?skuId={0}&num={1}&rid={2}'
            .format(self.sku_id, self.purchase_num, int(time.time())),
        }
        rsp = self.session.post(url=url,
                                params=payload,
                                data=self.order_data.get(self.sku_id),
                                headers=headers)
        log.debug(rsp.text)
        rsp_json = parse_json(rsp.text)
        # 返回信息
        # 抢购失败：
        # {'errorMessage': '很遗憾没有抢到，再接再厉哦。', 'orderId': 0, 'resultCode': 60074, 'skuId': 0, 'success': False}
        # {'errorMessage': '抱歉，您提交过快，请稍后再提交订单！', 'orderId': 0, 'resultCode': 60017, 'skuId': 0, 'success': False}
        # {'errorMessage': '系统正在开小差，请重试~~', 'orderId': 0, 'resultCode': 90013, 'skuId': 0, 'success': False}
        # 抢购成功：
        # {"appUrl":"xxxxx","orderId":820227xxxxx,"pcUrl":"xxxxx","resultCode":0,"skuId":0,"success":true,"totalMoney":"xxxxx"}
        if rsp_json.get('success'):
            order_id = rsp_json.get('orderId')
            total_money = rsp_json.get('totalMoney')
            pay_url = 'https:' + rsp_json.get('pcUrl')
            log.info('抢购成功，订单号:{}, 总价:{}, 电脑端付款链接:{}'.format(
                order_id, total_money, pay_url))
            if config.get_config('messenger', 'enable') == 'true':
                success_message = "抢购成功，订单号:{}, 总价:{}, 电脑端付款链接:{}".format(
                    order_id, total_money, pay_url)
                send_wechat(success_message)
            return True
        else:
            log.info('抢购失败，返回信息:{}'.format(rsp_json))
            if config.get_config('messenger', 'enable') == 'true':
                error_message = '抢购失败，返回信息:{}'.format(rsp_json)
                send_wechat(error_message)
            return False