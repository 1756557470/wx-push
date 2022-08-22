import json
import http.client, urllib

conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名


headers = {'Content-type': 'application/x-www-form-urlencoded'}

# 获取节假日
def get_holiday():
    params = urllib.parse.urlencode({'key': 'b8843645156ff16cf819a0849f46a656'})
    conn.request('POST', '/jiejiari/index', params, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode('utf-8'))
    data2 = json.loads(data)
    if data2['newslist'][0]['cnweekday'] == "星期五":
        msg = "工作辛苦了，明天就要休息啦~"
    elif data2['newslist'][0]['cnweekday'] == "星期日":
        msg = "明天就要工作了，呜呜呜~"
    return msg


def get_tq():
    params = urllib.parse.urlencode({'key': 'b8843645156ff16cf819a0849f46a656','city':'松江区'})
    conn.request('POST', '/tianqi/index', params, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode('utf-8'))
    data2 = json.loads(data)
    area = data2["newslist"][0]["area"]
    date = data2["newslist"][0]["date"]
    week = data2["newslist"][0]["week"]
    weatherimg = data2["newslist"][0]["weatherimg"]
    print(area)
    print(date)
    print(week)
    print(weatherimg)


if __name__ == '__main__':
    get_tq()
