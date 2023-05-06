import requests
import os
import time
import smtplib
import ssl
from email.message import EmailMessage


history_dict = {}

FROM_ADDRESS = os.environ.get('FROM')
FROM_PWD = os.environ.get('FROMPWD')
TO_ADDRESS = os.environ.get('TO')
TRACKING_NUM = os.environ.get('NUM')


url = 'https://www.ecmsglobal.com/brige/getTarcking?orderNumber=' + TRACKING_NUM

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh',
    'Connection': 'keep-alive',
    'Content-Length': '0',
    'Cookie': '_pk_id.4.8a7d=af3c039c5001347e.1683168786.; sessionId=f320fe50-ebe4-11ed-b8ee-ef7c95f8c714; locale=zh-cn; LANG=zh; country=CN; notice=true; _pk_ref.4.8a7d=%5B%22%22%2C%22%22%2C1683374690%2C%22https%3A%2F%2Fese.ecmsglobal.com%2F%22%5D; _pk_ses.4.8a7d=1',
    'Origin': 'https://www.ecmsglobal.com',
    'Referer': 'https://www.ecmsglobal.com/zh-cn/tracking.html?orderNumber=' + TRACKING_NUM,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'userToken': 'f320fe50-ebe4-11ed-b8ee-ef7c95f8c714'
}


def sendEmail(result_list):
    if len(result_list) == 0:
        return
    content = ''
    for item in result_list:
        content = content + '\n' + item
    # Set up the email message
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = "ECMS快递信息更新了！"
    msg["From"] = FROM_ADDRESS
    msg["To"] = TO_ADDRESS
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(FROM_ADDRESS, FROM_PWD)
        server.send_message(msg)


def check():
    result_list = []
    print('start to make a request')
    response = requests.post(url, headers=headers).json()
    infoList = response['orderInfo'][0]['infoList']
    try:
        if len(history_dict) == 0:
            for info in infoList:
                history_dict[info['id']] = info['customDescription']
        else:
            for info in infoList:
                if info['id'] not in history_dict:
                    result_list.append(info['customDescription'])
                    history_dict[info['id']] = info['customDescription']
            if len(result_list) > 0:
                sendEmail(result_list)
    except:
        result_list.append(
            'there is something wrong with the ECMS check process')
        sendEmail(result_list)


if __name__ == '__main__':
    while True:
        #history_dict[1856948432] = 'Amazon的发货预报已收到，正在等待货物到达我们的始发站仓库'
        check()
        # print(history_dict)
        time.sleep(600)
