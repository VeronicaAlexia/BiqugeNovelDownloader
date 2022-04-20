import re
import time
from config import *


class Vars:
    cfg = Config('Config.json', os.getcwd())
    book_info = None
    epub_info = None


class Msg:
    msg_help = [
        '输入指令\nd | bookid\t\t\t\t\t———输入书籍序号下载单本小说',
        's | search-book\t\t\t\t\t———下载单本小说',
        'h | help\t\t\t\t\t———获取使用程序帮助',
        'q | quit\t\t\t\t\t———退出运行的程序',
        'p | thread-max\t\t\t\t\t———改变线程数目',
        'u | update\t\t\t\t\t———下载指定文本中的book-id '
    ]
    msg_agree_terms = "是否以仔细阅读且同意LICENSE中叙述免责声明"\
                      "如果同意声明，请输入英文 \"yes\" 或者中文 \"同意\" 后按Enter建，如果不同意请关闭此程式"


def novel_id_url(novel_id: int) -> str:
    return "{}/{}".format(int(int(novel_id) / 1000) + 1, novel_id)


def mkdir(file_path: str):
    if not os.path.exists(file_path):
        os.mkdir(file_path)


def makedirs(file_path: str):
    if not os.path.exists(os.path.join(file_path)):
        os.makedirs(os.path.join(file_path))


def isCN(book_name):
    cn_no = 0
    for ch in book_name:
        if '\u4e00' <= ch <= '\u9fff':
            cn_no += 1
    return 40 - cn_no


def input_str(prompt, default=None):
    while True:
        ret = input(prompt)
        if ret != '':
            return ret
        elif default is not None:
            return default


def del_title(title: str):
    """删去windowns不规范字符"""
    return re.sub(r'[？?。*|“<>:/\\]', '', title.replace("\x06", "").replace("\x05", "").replace("\x07", ""))


def write(path: str, mode: str, info=None):
    if info is not None:
        try:
            with open(path, f'{mode}', encoding='UTF-8', newline='') as file:
                file.writelines(info)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            with open(path, f'{mode}', encoding='gbk', newline='') as file:
                file.writelines(info)
    else:
        try:
            return open(path, f'{mode}', encoding='UTF-8')
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            return open(path, f'{mode}', encoding='gbk')


def setup_config():
    Vars.cfg.load()
    config_change = False
    if type(Vars.cfg.data.get('save_book')) is not str or Vars.cfg.data.get('save_book') == "":
        Vars.cfg.data['save_book'] = 'novel'
        config_change = True
    if type(Vars.cfg.data.get('config_book')) is not str or Vars.cfg.data.get('config_book') == "":
        Vars.cfg.data['config_book'] = 'config'
        config_change = True
    if type(Vars.cfg.data.get('threading_pool_size')) is not int or Vars.cfg.data.get('threading_pool_size') == "":
        Vars.cfg.data['threading_pool_size'] = 12
        config_change = True
    if type(Vars.cfg.data.get('Disclaimers')) is not str or Vars.cfg.data.get('Disclaimers') == "":
        Vars.cfg.data['Disclaimers'] = 'No'
        config_change = True

    if config_change:
        Vars.cfg.save()
        if os.path.exists(Vars.cfg.data.get('save_book')) and os.path.exists(Vars.cfg.data.get('config_book')):
            pass
        else:
            mkdir(Vars.cfg.data.get('save_book'))
            mkdir(Vars.cfg.data.get('config_book'))
