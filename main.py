import random
from time import localtime
from requests import get, post
from datetime import datetime, date
import sys
import os
import json
import http.client, urllib

with open("config.txt", encoding="utf-8") as f:
    config = eval(f.read())


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(90)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_birthday(birthday, year, today):
    # 获取生日的月和日
    birthday_month = int(birthday.split("-")[1])
    birthday_day = int(birthday.split("-")[2])
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


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名

headers = {'Content-type': 'application/x-www-form-urlencoded'}
params = urllib.parse.urlencode({'key': 'b8843645156ff16cf819a0849f46a656'})


# 获取节假日
def get_holiday():
    msg = None
    conn.request('POST', '/jiejiari/index', params, headers)
    res = conn.getresponse()
    data = res.read()
    data2 = json.loads(data)
    if data2['newslist'][0]['cnweekday'] == "星期二":
        msg = "工作辛苦了，明天就要休息啦~"
    elif data2['newslist'][0]['cnweekday'] == "星期日":
        msg = "明天就要工作了，呜呜呜~"
    return msg


def get_tq():
    tip = None
    params = urllib.parse.urlencode({'key': 'b8843645156ff16cf819a0849f46a656', 'city': '松江区'})
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
        tip = "今天有雨，出门记得带伞嗷~~"
    elif "晴" in weather:
        tip = "今天天气不错，要元气满满嗷~~"
    elif 38 <= lowest:
        tip = "今天天气很热，出门注意防晒嗷~~"

    return area, today_date, week, weather, real, lowest, highest, wind, tips, tip


def send_message(to_user, access_token, area, today_date, week, weather, real, lowest, highest, wind, tips, note_ch,
                 note_en, msg, tip):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)

    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "today_date": {
                "value": today_date,
                "color": '#2E2D2C'
            },
            "week": {
                "value": week,
                "color": '#E84022'
            },
            "area": {
                "value": area,
                "color": '#089308'
            },
            "weather": {
                "value": weather,
                "color": get_color()
            },
            "real": {
                "value": real,
                "color": get_color()
            },
            "lowest": {
                "value": lowest,
                "color": get_color()
            },
            "highest": {
                "value": highest,
                "color": get_color()
            },
            "wind": {
                "value": wind,
                "color": get_color()
            },
            "tips": {
                "value": tips,
                "color": get_color()
            },
            "love_day": {
                "value": love_days,
                "color": get_color()
            },
            "note_en": {
                "value": note_en,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            },
            "msg": {
                "value": msg,
                "color": get_color()
            },
            "tip": {
                "value": tip,
                "color": get_color()
            }
        }
    }
    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day = get_birthday(value, year, today)
        # 将生日数据插入data
        data["data"][key] = {"value": birth_day, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    # def main_handler(event, context):
    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入省份和市获取天气信息
    area, today_date, week, weather, real, lowest, highest, wind, tips, tip = get_tq()
    # 获取词霸每日金句
    note_ch, note_en = get_ciba()
    msg = get_holiday()
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, area, today_date, week, weather, real, lowest, highest, wind, tips, note_ch,
                     note_en, msg, tip)

