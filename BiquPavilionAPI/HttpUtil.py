import requests
import functools
from instance import *
from random import choice


def MaxRetry(func, max_retry=5):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for retry in range(max_retry):
            response = func(*args, **kwargs)
            if not isinstance(response, bool):
                return response
            else:
                print("尝试第:{}次".format(retry + 1))
                time.sleep(retry * 0.5)

    return wrapper


def headers():
    return {
        "Host": "infosxs.pigqq.com",
        "Connection": "Keep-Alive",
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip",
        'User-Agent': choice(Msg.msg_user_agent)
    }


def get(api_url: str, params=None, max_retry=4, **kwargs):
    for retry in range(max_retry):
        try:
            response = requests.get(api_url, headers=headers(), params=params, **kwargs)
            response.encoding = 'utf-8-sig'
            if response.status_code == 200:
                return response
            print("error status_code:{}\n".format(response.status_code))
        except requests.exceptions.RequestException as error:
            if retry >= 2:
                print("\nGet url:{} Error:{}".format(api_url, error))


@MaxRetry
def post(api_url: str, data=None, **kwargs):
    try:
        response = requests.post(api_url, headers=headers(), params=data, **kwargs)
        if response.status_code == 200:
            return response
        else:
            return False
    except requests.exceptions.RequestException as error:
        print("\nGet url:{} Error:{}".format(api_url, error))
        return False


@MaxRetry
def put(api_url: str, data=None, **kwargs):
    try:
        response = requests.put(api_url, headers=headers(), params=data, **kwargs)
        if response.status_code == 200:
            return response
        else:
            return False
    except requests.exceptions.RequestException as error:
        print("\nGet url:{} Error:{}".format(api_url, error))
        return False
