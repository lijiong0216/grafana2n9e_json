#!/usr/bin/python
# -*- coding: UTF-8 -*-
import __future__
import time
import re
from dingtalkchatbot import chatbot
import sys
import json
import urllib2
import smtplib
from email.mime.text import MIMEText
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
notify_channel_funcs = {
  "email":"email",
  "sms":"sms",
  "voice":"voice",
  "dingtalk":"dingtalk",
  "wecom":"wecom"
}

mail_host = "smtp.163.com"
mail_port = 994
mail_user = "ulricqin"
mail_pass = "password"
mail_from = "ulricqin@163.com"

class Sender(object):
    @classmethod
    def send_email(cls, payload):
        users = payload.get('event').get("notify_users_obj")

        emails = {}
        for u in users:
            if u.get("email"):
                emails[u.get("email")] = 1

        if not emails:
            return

        recipients = emails.keys()
        mail_body = payload.get('tpls').get("mailbody.tpl", "mailbody.tpl not found")
        message = MIMEText(mail_body, 'html', 'utf-8')
        message['From'] = mail_from
        message['To'] = ", ".join(recipients)
        message["Subject"] = payload.get('tpls').get("subject.tpl", "subject.tpl not found")

        try:
            smtp = smtplib.SMTP_SSL(mail_host, mail_port)
            smtp.login(mail_user, mail_pass)
            smtp.sendmail(mail_from, recipients, message.as_string())
            smtp.close()
        except smtplib.SMTPException, error:
            print(error)

    @classmethod
    def send_wecom(cls, payload):
        users = payload.get('event').get("notify_users_obj")

        tokens = {}

        for u in users:
            contacts = u.get("contacts")
            if contacts.get("wecom_robot_token", ""):
                tokens[contacts.get("wecom_robot_token", "")] = 1

        opener = urllib2.build_opener(urllib2.HTTPHandler())
        method = "POST"

        for t in tokens:
            url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(t)
            body = {
                "msgtype": "markdown",
                "markdown": {
                    "content": payload.get('tpls').get("wecom.tpl", "wecom.tpl not found")
                }
            }
            request = urllib2.Request(url, data=json.dumps(body))
            request.add_header("Content-Type",'application/json;charset=utf-8')
            request.get_method = lambda: method
            try:
                connection = opener.open(request)
                print(connection.read())
            except urllib2.HTTPError, error:
                print(error)

    @classmethod
    def send_dingtalk(cls, payload):
        users = payload.get('event').get("notify_users_obj")

        tokens = {}
        phones = {}

        for u in users:
            if u.get("phone"):
                phones[u.get("phone")] = 1

            contacts = u.get("contacts")
            if contacts.get("dingtalk_robot_token", ""):
                tokens[contacts.get("dingtalk_robot_token", "")] = 1

        opener = urllib2.build_opener(urllib2.HTTPHandler())
        method = "POST"

        for t in tokens:
            webhook = "https://oapi.dingtalk.com/robot/send?access_token={}".format(t)
            silence_url = "http://47.98.189.67:8080/arg?user=flask"
            #silence_url = "http://127.0.0.1:5000/arg?user=flask"
            event_obj = payload.get("event")
            metric = str(payload.get("event").get("group_id"))
            #alert_content = "级别状态:"
            # + payload.get("event").get("rule_name")
            #if payload.get("event").get("is_recovered"):
        #       alert_content = alert_content + " P" + str(payload.get("event").get("severity")) + "恢复" + "\n\n"
            #else:
        #       alert_content = alert_content + " P" + str(payload.get("event").get("severity")) + "告警" + "\n\n"
            alert_content = ""
            # + payload.get("event").get("rule_name")
            readable_expr = event_obj.get("tags")
            alert_bot = chatbot.DingtalkChatbot(webhook)
            tt = payload.get("event").get("rule_name")
            tt = tt.encode('UTF-8')
            btns3 = [{"title": "静默15分钟", "actionURL": "%s&time=1&webhook=%s&metric=%s&readable_expression=%s&cluster=Default&tt=%s" % (
            silence_url, webhook, metric, readable_expr, tt)},
                     {"title": "静默30分钟", "actionURL": "%s&time=2&webhook=%s&metric=%s&readable_expression=%s&cluster=Default&tt=%s" % (
                     silence_url, webhook, metric, readable_expr, tt)},
                     {"title": "静默1小时", "actionURL": "%s&time=4&webhook=%s&metric=%s&readable_expression=%s&cluster=Default&tt=%s" % (
                     silence_url, webhook, metric, readable_expr, tt)},
                     {"title": "静默2小时", "actionURL": "%s&time=8&webhook=%s&metric=%s&readable_expression=%s&cluster=Default&tt=%s" % (
                     silence_url, webhook, metric, readable_expr, tt)}]
            if payload.get("event").get("is_recovered"):
                alert_content = "<font color=#008000>" + "级别状态:" + " P" + str(payload.get("event").get("severity")) + "恢复" + "</font>" + "\n\n"
                btns3 = [{"title": "完成", "actionURL": "http://47.98.189.67:8080/"}]
            else:
                alert_content = "<font color=#ff0000>" + "级别状态:" + " P" + str(payload.get("event").get("severity")) + "告警" + "</font>" + "\n\n"
                alert_bot.send_text("请查看告警", is_at_all=True)
            tags_special = ["hostname", "instance", "slbname", "flag", "ipaddr", "queuename"]
            alert_content = alert_content + "规则名称:" + payload.get("event").get("rule_name") + "\n\n"
            # alert_content = alert_content + "表达式:" + payload.get("event").get("prom_ql") + "\n\n"
            str_in = payload.get("event").get("prom_ql")
            compare_list = [">", "<", ">=", "<=", "=="]
            for compare_index in compare_list:
                try:
                    current = re.findall(compare_index + ".*", str_in)[0]
                except:
                    pass
            alert_content = alert_content + "标准值:" + re.findall("\d+", current)[0] + "\n\n"
            alert_content = alert_content + "当前值:" + str(payload.get("event").get("trigger_value")) + "\n\n"
            alert_content = alert_content + "触发时间:" + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(payload.get("event").get("trigger_time"))) + "\n\n"
            str1 = str(payload.get("event").get("tags"))
            text_send = ""
            for tags_i in tags_special:
                try:
                    # alert_bot.send_text("lmt " + re.findall("hostname=.*? ", str1)[0], is_at_all=False)
                    text_send = text_send + re.sub("'", "", re.findall(tags_i + "=.*?'", str1)[0]) + "\n"
                except:
                    pass
            alert_content = alert_content + "标签:" + "\n\n" + text_send
            #alert_content = alert_content + "标签:" + str(payload.get("event").get("tags")) + "\n\n"
            # body = {
            #     "msgtype": "text",
            #         "content": payload.get('tpls').get("dingtalk.tpl", "dingtalk.tpl not found")
            #     },
            #     "at": {
            #         "atMobiles": phones.keys(),
            #         "isAtAll": False
            #     }
            # }
            # request = urllib2.Request(url, data=json.dumps(body))
            # request.add_header("Content-Type",'application/json;charset=utf-8')
            # request.get_method = lambda: method
            # try:
            #     connection = opener.open(request)
            #     print(connection.read())
            # except urllib2.HTTPError, error:
            #     print(error)
            #if "恢复" in alert_content:
            #    alert_content = alert_content.join(["<font color=#008000>", "</font>"])
            #    btns3 = [{"title": "完成", "actionURL": "http://47.98.189.67:8080/"}]

            #else:
            #    alert_content = alert_content.join(["<font color=#ff0000>", "</font>"])
            #    alert_bot.send_text("请查看告警", is_at_all=True)
            actioncard3 = chatbot.ActionCard(title='alert', text=alert_content, btns=btns3, btn_orientation=1,
                                             hide_avatar=0)
            alert_bot.send_action_card(actioncard3)
            # alert_bot.send_text("lmt" + event_obj.get("tags"), is_at_all=False)
            #str1 = str(payload.get("event").get("tags"))
            #text_send = ""
            # alert_bot.send_text("lmt1" + str1, is_at_all=False)
            #for tags_i in tags_special:
            #    try:
                    # alert_bot.send_text("lmt " + re.findall("hostname=.*? ", str1)[0], is_at_all=False)
            #        text_send = text_send + re.sub("'", "", re.findall(tags_i + "=.*?'", str1)[0]) + "\n"
            #    except:
            #        pass
                    # try:
                        # alert_bot.send_text("lmt " + re.findall("hostname=.*? ", str1)[0], is_at_all=False)
            #        text_send = text_send + re.sub("'", "", re.findall(tags_i + "=.*?'", str1)[0]) + "\n"
            #    except:
            #        pass
            # try:
            # text_send = text_send + re.findall("instance=.*? ", str1)[0] + "\n"
            # alert_bot.send_text("lmt " + re.findall("instance=.*? ", str1)[0], is_at_all=False)
            # except:
            # pass
            alert_bot.send_text("lmt特有内容： " + "\n" + text_send, is_at_all=False)
            print("send_dingtalk")

    @classmethod
    def send_sms(cls, payload):
        users = payload.get('event').get("notify_users_obj")
        phones = {}
        for u in users:
            if u.get("phone"):
                phones[u.get("phone")] = 1
        if phones:
            print("send_sms not implemented, phones: {}".format(phones.keys()))

    @classmethod
    def send_voice(cls, payload):
        users = payload.get('event').get("notify_users_obj")
        phones = {}
        for u in users:
            if u.get("phone"):
                phones[u.get("phone")] = 1
        if phones:
            print("send_voice not implemented, phones: {}".format(phones.keys()))

def main():
    payload = json.load(sys.stdin)
    with open(".payload", 'w') as f:
        f.write(json.dumps(payload, indent=4))
    for ch in payload.get('event').get('notify_channels'):
        send_func_name = "send_{}".format(notify_channel_funcs.get(ch.strip()))
        if not hasattr(Sender, send_func_name):
            print("function: {} not found", send_func_name)
            continue
        send_func = getattr(Sender, send_func_name)
        send_func(payload)

def hello():
    print("hello nightingale")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    elif sys.argv[1] == "hello":
        hello()
    else:
        print("I am confused")