# -*- coding:utf-8 -*-
import os, time, requests, re
from PIL import Image
from tkinter import filedialog, Tk
from time import sleep
import xml.etree.ElementTree as ET
from hashlib import md5
from json import loads
from traceback import format_exc
from re import search
import cloudscraper


# 每一部jav的“结构体”
class JavFile(object):
    def __init__(self):
        self.file = 'ABC-123.mp4'  # 文件名
        self.num = 'ABC-123'  # 车牌
        self.search = 'ABC%20123'  # 用于搜索的车牌，javbus处理不了“-”“_”，把这两个换成了“%20”
        self.episodes = 1     # 第几集
        self.subt = ''        # 字幕文件名  ABC-123.srt


# 获取用户选取的文件夹路径，返回路径str
def get_directory():
    directory_root = Tk()
    directory_root.withdraw()
    work_path = filedialog.askdirectory()
    if work_path == '':
        print('你没有选择目录! 请重新选：')
        sleep(2)
        return get_directory()
    else:
        # askdirectory 获得是 正斜杠 路径C:/，所以下面要把 / 换成 反斜杠\
        return work_path.replace('/', os.sep)


# 记录错误txt，无返回。记录在jav搜索后的错误。  这两个函数的区别是，“>>”和“>”，就为了能在显示报错时“整整齐齐”。
def record_fail(fail_msg):
    print(fail_msg, end='')
    txt_fai = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    txt_fai.write(fail_msg)
    txt_fai.close()


# 判断是否有除了“.actors”"extrafanrt”的其他文件夹，存在返回True
def exist_other_folders(lst_folders):
    for folder in lst_folders:
        if folder != '.actors' and folder != 'extrafanart':
            return True
    return False


# 调用百度翻译API接口，返回中文简介str
def tran(api_id, key, word, to_lang, retry):
    if retry == 10:
        print('    >翻译简介失败...请截图联系作者...')
        return '【百度翻译出错】' + word
    # 把账户、翻译的内容、时间 混合md5加密，传给百度验证
    salt = str(time.time())[:10]
    final_sign = api_id + word + salt + key
    final_sign = md5(final_sign.encode("utf-8")).hexdigest()
    # 表单paramas
    paramas = {
        'q': word,
        'from': 'jp',
        'to': to_lang,
        'appid': '%s' % api_id,
        'salt': '%s' % salt,
        'sign': '%s' % final_sign
    }
    try:
        response = requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate', params=paramas, timeout=(6, 7))
    except requests.exceptions.ConnectTimeout:
        print('    >百度翻译又拉闸了...重新翻译...')
        return tran(api_id, key, word, to_lang, retry)
    content = str(response.content, encoding="utf-8")
    # 百度返回为空
    if not content:
        retry += 1
        print('    >百度翻译返回为空...重新翻译...')
        sleep(1)
        return tran(api_id, key, word, to_lang, retry)
    # 百度返回了dict json
    json_reads = loads(content)
    if 'error_code' in json_reads:    # 返回错误码
        error_code = json_reads['error_code']
        if error_code == '54003':
            print('    >请求百度翻译太快...技能冷却1秒...')
            sleep(1)
        elif error_code == '54005':
            print('    >发送了太多超长的简介给百度翻译...技能冷却3秒...')
            sleep(3)
        elif error_code == '52001':
            print('    >连接百度翻译超时...重新翻译...')
        elif error_code == '52002':
            print('    >百度翻译拉闸了...重新翻译...')
        elif error_code == '52003':
            print('    >请正确输入百度翻译API账号，请阅读【使用说明】！')
            print('>>javsdt已停止工作。。。')
            os.system('pause')
        elif error_code == '58003':
            print('    >你的百度翻译API账户被百度封禁了，请联系作者，告诉你解封办法！“')
            print('>>javsdt已停止工作。。。')
            os.system('pause')
        elif error_code == '90107':
            print('    >你的百度翻译API账户还未通过认证或者失效，请前往API控制台解决问题！“')
            print('>>javsdt已停止工作。。。')
            os.system('pause')
        else:
            print('    >百度翻译error_code！请截图联系作者！', error_code)
        retry += 1
        return tran(api_id, key, word, to_lang, retry)
    else:  # 返回正确信息
        return json_reads['trans_result'][0]['dst']


# 获取一个arzon_cookie，返回cookie
def get_acook(prox, retry):
    if retry == 10:
        print('>>请检查你的网络环境是否可以打开：https://www.arzon.jp/')
        os.system('pause')
    try:
        if prox:
            session = requests.Session()
            session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', proxies=prox, timeout=(6, 7))
            return session.cookies.get_dict()
        else:
            session = requests.Session()
            session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', timeout=(6, 7))
            return session.cookies.get_dict()
    except:
        print('通过arzon的成人验证失败，正在重新尝试...')
        return get_acook(prox, retry)


# 获取网页源码，返回网页html
def get_library_html(list_url):   # 0尝试次数  1报错信息   2url  3 proxy
    scraper = cloudscraper.create_scraper(browser="chrome", delay=10)
    while list_url[0] != 10:
        try:
            if len(list_url) == 3:
                rqs = scraper.get(list_url[2])
            else:
                rqs = scraper.get(list_url[2], proxies=list_url[3])
            rqs.encoding = 'utf-8'
            return rqs.text
        except:
            list_url[0] += 1
            continue
    if list_url[0] == 10:
        print('>>请检查你的网络环境是否可以打开：', list_url[2])
        os.system('pause')


def get_bus_html(list_url):    # 0尝试次数  1报错信息  2url  3 proxy
    if list_url[0] == 10:
        print('>>请检查你的网络环境是否可以打开：', list_url[2])
        os.system('pause')
    try:
        if len(list_url) == 3:
            rqs = requests.get(list_url[2], timeout=(6, 7), headers={'Cookie': 'existmag=all'})
        else:   # cookie 为了 获得所有影片，而不是默认的有磁力的链接
            rqs = requests.get(list_url[2], proxies=list_url[3], timeout=(6, 7), headers={'Cookie': 'existmag=all'})
    except:
        list_url[0] += 1
        print(list_url[1], list_url[2])
        return get_bus_html(list_url)
    rqs.encoding = 'utf-8'
    rqs_content = rqs.text
    if search(r'JavBus', rqs_content):
        return rqs_content
    else:
        list_url[0] += 1
        print(list_url[1], '空返回...', list_url[2])
        return get_bus_html(list_url)


def search_db_html(list_url):   # 0尝试次数  1报错信息  2url  3proxy
    # print(list_url)
    if list_url[0] == 11:
        print('>>请检查你的网络环境是否可以打开：', list_url[2])
        os.system('pause')
    if list_url[0] % 3 == 0:
        print(list_url[1], '休息300秒...', list_url[2])
        list_url[0] += 1
        sleep(300)
        return search_db_html(list_url)
    try:
        if len(list_url) == 3:
            rqs = requests.get(list_url[2], timeout=(6, 7))
        else:
            rqs = requests.get(list_url[2], proxies=list_url[3], timeout=(6, 7))
    except:
        # print(format_exc())
        list_url[0] += 1
        print(list_url[1], list_url[2])
        return search_db_html(list_url)
    rqs.encoding = 'utf-8'
    rqs_content = rqs.text
    if search(r'搜索結果', rqs_content):
        return rqs_content
    else:
        # print('！！！！！！！！！失败！')
        # sleep(300)
        list_url[0] += 1
        print(list_url[1], '空返回...', list_url[2])
        return search_db_html(list_url)


def get_db_html(list_url):   # 0尝试次数  1报错信息  2url  3proxy
    # print(list_url)
    if list_url[0] == 10:
        print('>>请检查你的网络环境是否可以打开：', list_url[2])
        os.system('pause')
    if list_url[0] % 3 == 0:
        print(list_url[1], '休息20秒...', list_url[2])
        list_url[0] += 1
        sleep(20)
        return get_db_html(list_url)
    try:
        if len(list_url) == 3:
            rqs = requests.get(list_url[2], timeout=(6, 7))
        else:
            rqs = requests.get(list_url[2], proxies=list_url[3], timeout=(6, 7))
    except:
        # print(format_exc())
        list_url[0] += 1
        print(list_url[1], list_url[2])
        return get_db_html(list_url)
    rqs.encoding = 'utf-8'
    rqs_content = rqs.text
    if search(r'JavDB', rqs_content):
        return rqs_content
    else:
        list_url[0] += 1
        print(list_url[1], '空返回...', list_url[2])
        return get_db_html(list_url)


def get_arzon_html(list_url):   # 0 尝试次数  1报错信息  2url  3 cookies  4 proxy
    if list_url[0] == 10:
        print('>>请检查你的网络环境是否可以打开：', list_url[2])
        os.system('pause')
    try:
        if len(list_url) == 4:
            rqs = requests.get(list_url[2], cookies=list_url[3], timeout=(6, 7))
        else:
            rqs = requests.get(list_url[2], cookies=list_url[3], proxies=list_url[4], timeout=(6, 7))
    except:
        list_url[0] += 1
        print(list_url[1], list_url[2])
        return get_arzon_html(list_url)
    rqs.encoding = 'utf-8'
    rqs_content = rqs.text
    if search(r'arzon', rqs_content):
        return rqs_content
    else:
        list_url[0] += 1
        print(list_url[1], '空返回...', list_url[2])
        return get_arzon_html(list_url)


def get_321_html(list_url):   # 0尝试次数  1报错信息   2url  3 proxy
    if list_url[0] == 10:
        print('>>请检查你的网络环境是否可以打开：', list_url[2])
        os.system('pause')
    try:
        if len(list_url) == 3:
            rqs = requests.get(list_url[2], timeout=(6, 7))
        else:
            rqs = requests.get(list_url[2], proxies=list_url[3], timeout=(6, 7))
    except:
        list_url[0] += 1
        print(list_url[1], list_url[2])
        return get_321_html(list_url)
    rqs.encoding = 'utf-8'
    rqs_content = rqs.text
    if search(r'JAV321', rqs_content):
        return rqs_content
    else:
        list_url[0] += 1
        print(list_url[1], '空返回...', list_url[2])
        return get_321_html(list_url)


def post_321_html(list_url):   # 0尝试次数  1报错信息   2url  3data  4proxy
    if list_url[0] == 10:
        print('>>请检查你的网络环境是否可以打开：', list_url[2])
        os.system('pause')
    try:
        if len(list_url) == 4:
            rqs = requests.post(list_url[2], data=list_url[3], timeout=(6, 7))
        else:
            rqs = requests.post(list_url[2], data=list_url[3], proxies=list_url[4], timeout=(6, 7))
    except:
        # print(format_exc())
        list_url[0] += 1
        print(list_url[1], list_url[2])
        return post_321_html(list_url)
    rqs.encoding = 'utf-8'
    rqs_content = rqs.text
    if search(r'JAV321', rqs_content):
        return rqs_content
    else:
        list_url[0] += 1
        print(list_url[1], '空返回...', list_url[2])
        return post_321_html(list_url)


# 下载图片，无返回
def download_pic(list_cov):
    # print(list_cov)
    # 0错误次数  1图片url  2图片路径  3proxies
    if list_cov[0] < 5:
        try:
            if len(list_cov) == 3:
                r = requests.get(list_cov[1], stream=True, timeout=(6, 10))
                with open(list_cov[2], 'wb') as pic:
                    for chunk in r:
                        pic.write(chunk)
            else:
                r = requests.get(list_cov[1], proxies=list_cov[3], stream=True, timeout=(6, 10))
                with open(list_cov[2], 'wb') as pic:
                    for chunk in r:
                        pic.write(chunk)
        except:
            # print(format_exc())
            print('    >下载失败，重新下载...')
            list_cov[0] += 1
            download_pic(list_cov)
        # 下载的图片打不开，重新下载
        try:
            Image.open(list_cov[2])
        except OSError:
            print('    >下载失败，重新下载....')
            list_cov[0] += 1
            download_pic(list_cov)
    else:
        raise Exception('    >下载多次，仍然失败！')


# 人体识别，返回鼻子位置
def image_cut(file_name, cli):
    with open(file_name, 'rb') as fp:
        image = fp.read()
    try:
        result = cli.bodyAnalysis(image)
        return int(result["person_info"][0]['body_parts']['nose']['x'])
    except:
        print('    >人体分析出现错误，请对照“人体分析错误表格”：', result)
        print('    >正在尝试重新人体检测...')
        return image_cut(file_name, cli)


##################################################################################################################
# 判断文件夹是否含有“中字、㊥”，返回布尔值
def if_word_file(lst, file):
    subs = False
    for word in lst:
        if word in file:  # 原文件名包含“-c、-C、中字”这些字符
            subs = True
            break
    return subs


# 判断nfo中的title和genre也没有“中文字幕”
def if_word_nfo(lst, path):
    try:
        tree = ET.parse(path)
    except ET.ParseError:  # nfo可能损坏
        return False
    for child in tree.getroot():
        if child.tag == 'title':
            for word in lst:
                if word in child.text:
                    # print('有中文')
                    return True
        if child.text == '中文字幕':
            # print('有中文!!!')
            return True
    return False


# 为nfo加上“中文字幕特征
def append_subt(path, cus_subt, cus_title):
    # 读取原nfo
    file_old = open(path, 'r', encoding="utf-8")
    list_lines = [i for i in file_old]
    file_old.close()
    # 原nfo还没有“中字”特征
    if '  <genre>中文字幕</genre>\n' not in list_lines:
        if cus_title.startswith('车牌+空格+是否中字+标题'):
            for i in range(len(list_lines)):
                if list_lines[i].startswith('  <title>'):
                    title = search(r'>(.+?)<', list_lines[i]).group(1)
                    title = title.replace(' ', ' ' + cus_subt, 1)
                    list_lines[i] = '  <title>' + title + '</title>\n'
                    break
        # print(list_lines)
        list_lines.insert(list_lines.index('  <actor>\n'), '  <genre>中文字幕</genre>\n  <tag>中文字幕</tag>\n')
        # 再覆盖写入
        file_new = open(path, 'w', encoding="utf-8")
        file_new.write(''.join(list_lines))
        file_new.close()
        print('重写nfo：', path)
