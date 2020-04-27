# -*- coding:utf-8 -*-
from os import system
from re import search, findall
from time import sleep
from requests import Session, get, post
from PIL import Image
from cloudscraper import get_cookie_string
# from traceback import format_exc

# 功能：请求各大jav网站和arzon的网页
# 参数：网址url，请求头部header/cookies，代理proxy
# 返回：网页html，请求头部


#################################################### arzon ########################################################
# 获取一个arzon_cookie，返回cookie
def steal_arzon_cookies(proxy):
    print('\n正在尝试通过 https://www.arzon.jp 的成人验证...')
    for retry in range(10):
        try:    # 当初费尽心机，想办法如何通过页面上的成人验证，结果在一个C#开发的jav爬虫项目，看到它请求以下网址，再跳转到arzon主页，所得到的的cookie即是合法的cookie
            if proxy:
                session = Session()
                session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', proxies=proxy, timeout=(6, 7))
                print('通过arzon的成人验证！\n')
                return session.cookies.get_dict()
            else:
                session = Session()
                session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', timeout=(6, 7))
                print('通过arzon的成人验证！\n')
                return session.cookies.get_dict()
        except:
            # print(format_exc())
            print('通过失败，重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：https://www.arzon.jp/')
    system('pause')


# 搜索arzon，或请求arzon上jav所在网页，返回html
def get_arzon_html(url, cookies, proxy):
    # print('代理：', proxy)
    for retry in range(10):
        try:
            if proxy:
                rqs = get(url, cookies=cookies, proxies=proxy, timeout=(6, 7))
            else:
                rqs = get(url, cookies=cookies, timeout=(6, 7))
        except:
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'arzon', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    system('pause')


def find_plot_arzon(jav_num, acook, proxy_arzon):
    for retry in range(2):
        url_search_arzon = 'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q=' + jav_num.replace('-', '')
        print('    >查找简介：', url_search_arzon)
        # 得到arzon的搜索结果页面
        html_search_arzon = get_arzon_html(url_search_arzon, acook, proxy_arzon)
        # <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落 ～村民"><img src=
        list_search_results = findall(r'h2><a href="(/item.+?)" title=', html_search_arzon)  # 所有搜索结果链接
        # 搜索结果为N个AV的界面
        if list_search_results:  # arzon有搜索结果
            for url_each_result in list_search_results:
                url_on_arzon = 'https://www.arzon.jp' + url_each_result  # 第i+1个链接
                print('    >获取简介：', url_on_arzon)
                # 打开arzon上每一个搜索结果的页面
                html_arzon = get_arzon_html(url_on_arzon, acook, proxy_arzon)
                # 在该url_on_arzon网页上查找简介
                plotg = search(r'h2>作品紹介</h2>([\s\S]*?)</div>', html_arzon)
                # 成功找到plot
                if str(plotg) != 'None':
                    plot_br = plotg.group(1)
                    plot = ''
                    for line in plot_br.split('<br />'):
                        line = line.strip()
                        plot += line
                    return plot, 0, acook
            # 几个搜索结果查找完了，也没有找到简介
            return '【arzon有该影片，但找不到简介】', 1, acook
        # 没有搜索结果
        else:
            # arzon返回的页面实际是18岁验证
            adultg = search(r'１８歳未満', html_search_arzon)
            if str(adultg) != 'None':
                acook = steal_arzon_cookies(proxy_arzon)
                continue
            # 不是成人验证，也没有简介
            else:
                return '【影片下架，暂无简介】', 2, acook
    print('>>请检查你的网络环境是否可以通过成人验证：https://www.arzon.jp/')
    system('pause')
    return '', 3, acook


#################################################### javlibrary ########################################################
# 获取一个library_cookie，返回cookie
def steal_library_header(url, proxy):
    print('\n正在尝试通过', url, '的5秒检测...如果超过20秒卡住...重启程序...')
    for retry in range(10):
        try:
            if proxy:
                cookie_value, user_agent = get_cookie_string(url, proxies=proxy, timeout=15)
            else:
                cookie_value, user_agent = get_cookie_string(url, timeout=15)
            print('通过5秒检测！\n')
            return {'User-Agent': user_agent, 'Cookie': cookie_value}
        except:
            # print(format_exc())
            print('通过失败，重新尝试...')
            continue
    print('>>通过javlibrary的5秒检测失败：', url)
    system('pause')


# 搜索javlibrary，或请求javlibrary上jav所在网页，返回html
def get_library_html(url, header, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = get(url, headers=header, proxies=proxy, timeout=(6, 7), allow_redirects=False)
            else:
                rqs = get(url, headers=header, timeout=(6, 7), allow_redirects=False)
        except:
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        # print(rqs_content)
        if search(r'JAVLibrary', rqs_content):        # 得到想要的网页，直接返回
            return rqs_content, header
        elif search(r'javli', rqs_content):           # 搜索车牌后，javlibrary跳转前的网页
            url = url[:23] + search(r'(\?v=javli.+?)"', rqs_content).group(1)    # rqs_content是一个非常简短的跳转网页，内容是目标jav所在网址
            if len(url) > 70:                          # 跳转车牌特别长，cf已失效
                header = steal_library_header(url[:23], proxy)  # 更新header后继续请求
                continue
            print('    >获取信息：', url)
            continue                                  # 更新url后继续get
        elif search(r'Compatible', rqs_content):     # cf检测
            header = steal_library_header(url[:23], proxy)    # 更新header后继续请求
            continue
        else:                                         # 代理工具返回的错误信息
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    system('pause')


#################################################### javbus ########################################################
# 搜索javbus，或请求javbus上jav所在网页，返回html
def get_bus_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:       # existmag=all为了 获得所有影片，而不是默认的有磁力的链接
                rqs = get(url, proxies=proxy, timeout=(6, 7), headers={'Cookie': 'existmag=all'})
            else:
                rqs = get(url, timeout=(6, 7), headers={'Cookie': 'existmag=all'})
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JavBus', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    system('pause')


# 去javbus搜寻系列
def find_series_cover_bus(jav_num, url_bus, proxy_bus):
    # 需要这两个东西
    series = url_cover_bus = ''
    status_series = 0
    # 在javbus上找图片url
    url_on_bus = url_bus + jav_num
    print('    >获取系列：', url_on_bus)
    # 获得影片在javbus上的网页
    html_bus = get_bus_html(url_on_bus, proxy_bus)
    if not search(r'404 Page', html_bus):
        # DVD封面cover
        coverg = search(r'bigImage" href="(.+?)">', html_bus)
        if str(coverg) != 'None':
            url_cover_bus = coverg.group(1)
        # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
        seriesg = search(r'系列:</span> <a href=".+?">(.+?)</a>', html_bus)
        if str(seriesg) != 'None':
            series = seriesg.group(1)
    else:
        # 还是老老实实去搜索
        url_search_bus = url_bus + 'search/' + jav_num.replace('-', '') + '&type=1&parent=ce'
        print('    >搜索javbus：', url_search_bus)
        html_bus = get_bus_html(url_search_bus, proxy_bus)
        # 搜索结果的网页，大部分情况一个结果，也有可能是多个结果的网页
        # 尝试找movie-box
        list_search_results = findall(r'movie-box" href="(.+?)">', html_bus)  # 匹配处理“标题”
        if list_search_results:
            jav_pref = jav_num.split('-')[0]  # 匹配车牌的前缀字母
            jav_suf = jav_num.split('-')[-1].lstrip('0')  # 当前车牌的后缀数字 去除多余的0
            list_fit_results = []  # 存放，车牌符合的结果
            for i in list_search_results:
                url_end = i.split('/')[-1].upper()
                url_suf = search(r'[-_](\d+)', url_end).group(1).lstrip('0')  # 匹配box上影片url，车牌的后缀数字，去除多余的0
                if jav_suf == url_suf:  # 数字相同
                    url_pref = search(r'([A-Z]+2?8?)', url_end).group(1).upper()  # 匹配处理url所带车牌前面的字母“n”
                    if jav_pref == url_pref:  # 数字相同的基础下，字母也相同，即可能车牌相同
                        list_fit_results.append(i)
            # 有结果
            if list_fit_results:
                # 有多个结果，发个状态码，警告一下用户
                if len(list_fit_results) > 1:
                    status_series = 1
                # 默认用第一个搜索结果
                url_first_result = list_fit_results[0]
                print('    >获取系列：', url_first_result)
                html_bus = get_bus_html(url_first_result, proxy_bus)
                # DVD封面cover
                coverg = search(r'bigImage" href="(.+?)">', html_bus)
                if str(coverg) != 'None':
                    url_cover_bus = coverg.group(1)
                # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
                seriesg = search(r'系列:</span> <a href=".+?">(.+?)</a>', html_bus)
                if str(seriesg) != 'None':
                    series = seriesg.group(1)
    return url_cover_bus, series, status_series


#################################################### jav321 ########################################################
# 用户指定jav321的网址后，请求jav所在网页，返回html
def get_321_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = get(url, timeout=(6, 7))
        except:
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JAV321', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    system('pause')


# 向jav321 post车牌，得到jav所在网页，也可能是无结果的网页，返回html
def post_321_html(url, data, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = post(url, data=data, proxies=proxy, timeout=(6, 7))
            else:
                rqs = post(url, data=data, timeout=(6, 7))
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JAV321', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    system('pause')


#################################################### javdb ########################################################
# 搜索javdb，得到搜索结果网页，返回html。
def get_search_db_html(url, proxy):
    for retry in range(1, 11):
        if retry % 4 == 0:
            print('    >睡眠5分钟...')
            sleep(300)
        try:
            if proxy:
                rqs = get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = get(url, timeout=(6, 7))
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JavDB', rqs_content):
            if search(r'搜索結果', rqs_content):
                return rqs_content
            else:
                print('    >睡眠5分钟...')
                sleep(300)
                continue
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    system('pause')


# 请求jav在javdb上的网页，返回html
def get_db_html(url, proxy):
    for retry in range(1, 11):
        if retry % 4 == 0:
            print('    >睡眠5分钟...')
            sleep(300)
        try:
            if proxy:
                rqs = get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = get(url, timeout=(6, 7))
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JavDB', rqs_content):
            if search(r'content="JavDB', rqs_content):
                return rqs_content
            else:
                print('    >睡眠5分钟...')
                sleep(300)
                continue
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    system('pause')


#################################################### 下载图片 ########################################################
# 下载图片，无返回
def download_pic(url, path, proxy):
    for retry in range(5):
        try:
            if proxy:
                r = get(url, proxies=proxy, stream=True, timeout=(6, 10))
                with open(path, 'wb') as pic:
                    for chunk in r:
                        pic.write(chunk)
            else:
                r = get(url, stream=True, timeout=(6, 10))
                with open(path, 'wb') as pic:
                    for chunk in r:
                        pic.write(chunk)
        except:
            # print(format_exc())
            print('    >下载失败，重新下载...')
            continue
        # 如果下载的图片打不开，则重新下载
        try:
            img = Image.open(path)
            img.load()
            return
        except OSError:
            print('    >下载失败，重新下载....')
            continue
    raise Exception('    >下载多次，仍然失败！')

