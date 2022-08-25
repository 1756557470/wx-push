# -*- coding: utf-8 -*-
# @Time      :     2022/8/25 11:07
# @Author    :     Liyichen.0827
import requests
from requests import get
import http.client
import json
import os
import random
import sys
import urllib
from datetime import datetime, date
from time import localtime

with open("config.txt", encoding="utf-8") as f:
    config = eval(f.read())

    # corpid
    corpid = config["corpid"]
    # corpsecret
    corpsecret = config["corpsecret"]


def get_access_token():
    post_url = ("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}"
                .format(corpid, corpsecret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
    # print(access_token)
    return access_token




conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名

headers = {'Content-type': 'application/x-www-form-urlencoded'}
params = urllib.parse.urlencode({'key': 'b8843645156ff16cf819a0849f46a656'})
def get_caihongpi():
    conn.request('POST', '/caihongpi/index', params, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    caihong = data["newslist"][0]["content"]
    return caihong

def get_holiday():
    msg = None
    conn.request('POST', '/jiejiari/index', params, headers)
    res = conn.getresponse()
    data = res.read()
    data2 = json.loads(data)
    if data2['newslist'][0]['cnweekday'] == "星期四":
        msg = "工作辛苦了，明天就要休息啦~"
    elif data2['newslist'][0]['cnweekday'] == "星期日":
        msg = "明天就要工作了，呜呜呜~"
    return msg
def get_tq():
    tip = None
    params = urllib.parse.urlencode({'key': 'b8843645156ff16cf819a0849f46a656', 'city': config["city"]})
    conn.request('POST', '/tianqi/index', params, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    area = data["newslist"][0]["area"]
    today_date = data["newslist"][0]["date"]
    week = data["newslist"][0]["week"]
    weather = data["newslist"][0]["weather"]

    # 当前温度
    real = data["newslist"][0]["real"]
    # 最高温度
    lowest = data["newslist"][0]["lowest"]
    # 最低温度
    highest = data["newslist"][0]["highest"]
    # 风向
    wind = data["newslist"][0]["wind"]
    # 提示
    tips = data["newslist"][0]["tips"]

    if "雨" in weather:
        tip = "🌧"
    elif "晴" in weather:
        tip = "☀"
    else:
        tip = "🌤"

    return area, today_date, week, weather, real, lowest, highest, tips, tip


year = localtime().tm_year
month = localtime().tm_mon
day = localtime().tm_mday
today = datetime.date(datetime(year=year, month=month, day=day))
def get_record():
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    return  love_days

def get_birthday():
    # 获取生日的月和日
    birthday_month = int(config["birthday"].split("-")[1])
    birthday_day = int(config["birthday"].split("-")[2])
    # 今年生日
    year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day

def send_text(area, today_date, week, weather, real, lowest, highest, tips, tip, caihong, love_days,birth_day,msg,
              useridlist=['name1|name2']):
    useridstr = "|".join(useridlist)  # userid 在企业微信-通讯录-成员-账号
    response = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}"
                            .format(corpid, corpsecret))
    data = json.loads(response.text)
    access_token = data['access_token']
    json_dict = {
        "touser": useridstr,
        "msgtype": "template_card",
        "agentid": 1000002,
        "msgtype": "textcard",
        "textcard": {
            "title": "🌈每日推送🌈",
            "description":
                today_date + "，" + week + ", "+msg+"\n\n"
                "沪漂第" + love_days + "天,"+"23岁生日还有" + birth_day+"天\n\n"                          
                "🏙" + config["provinces"] + area + ", 今日天气: " + weather + "  " + tip + "\n\n"
                "🌈当前温度: " + real + "\n\n"
                "🥶最低温度: " + lowest + "\n\n"
                "🥵最高温度: " + highest + "\n\n"
                "<div class=\"highlight\"> Tips: " + tips + "</div>"+"\n"                   
               "" + caihong
            ,
            "url": "URL",
            # "btntxt": "更多"
        },
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    json_str = json.dumps(json_dict)
    response_send = requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
        access_token=access_token), data=json_str)
    print("send to " + useridstr + ' ' + json.loads(response_send.text)['errmsg'])
    return json.loads(response_send.text)['errmsg'] == 'ok'


# if __name__ == '__main__':
def main_handler(event, context):
    caihong = get_caihongpi()
    area, today_date, week, weather, real, lowest, highest, tips, tip =get_tq()
    love_days = get_record()
    get_access_token()
    birthday = get_birthday()
    msg = get_holiday()
    send_text(area, today_date, week, weather, real, lowest, highest, tips, tip,caihong,love_days,birthday,msg, ['LiYiChen'])


