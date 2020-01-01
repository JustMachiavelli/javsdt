import requests, configparser, base64, os, urllib.parse, re, traceback

if not os.path.exists('女优头像'):
    print('“女优头像”文件夹丢失！请把它放进exe的文件夹中！\n')
    os.system('pause')

# 读取配置文件，这个ini文件用来给用户设置重命名的格式和jav网址
config_settings = configparser.RawConfigParser()
print('正在读取ini中的设置...', end='')
try:
    config_settings.read('ini的设置会影响所有exe的操作结果.ini', encoding='utf-8-sig')
    emby_url = config_settings.get("emby专用", "网址")
    api_key = config_settings.get("emby专用", "api id")
except:
    print(traceback.format_exc())
    print('\n无法读取ini文件，请修改它为正确格式，或者打开“【ini】重新创建ini.exe”创建全新的ini！')
    os.system('pause')
print('\n读取ini文件成功!\n')

if not emby_url.endswith('/'):
    emby_url += '/'
pics = os.listdir('女优头像')
try:
    suc_num = 0
    num = 0
    for file in pics:
        if file.endswith('jpg') or file.endswith('png'):
            num += 1
            if num%500 == 0:
                print('已扫描', num, '个头像')
            actor = file.split('.')[0]
            actor_urlde = urllib.parse.quote(actor)
            # ${embyServerURL}/emby/Persons/${personName}?api_key=${apiKey}
            get_url = emby_url + 'emby/Persons/' + actor_urlde + '?api_key=' + api_key
            check_res = requests.get(url=get_url)
            # print(get_url)
            actor_msg = check_res.text
            # print(actor_msg)
            if actor_msg.startswith('{"Name'):  # Object
                actor_id = re.search(r'"Id":"(\w+)"', actor_msg).group(1)  # 匹配处理“标题”
                print('>>女优：', actor, 'ID：', actor_id)
            elif actor_msg.startswith('Access'):
                print(actor_msg)
                print('请检查API ID填写是否正确！')
                break
            else:
                continue
            actor_path = '女优头像\\' + file
            f = open(actor_path, 'rb')            # 二进制方式打开图文件
            b6_pic = base64.b64encode(f.read())   # 读取文件内容，转换为base64编码
            f.close()
            url = emby_url + 'emby/Items/' + actor_id + '/Images/Primary?api_key=' + api_key
            if file.endswith('jpg'):
                header = {"Content-Type": 'image/png', }
            else:
                header = {"Content-Type": 'image/jpeg', }
            # print(url)
            # os.system('pause')
            respones = requests.post(url=url, data=b6_pic, headers=header)
            suc_path = '女优头像\\设置成功\\' + file
            suc_num += 1
            try:
                os.rename(actor_path, suc_path)
            except:
                print('    >已经存在：', suc_path)
except requests.exceptions.ConnectionError:
    print('emby服务端无法访问，请检查：', emby_url, '\n')
    os.system('pause')
except:
    print(traceback.format_exc())
    print('发生未知错误，请截图给作者：', emby_url, '\n')
    os.system('pause')

print('\n成功处理', suc_num, '个女优头像！\n')
os.system('pause')

