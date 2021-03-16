# JDHelper

# 急求需要在京东抢购的商品链接做测试！！！

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
#### 1.使用cookies登录
若使用cookies登录，直接填写cookies信息即可，可以跳过步骤2
#### 2. 配置webdriver
下载一个Chromedriver放到chrome安装路径，或者gecodriver放到firefox的安装路径，然后把这个路径配置到环境变量里，在Login函数里修改对应的浏览器登录，在浏览器中完成人机验证操作即可，浏览器会自动关闭，然后将cookies信息保存下来，后续会默认使用cookies登录。后面若cookies失效，也可以使用这种办法更新cookies信息

#### 3. 在config.ini中填写产品ID和购买时间
产品ID就是商品页面选完型号后URL里的那一串数字，时间设置建议比官网时间提前半秒

#### 4.eid和fp暂时用不到，可填可不填，具体填法可参考原作者，后续可能会用到
> 不会的话参考原作者的issue https://github.com/zhou-xiaojun/jd_mask/issues/22

#### 5. 运行python main.py即可
在运行抢购程序前可以选择功能3进行服务器对时，由于windows设置时间只能精确到秒，所以仍然与服务器会有至多半秒的差距，不过这个差距在代码里也考虑到了
