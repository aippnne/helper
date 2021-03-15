#JDHelper

##### 非常感谢原作者 https://github.com/andyzys/jd_seckillk、 https://github.com/phanker/jd-seckill-maotai等项目提供的代码（未全部列出），本项目在以上项目基础上修改而来，在使用以上项目抢购K40的时候发现接口 https://itemko.jd.com/itemShowBtn 好像失效了，目前返回的url一直是空的，所以使用以上项目重写抢购流畅

## 主要功能

- 登陆京东商城（[www.jd.com](http://www.jd.com/)）
  - 初次登陆可使用浏览器登录
- 预约
  - 定时自动预约
- 秒杀预约后等待抢购
  - 定时开始自动抢购

## 运行环境

- [Python 3](https://www.python.org/)

## 第三方库

- 需要使用到的库已经放在requirements.txt，使用pip安装的可以使用指令  
`pip install -r requirements.txt`

## 使用教程  
#### 1. 网页扫码登录
#### 2. 填写config.ini配置信息 
(1)eid,和fp找个普通商品随便下单,然后抓包就能看到,这两个值可以填固定的 
> 不会的话参考原作者的issue https://github.com/zhou-xiaojun/jd_mask/issues/22

(2)cookies_string,sku_id
初次登陆可在配置文件中填写用户名和密码并清空cookies信息，脚本会调用浏览器进行登录并保存cookies信息，后续登录可直接使用cookies登录
sku_id为商品对应的ID，这里我用的K40 12GB+256GB的版本

(3)时间配置采用NTP时间同步策略和京东服务器时间同步策略两种，可根据需要自行选择

#### 3.运行main.py 
根据提示选择相应功能即可