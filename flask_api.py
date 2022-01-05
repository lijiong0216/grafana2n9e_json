#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask
from flask import request
import time
import requests
import json
import re
from dingtalkchatbot import chatbot

app = Flask(__name__)

def authorization():
    n9e_api_login = "http://172.18.205.58:18000/api/n9e/auth/login"
    password = "root.2020"
    username = "root"
    data_login = {"password": password,
                  "username": username}
    headers_login = {
        'Content-Type': 'application/json;charset=utf-8',
    }
    res = requests.post(n9e_api_login, json=data_login, headers=headers_login)
    print(res.text)
    print(type(res.text))
    authorization = "Bearer " + json.loads(res.text).get("dat").get("access_token")
    print(authorization)
    return authorization

def get_id(busi_group, btime):
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': authorization(),
        'Cookie': 'n9e=MTYzOTU1MDAwOHxEdi1CQkFFQ180SUFBUkFCRUFBQUp2LUNBQUVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dHQUFSeWIyOTB8pGuZdwXfcuWX_Lki-1RkaJrQ0vqk_FjmlcUH6m5vmvM='
    }
    # res_tagmetrics = requests.post(n9e_api_tagmetrics, json={}, headers=headers)
    # print(res_tagmetrics.text)
    n9e_api = "http://172.18.205.58:18000/api/n9e/busi-group/" + busi_group + "/alert-mutes"
    print(n9e_api)
    res = requests.get(n9e_api, headers=headers)
    print(res.status_code)
    print(res.text)
    dict_text = json.loads(res.text)

    for i in range(len(dict_text["dat"])):
        id_now = dict_text["dat"][i]["id"]
        if dict_text["dat"][i]["cause"] == "钉钉告警屏蔽" + btime:
            return str(id_now)

    return "not_found"




@app.route('/', methods=['GET'])
def hello_world():
    return '完成'


@app.route('/cancel', methods=['GET'])
def cancel():
    webhook = request.args.get('webhook')
    busi_group = request.args.get('metric')
    btime = request.args.get("time_block")

    id_result = get_id(busi_group, btime)
    print("id_result: ", id_result)
    xiaoding = chatbot.DingtalkChatbot(webhook)
    if id_result == "not_found":
        xiaoding.send_text("未找到需要取消的屏蔽规则", is_at_all=False)
    else:
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': authorization(),
            'Cookie': 'n9e=MTYzOTU1MDAwOHxEdi1CQkFFQ180SUFBUkFCRUFBQUp2LUNBQUVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dHQUFSeWIyOTB8pGuZdwXfcuWX_Lki-1RkaJrQ0vqk_FjmlcUH6m5vmvM='
        }
        # res_tagmetrics = requests.post(n9e_api_tagmetrics, json={}, headers=headers)
        # print(res_tagmetrics.text)
        n9e_api = "http://172.18.205.58:18000/api/n9e/busi-group/" + busi_group + "/alert-mutes"
        print(n9e_api)
        ids = {
            "ids": [int(id_result)]
        }
        res = requests.delete(n9e_api, json=ids, headers=headers)
        print(res.status_code)
        print(res.text)
        xiaoding.send_text("已取消屏蔽规则", is_at_all=False)

    return "取消"


@app.route('/arg', methods=['GET'])
def arg():
    # 读取GET请求中的arg字段值
    time_block = 3600
    time_block = int(request.args.get('time'))*900
    webhook = request.args.get('webhook')
    cluster = request.args.get("cluster")
    # busi_group = request.args.get('busi_group')
    busi_group = request.args.get('metric')
    #readable_expr = "sqs_ApproximateNumberOfMessagesVisible{queuename=~\"prod-dlq-openapi-invoice-result\"}>=1"
    readable_expr = request.args.get("readable_expression")
    tt = request.args.get("tt")
    #tags = re.findall(r'({.*?})', readable_expr)
    #tags = re.sub("\"", "", tags[0])
    # tags = readable_expr
    #     # tags = re.sub("~", "", tags)
    #     # #tags = re.sub("{", "", tags)
    #     # #tags = re.sub("}", "", tags)
    #     # #tags = re.sub(",", " ", tags)
    #     # tags = re.findall(".*?=.*? ", tags)
    #     # print("tags: ", tags)
    #     # tags1 = []
    #     # for i in tags:
    #     #     tags1.append(re.findall(".*? .*?", i))
    #     #     print("tags1", tags1)
    #     # #print(time, webhook)
    #     # tags_final = ""
    #     # for i in range(len(tags)):
    #     #     tags_final = tags_final + str(tags1[i][-1])
    #     # print("tags_final", tags_final)
    tags = readable_expr
    tags = re.sub("\[", "", tags)
    tags = re.sub("\]", "", tags)
    print("tags: ", tags)
    tag_group = tags.split(", ")
    tags_final = []
    for tag in tag_group:
        dict_panel = {"func": "==", "key": "", "value": ""}
        tag = re.sub("u\'", "", tag)
        tag = re.sub("\'", "", tag)
        print(tag)
        dict_panel["key"] = re.sub("=", "", re.findall(".*?=", tag)[0])
        dict_panel["value"] = re.sub("=", "", re.findall("=.*", tag)[0])
        print(dict_panel)
        tags_final.append(dict_panel)

    btime = int(time.time())
    print(time, webhook)
    data_block = {
      "tags": tags_final,
      "cluster": cluster,
      "cause": "钉钉告警屏蔽" + str(btime),
      "btime": btime,
      "etime": btime+time_block
    }
    # 3600 = 1hr
    # busi_group = "1"
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': authorization(),
        'Cookie': 'n9e=MTYzOTU1MDAwOHxEdi1CQkFFQ180SUFBUkFCRUFBQUp2LUNBQUVHYzNSeWFXNW5EQW9BQ0hWelpYSnVZVzFsQm5OMGNtbHVad3dHQUFSeWIyOTB8pGuZdwXfcuWX_Lki-1RkaJrQ0vqk_FjmlcUH6m5vmvM='
    }
    # res_tagmetrics = requests.post(n9e_api_tagmetrics, json={}, headers=headers)
    # print(res_tagmetrics.text)
    n9e_api = "http://172.18.205.58:18000/api/n9e/busi-group/" + busi_group + "/alert-mutes"
    print(n9e_api)
    res = requests.post(n9e_api, json=data_block, headers=headers)
    print(res.status_code)
    print(res.text)
    title = "已屏蔽: " + tt + "\n\n" + "标签: "
    for i in tags_final:
        title = title + i["key"] + "=" + i["value"]
    cancel_silence_url = "http://172.18.205.58:18000/api/n9e/busi-group/3/alert-mutes"
    server_url = "http://47.98.189.67:8080/cancel?user=flask"
    btns3 = [{"title": "取消屏蔽", "actionURL": "%s&webhook=%s&metric=%s&time_block=%s" % (server_url, webhook, busi_group, btime)}]
    xiaoding = chatbot.DingtalkChatbot(webhook)
    actioncard3 = chatbot.ActionCard(title='alert屏蔽', text=title, btns=btns3, btn_orientation=1,
                                     hide_avatar=0)
    xiaoding.send_action_card(actioncard3)
    return '屏蔽成功'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
