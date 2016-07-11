from sms.app_settings import *
import requests
import re


def send_message(number_list=[], message=""):
    try:
        if len(number_list) == 0:
            raise Exception("No number for sending message")

        number = ','.join(number_list)

        send = URL
        send += "&send_to="+number+"&msg="+message

        resp = requests.get(send)
        if not resp.status_code == 200:
            raise Exception("Error in sending message from sms")

    except Exception, e:
        print e.message


def send_promo_message(loginid, password, number_list=[], message=""):
    try:
        if len(number_list) == 0:
            raise Exception("No number for sending message")

        number = ','.join(number_list)

        send = PROMO_URL
        send += "&send_to="+number+"&msg="+message+"&loginid="+loginid+"&password="+password

        resp = requests.get(send)
        if not resp.status_code == 200:
            raise Exception("Error in sending message from sms")

    except Exception, e:
        print e.message


def check_balance(loginid, password):
    try:
        post_data = {
            'loginid': loginid,
            'password': password
        }
        response = requests.post(PROMO_BAL_URL, data=post_data)
        content = response.content

        return int(re.search(r'\d+', content).group())

    except Exception, e:
        print e.message


def send_message_trans(username, password, number_list=[], message=""):
    try:
        if len(number_list) == 0:
            raise Exception("No number for sending message")

        number = ','.join(number_list)

        send = get_trans_url(username, password)
        send += "&send_to="+number+"&msg="+message

        resp = requests.get(send)
        if not resp.status_code == 200:
            raise Exception("Error in sending message from sms")

    except Exception, e:
        print e.message


def get_trans_url(username, password):
    url = "http://"+username+"#"+username+"&auth_scheme=plain&password="+password+"&v=1.1&format=text"

    return url

