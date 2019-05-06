# git@github.com:wgr1009/wx_weather.git

'''
    通过wxpy获取微信联系人，利用apshedule模块作为定时, 从高德地图指定接口获取天气数据发送到微信联系人
    key: 
    url: https://restapi.amap.com/v3/weather/weatherInfo?parameters


'''

import requests
import json
import csv
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from wxpy import *
import logging

class WxSpider:

    def __init__(self):
        self.baseurl = 'https://restapi.amap.com/v3/weather/weatherInfo?'
        self.baseurl2 = "http://open.iciba.com/dsapi/"
        self.headers = {
            "User-Agent":'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Mobile Safari/537.36',
      
        }

        LOG_FORMAT = '%(asctime)s : %(levelname)s : %(message)s'
        logging.basicConfig(filename='loging.log', level=logging.INFO, format=LOG_FORMAT)

        self.wxbot = Bot()

    def get_citycode(self):
        '''
        获取城市编码code
        :return:
        '''

        with open('AMap_adcode_citycode.csv', 'r', encoding='utf-8') as csvfile:
            city_reader = csv.reader(csvfile)
            city = []
            for row in city_reader:
                city_code = {'city': '', 'code': ''}
                city_code['city'] = row[0]
                city_code['code'] = row[1]
                city.append(city_code)
            return city

    def get_weather_data(self):
        '''
        通过高德天气接口获取实时天气
        :return: res
        '''

        params = {
            'key': '',
            'city': '110000',
            'extensions': 'base',
            'output': 'JSON',
        }
        # city = input('请输入查询城市名称: ')  # 实际是城市的城市编码
        # for k in self.get_citycode():
        #     if k['city'] != city:
        #         continue
        #     else:
        #         params['city'] = k['code']
        #         break
        # params['extensions'] = input('请输入查询类型base/all(实况/预报):')
        rep = requests.get(self.baseurl, headers=self.headers, params=params)
        rep.encoding = 'utf-8'
        res = rep.text

        if params['extensions'] == 'base':
            self.parse_weather_data(res)

        else:
            self.parse_weather_alldata(res)

    def get_jinshan(self):
        """获取金山词霸每日一句，英文和翻译"""

        headers = {'User-Agent': self.headers["User-Agent"]}
        r = requests.get(self.baseurl2, headers=headers)
        content = r.json()['content']
        note = r.json()['note']

        return content +'\n' +  note

    def parse_weather_data(self, res):
        '''
        解析返回的天气数据
        :param res:
        :return:
        '''
        res = json.loads(res)
        if res['status'] == '0':
            print('查询失败')
        message = res['lives'][0]
        province = message['province']
        city = message['city']
        weather = message['weather']
        humidity = message['humidity']
        temperature = message['temperature']
        winddirection = message['winddirection']
        windpower = message['windpower']
        reporttime = message['reporttime']

        send_message = '天气预报来喽~每天准时更新呦~\n' \
                       + '当前城市: {} \n'.format(province + city) \
                       + '当前天气: {}\n'.format(weather) \
                       + '当前温度: {}℃\n'.format(temperature) \
                       + '当前湿度: {} %\n'.format(humidity) \
                       + '当前风向: {}\n'.format(winddirection) \
                       + '当前风力: {} 级\n'.format(windpower) \
                       + '发布时间: {}\n'.format(reporttime) \
                       + '\n' \
                       + '每日一句\n' \
                       + self.get_jinshan()

        self.send_message(send_message)

    def send_message(self, message):
        '''
        连接微信发送到指定联系人
        :param message:
        :return:
        '''
        my_friend = self.wxbot.friends().search('皮克')[0]
        my_friend.send(message)


    def parse_weather_alldata(self, res):
        res = json.loads(res)
        print(res)


    def main(self):
        try:
            self.get_weather_data()
            # logging.info('send_message OK!')
        except:
            print('发生错误')


if __name__ == '__main__':
    app = WxSpider()
    sched = BlockingScheduler()
    sched.add_job(app.main, 'cron', hour=8, minute=0)
    # sched.add_job(app.main, 'interval', seconds=5)
    sched.start()


# sched.add_job(app.main, 'interval', seconds=5)   # 每5秒执行一次程序  interval 间隔执行
# git@github.com:wgr1009/wx_weather.git
