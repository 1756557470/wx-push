import json

import requests
from requests import get, post

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
    print(access_token)
    return access_token


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


def send_text(note_ch, note_en, _message, useridlist=['name1|name2']):
    useridstr = "|".join(useridlist)  # userid 在企业微信-通讯录-成员-账号
    response = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}"
                            .format(corpid, corpsecret))
    data = json.loads(response.text)
    access_token = data['access_token']
    json_dict = {
        "touser": useridstr,
        "msgtype": "textcard",
        "agentid": 1000002,
        "textcard": {
            "title": "小助手",
            "description": note_ch,

            "url": "URL",
            "btntxt": "更多"
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


if __name__ == '__main__':
    note_ch, note_en = get_ciba()
    get_access_token()
    send_text(note_ch, note_en, 'hello world', ['LiYiChen'])
