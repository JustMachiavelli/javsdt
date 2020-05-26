# -*- coding:utf-8 -*-
import os, re
from os.path import exists
from re import findall
from re import search
from configparser import RawConfigParser
from shutil import copyfile, move
from traceback import format_exc
########################################################################################################################
from functions_preparation import JavFile, choose_directory, check_classify_root, exist_nfo, exist_extra_folders,\
    record_start, record_fail, record_warn, record_video_old
from functions_process import check_subt_divulge, replace_xml, replace_xml_win
from functions_picture import check_pic, add_watermark_subt
from functions_requests import download_pic
########################################################################################################################
from functions_preparation import check_actors
from functions_process import find_num_bus, collect_sculpture
from functions_translate import tran_plot
from functions_picture import add_watermark_divulge, crop_poster_youma
from functions_requests import steal_arzon_cookies, get_arzon_html, find_plot_arzon, get_bus_html


#  main开始
print('1、避开21:00-1:00，访问javbus和arzon很慢。\n'
      '2、若一直连不上javbus，请在ini中更新防屏蔽网址\n')
# 读取配置文件，这个ini文件用来给用户设置
print('正在读取ini中的设置...', end='')
try:
    config_settings = RawConfigParser()
    config_settings.read('【点我设置整理规则】.ini', encoding='utf-8-sig')
    ####################################################################################################################
    # 是否 收集nfo
    bool_nfo = True if config_settings.get("收集nfo", "是否收集nfo？") == '是' else False
    # 是否 跳过已存在nfo的文件夹，不整理已有nfo的文件夹
    bool_skip = True if config_settings.get("收集nfo", "是否跳过已存在nfo的文件夹？") == '是' else False
    # 自定义 nfo中title的格式
    custom_nfo_title = config_settings.get("收集nfo", "nfo中title的格式")
    # 是否 去除 标题 末尾可能存在的演员姓名
    bool_strip_actors = True if config_settings.get("收集nfo", "是否去除标题末尾可能存在的演员姓名？") == '是' else False
    # 自定义 有些用户想把“发行年份”“影片类型”作为特征
    custom_genres = config_settings.get("收集nfo", "额外将以下元素添加到特征中")
    # 是否 将特征保存到风格中
    bool_genre = True if config_settings.get("收集nfo", "是否将特征保存到genre？") == '是' else False
    # 是否 将 片商 作为特征
    bool_tag = True if config_settings.get("收集nfo", "是否将特征保存到tag？") == '是' else False
    ####################################################################################################################
    # 是否 重命名 视频
    bool_rename_mp4 = True if config_settings.get("重命名影片", "是否重命名影片？") == '是' else False
    # 自定义 重命名 视频
    custom_video = config_settings.get("重命名影片", "重命名影片的格式")
    # 是否 重命名视频所在文件夹，或者为它创建独立文件夹
    bool_rename_folder = True if config_settings.get("修改文件夹", "是否重命名或创建独立文件夹？") == '是' else False
    # 自定义 新的文件夹名
    custom_folder = config_settings.get("修改文件夹", "新文件夹的格式")
    ####################################################################################################################
    # 是否 重命名用户已拥有的字幕
    bool_rename_subt = True if config_settings.get("字幕文件", "是否重命名已有的字幕文件？") == '是' else False
    ####################################################################################################################
    # 是否 归类jav
    bool_classify = True if config_settings.get("归类影片", "是否归类影片？") == '是' else False
    # 是否 针对“文件夹”归类jav，“否”即针对“文件”
    bool_classify_folder = True if config_settings.get("归类影片", "针对文件还是文件夹？") == '文件夹' else False
    # 自定义 路径 归类的jav放到哪
    custom_root = config_settings.get("归类影片", "归类的根目录")
    # 自定义 jav按什么类别标准来归类
    custom_classify_basis = config_settings.get("归类影片", "归类的标准")
    ####################################################################################################################
    # 是否 下载图片
    bool_jpg = True if config_settings.get("下载封面", "是否下载封面海报？") == '是' else False
    # 自定义 命名 大封面fanart
    custom_fanart = config_settings.get("下载封面", "DVD封面的格式")
    # 自定义 命名 小海报poster
    custom_poster = config_settings.get("下载封面", "海报的格式")
    # 是否 如果视频有“中字”，给poster的左上角加上“中文字幕”的斜杠
    bool_watermark_subt = True if config_settings.get("下载封面", "是否为海报加上中文字幕条幅？") == '是' else False
    # 是否 如果视频是“无码流出”，给poster的右上角加上“无码流出”的斜杠
    bool_watermark_divulge = True if config_settings.get("下载封面", "是否为海报加上无码流出条幅？") == '是' else False
    ####################################################################################################################
    # 是否 收集演员头像
    bool_sculpture = True if config_settings.get("kodi专用", "是否收集演员头像？") == '是' else False
    # 是否 对于多cd的影片，kodi只需要一份图片和nfo
    bool_cd_only = True if config_settings.get("kodi专用", "是否对多cd只收集一份图片和nfo？") == '是' else False
    ####################################################################################################################
    # 是否 使用局部代理
    bool_proxy = True if config_settings.get("局部代理", "是否使用局部代理？") == '是' else False
    # 是否 使用http代理，否 就是socks5
    bool_http = True if config_settings.get("局部代理", "http还是socks5？") == 'http' else False
    # 代理端口
    custom_proxy = config_settings.get("局部代理", "代理端口")
    # 是否 代理javbus，还有代理javbus上的图片cdnbus
    bool_bus_proxy = True if config_settings.get("局部代理", "是否代理javbus？") == '是' else False
    # 是否 代理arzon
    bool_arzon_proxy = True if config_settings.get("局部代理", "是否代理arzon？") == '是' else False
    ####################################################################################################################
    # 是否 使用简体中文 简介翻译的结果和jav特征会变成“简体”还是“繁体”
    bool_zh = True if config_settings.get("其他设置", "简繁中文？") == '简' else False
    # 自定义 文件类型 只有列举出的视频文件类型，才会被处理
    custom_file_type = config_settings.get("其他设置", "扫描文件类型")
    # 自定义 命名格式中“标题”的长度 windows只允许255字符，所以限制长度，但nfo中的标题是全部
    int_title_len = int(config_settings.get("其他设置", "重命名中的标题长度（50~150）"))
    ####################################################################################################################
    # 自定义 素人车牌 素人需要去jav321处理，这里javbus直接跳过
    custom_suren_pref = config_settings.get("信息来源", "列出车牌(素人为主，可自行添加)")
    ####################################################################################################################
    # 自定义 原影片性质 影片有中文，体现在视频名称中包含这些字符
    custom_subt_video = config_settings.get("原影片文件的性质", "是否中字即文件名包含")
    # 自定义 是否中字 这个元素的表现形式
    custom_subt_expression = config_settings.get("原影片文件的性质", "是否中字的表现形式")
    # 自定义 原影片性质 影片是无码流出片，体现在视频名称中包含这些字符
    custom_divulge_video = config_settings.get("原影片文件的性质", "是否流出即文件名包含")
    # 自定义 是否流出 这个元素的表现形式
    custom_divulge_expression = config_settings.get("原影片文件的性质", "是否流出的表现形式")
    ######################################## 不同之处 ####################################################
    # 自定义 原影片性质 有码
    custom_movie_type = config_settings.get("原影片文件的性质", "有码")
    # 网址 javbus
    url_web = config_settings.get("其他设置", "javbus网址")
    # 自定义 无视的字母数字 去除影响搜索结果的字母数字 xhd1080、mm616、FHD-1080
    custom_surplus_words = config_settings.get("原影片文件的性质", "无视有码、素人视频文件名中多余的形如abc123的字母数字")
    # 是否 需要简介
    bool_plot = True if config_settings.get("百度翻译API", "是否需要日语简介？") == '是' else False
    # 是否 把日语简介翻译为中文
    bool_tran = True if config_settings.get("百度翻译API", "是否翻译为中文？") == '是' else False
    # 账户 百度翻译api
    tran_id = config_settings.get("百度翻译API", "APP ID")
    tran_sk = config_settings.get("百度翻译API", "密钥")
except:
    print(format_exc())
    print('\n无法读取ini文件，请修改它为正确格式，或者打开“【ini】重新创建ini.exe”创建全新的ini！')
    system('pause')

# 未雨绸缪：如果需要为kodi整理头像，先检查演员头像ini、头像文件夹是否存在
if bool_sculpture:
    check_actors()
print('\n读取ini文件成功!\n')
# 初始化：代理设置，哪些站点需要代理
if bool_proxy and custom_proxy:
    if bool_http:
        proxies = {"http": "http://" + custom_proxy, "https": "https://" + custom_proxy}
    else:
        proxies = {"http": "socks5://" + custom_proxy, "https": "socks5://" + custom_proxy}
    proxy_arzon = proxies if bool_arzon_proxy else {}    # 请求arzon时传递的参数
    proxy_bus = proxies if bool_bus_proxy else {}    # 请求javbus时传递的参数
else:
    proxy_arzon = proxy_bus = {}   # 请求dmm图片时传递的参数
# 初始化：如果需要日语简介，需要先获得arzon的cookie，通过成人验证
acook = steal_arzon_cookies(proxy_arzon) if bool_plot and bool_nfo else {}
# 初始化：jav网址，无论用户输不输人后面的斜杠 https://www.buscdn.work/
if not url_web.endswith('/'):
    url_web += '/'
# 初始化：简/繁中文，影响影片特征和简介
if bool_zh:
    to_language = 'zh'          # 目标语言，百度翻译规定 zh是简体中文，cht是繁体中文
else:
    to_language = 'cht'
# 初始化：“是否重命名或创建独立文件夹”，还会受到“归类影片”影响。
if bool_classify:                            # 如果需要归类
    if bool_classify_folder:                 # 并且是针对文件夹
        bool_rename_folder = True            # 那么必须重命名文件夹或者创建新的文件夹
    else:
        bool_rename_folder = False           # 否则不会操作新文件夹
# 初始化 当前系统的路径分隔符 windows是“\”，linux和mac是“/”
sep = os.sep
# 初始化：存放影片信息，用于给用户自定义各种命名
dict_nfo = {'空格': ' ', '车牌': 'ABC-123', '标题': '有码标题', '完整标题': '完整标题', '导演': '有码导演',
            '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
            '片商': '有码片商', '评分': '0', '首个演员': '有码演员', '全部演员': '有码演员',
            '片长': '0', '\\': sep, '/': sep, '是否中字': '', '视频': 'ABC-123', '车牌前缀': 'ABC',
            '是否流出': '', '影片类型': custom_movie_type, '系列': '有码系列',
            '原文件名': 'ABC-123', '原文件夹名': 'ABC-123', }
# 初始化：将ini读取的各种自定义string，切割为list。如果是dict_nfo没有的、用户自己需要的元素，将它们放进dict_nfo中。
list_extra_genres = custom_genres.split('、') if custom_genres else [] # 需要的额外特征
# 是否需要把系列、片商加到特征中，如果没有明确的系列、片商，也不会加
bool_write_series = True if '系列' in list_extra_genres else False
bool_write_studio = True if '片商' in list_extra_genres else False
list_extra_genres = [i for i in list_extra_genres if i != '系列' and i != '片商']
list_suren_num = custom_suren_pref.split('、')          # 素人番号的列表
list_rename_video = custom_video.split('+')             # 重命名视频的格式
list_rename_folder = custom_folder.split('+')           # 重命名文件夹的格式
tuple_type = tuple(custom_file_type.split('、'))        # 需要扫描的文件的类型
list_name_nfo_title = custom_nfo_title.replace('标题', '完整标题', 1).split('+')  # nfo中title的写法
list_name_fanart = custom_fanart.split('+')            # fanart的格式
list_name_poster = custom_poster.split('+')            # poster的格式
list_subt_video = custom_subt_video.split('、')        # 包含哪些特殊含义的文字，判断是否中字
list_divulge_video = custom_divulge_video.split('、')          # 包含哪些特殊含义的文字，判断是否是无码流出片
list_surplus_words = custom_surplus_words.split('、')  # 视频文件名包含哪些多余的字幕数字，需要无视
# 七个for，如果有什么高效简介的办法，请告诉我
for j in list_extra_genres:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_rename_video:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_rename_folder:
    if j not in dict_nfo:
        dict_nfo[j] = j
list_classify_basis = []
for i in custom_classify_basis.split('\\'):   # 归类标准，归类到哪个文件夹。不管是什么操作系统，用户写归类的规则，用“\”连接
    for j in i.split('+'):
        if j not in dict_nfo:
            dict_nfo[j] = j
        list_classify_basis.append(j)
    list_classify_basis.append(sep)
for j in list_name_nfo_title:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_name_fanart:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_name_poster:
    if j not in dict_nfo:
        dict_nfo[j] = j
# 特征，繁日转简
dict_gen = {'中文字幕': '中文字幕', '无码流出': '无码流出',
            '折磨': '折磨', '嘔吐': '呕吐', '觸手': '触手', '蠻橫嬌羞': '蛮横娇羞', '處男': '处男', '正太控': '正太控',
            '出軌': '出轨', '瘙癢': '瘙痒', '運動': '运动', '女同接吻': '女同接吻', '性感的x': '性感的', '美容院': '美容院',
            '處女': '处女', '爛醉如泥的': '烂醉如泥的', '殘忍畫面': '残忍画面', '妄想': '妄想', '惡作劇': '恶作剧', '學校作品': '学校作品',
            '粗暴': '粗暴', '通姦': '通奸', '姐妹': '姐妹', '雙性人': '双性人', '跳舞': '跳舞', '性奴': '性奴',
            '倒追': '倒追', '性騷擾': '性骚扰', '其他': '其他', '戀腿癖': '恋腿癖', '偷窥': '偷窥', '花癡': '花痴',
            '男同性恋': '男同性恋', '情侶': '情侣', '戀乳癖': '恋乳癖', '亂倫': '乱伦', '其他戀物癖': '其他恋物癖', '偶像藝人': '偶像艺人',
            '野外・露出': '野外・露出', '獵豔': '猎艳', '女同性戀': '女同性恋', '企畫': '企画', '10枚組': '10枚组', '性感的': '性感的',
            '科幻': '科幻', '女優ベスト・総集編': '演员的总编', '温泉': '温泉', 'M男': 'M男', '原作コラボ': '原作协作',
            '16時間以上作品': '16时间以上作品', 'デカチン・巨根': '巨根', 'ファン感謝・訪問': '感恩祭', '動画': '动画', '巨尻': '巨尻', 'ハーレム': '后宫',
            '日焼け': '晒黑', '早漏': '早漏', 'キス・接吻': '接吻.', '汗だく': '汗流浃背', 'スマホ専用縦動画': '智能手机的垂直视频', 'Vシネマ': '电影放映',
            'Don Cipote\'s choice': 'Don Cipote\'s choice', 'アニメ': '日本动漫', 'アクション': '动作', 'イメージビデオ（男性）': '（视频）男性', '孕ませ': '孕育', 'ボーイズラブ': '男孩恋爱',
            'ビッチ': 'bitch', '特典あり（AVベースボール）': '特典（AV棒球）', 'コミック雑誌': '漫画雑志', '時間停止': '时间停止',

            '黑幫成員': '黑帮成员', '童年朋友': '童年朋友', '公主': '公主', '亞洲女演員': '亚洲女演员', '伴侶': '伴侣', '講師': '讲师',
            '婆婆': '婆婆', '格鬥家': '格斗家', '女檢察官': '女检察官', '明星臉': '明星脸', '女主人、女老板': '女主人、女老板', '模特兒': '模特',
            '秘書': '秘书', '美少女': '美少女', '新娘、年輕妻子': '新娘、年轻妻子', '姐姐': '姐姐', '車掌小姐': '车掌小姐',
            '寡婦': '寡妇', '千金小姐': '千金小姐', '白人': '白人', '已婚婦女': '已婚妇女', '女醫生': '女医生', '各種職業': '各种职业',
            '妓女': '妓女', '賽車女郎': '赛车女郎', '女大學生': '女大学生', '展場女孩': '展场女孩', '女教師': '女教师', '母親': '母亲',
            '家教': '家教', '护士': '护士', '蕩婦': '荡妇', '黑人演員': '黑人演员', '女生': '女生', '女主播': '女主播',
            '高中女生': '高中女生', '服務生': '服务生', '魔法少女': '魔法少女', '學生（其他）': '学生（其他）', '動畫人物': '动画人物', '遊戲的真人版': '游戏真人版',
            '超級女英雄': '超级女英雄',

            '角色扮演': '角色扮演', '制服': '制服', '女戰士': '女战士', '及膝襪': '及膝袜', '娃娃': '娃娃', '女忍者': '女忍者',
            '女裝人妖': '女装人妖', '內衣': '內衣', '猥褻穿著': '猥亵穿着', '兔女郎': '兔女郎', '貓耳女': '猫耳女', '女祭司': '女祭司',
            '泡泡襪': '泡泡袜', '緊身衣': '紧身衣', '裸體圍裙': '裸体围裙', '迷你裙警察': '迷你裙警察', '空中小姐': '空中小姐',
            '連褲襪': '连裤袜', '身體意識': '身体意识', 'OL': 'OL', '和服・喪服': '和服・丧服', '體育服': '体育服', '内衣': '内衣',
            '水手服': '水手服', '學校泳裝': '学校泳装', '旗袍': '旗袍', '女傭': '女佣', '迷你裙': '迷你裙', '校服': '校服',
            '泳裝': '泳装', '眼鏡': '眼镜', '哥德蘿莉': '哥德萝莉', '和服・浴衣': '和服・浴衣',

            '超乳': '超乳', '肌肉': '肌肉', '乳房': '乳房', '嬌小的': '娇小的', '屁股': '屁股', '高': '高',
            '變性者': '变性人', '無毛': '无毛', '胖女人': '胖女人', '苗條': '苗条', '孕婦': '孕妇', '成熟的女人': '成熟的女人',
            '蘿莉塔': '萝莉塔', '貧乳・微乳': '贫乳・微乳', '巨乳': '巨乳',


            '顏面騎乘': '颜面骑乘', '食糞': '食粪', '足交': '足交', '母乳': '母乳', '手指插入': '手指插入', '按摩': '按摩',
            '女上位': '女上位', '舔陰': '舔阴', '拳交': '拳交', '深喉': '深喉', '69': '69', '淫語': '淫语',
            '潮吹': '潮吹', '乳交': '乳交', '排便': '排便', '飲尿': '饮尿', '口交': '口交', '濫交': '滥交',
            '放尿': '放尿', '打手槍': '打手枪', '吞精': '吞精', '肛交': '肛交', '顏射': '颜射', '自慰': '自慰',
            '顏射x': '颜射', '中出': '中出', '肛内中出': '肛内中出',

            '立即口交': '立即口交', '女優按摩棒': '演员按摩棒', '子宮頸': '子宫颈', '催眠': '催眠', '乳液': '乳液', '羞恥': '羞耻',
            '凌辱': '凌辱', '拘束': '拘束', '輪姦': '轮奸', '插入異物': '插入异物', '鴨嘴': '鸭嘴', '灌腸': '灌肠',
            '監禁': '监禁', '紧缚': '紧缚', '強姦': '强奸', '藥物': '药物', '汽車性愛': '汽车性爱', 'SM': 'SM',
            '糞便': '粪便', '玩具': '玩具', '跳蛋': '跳蛋', '緊縛': '紧缚', '按摩棒': '按摩棒', '多P': '多P',
            '性愛': '性爱', '假陽具': '假阳具', '逆強姦': '逆强奸',

            '合作作品': '合作作品', '恐怖': '恐怖', '給女性觀眾': '女性向', '教學': '教学', 'DMM專屬': 'DMM专属', 'R-15': 'R-15',
            'R-18': 'R-18', '戲劇': '戏剧', '3D': '3D', '特效': '特效', '故事集': '故事集', '限時降價': '限时降价',
            '複刻版': '复刻版', '戲劇x': '戏剧', '戀愛': '恋爱', '高畫質': 'xxx', '主觀視角': '主观视角', '介紹影片': '介绍影片',
            '4小時以上作品': '4小时以上作品', '薄馬賽克': '薄马赛克', '經典': '经典', '首次亮相': '首次亮相', '數位馬賽克': '数位马赛克', '投稿': '投稿',
            '纪录片': '纪录片', '國外進口': '国外进口', '第一人稱攝影': '第一人称摄影', '業餘': '业余', '局部特寫': '局部特写', '獨立製作': '独立制作',
            'DMM獨家': 'DMM独家', '單體作品': '单体作品', '合集': '合集', '高清': 'xxx', '字幕': 'xxx', '天堂TV': '天堂TV',
            'DVD多士爐': 'DVD多士炉', 'AV OPEN 2014 スーパーヘビー': 'AV OPEN 2014 S级', 'AV OPEN 2014 ヘビー級': 'AV OPEN 2014重量级', 'AV OPEN 2014 ミドル級': 'AV OPEN 2014中量级',
            'AV OPEN 2015 マニア/フェチ部門': 'AV OPEN 2015 狂热者/恋物癖部门', 'AV OPEN 2015 熟女部門': 'AV OPEN 2015 熟女部门',
            'AV OPEN 2015 企画部門': 'AV OPEN 2015 企画部门', 'AV OPEN 2015 乙女部門': 'AV OPEN 2015 少女部',
            'AV OPEN 2015 素人部門': 'AV OPEN 2015 素人部门', 'AV OPEN 2015 SM/ハード部門': 'AV OPEN 2015 SM/硬件',
            'AV OPEN 2015 女優部門': 'AV OPEN 2015 演员部门', 'AVOPEN2016人妻・熟女部門': 'AVOPEN2016人妻・熟女部门',
            'AVOPEN2016企画部門': 'AVOPEN2016企画部', 'AVOPEN2016ハード部門': 'AVOPEN2016ハード部',
            'AVOPEN2016マニア・フェチ部門': 'AVOPEN2016疯狂恋物科', 'AVOPEN2016乙女部門': 'AVOPEN2016少女部',
            'AVOPEN2016女優部門': 'AVOPEN2016演员部', 'AVOPEN2016ドラマ・ドキュメンタリー部門': 'AVOPEN2016电视剧纪录部',
            'AVOPEN2016素人部門': 'AVOPEN2016素人部', 'AVOPEN2016バラエティ部門': 'AVOPEN2016娱乐部',
            'VR専用': 'VR専用', '堵嘴·喜劇': '堵嘴·喜剧', '幻想': '幻想', '性別轉型·女性化': '性别转型·女性化',
            '為智能手機推薦垂直視頻': '为智能手机推荐垂直视频', '設置項目': '设置项目', '迷你係列': '迷你系列',
            '體驗懺悔': '体验忏悔', '黑暗系統': '黑暗系统',

            'オナサポ': '手淫', 'アスリート': '运动员', '覆面・マスク': '蒙面具', 'ハイクオリティVR': '高品质VR', 'ヘルス・ソープ': '保健香皂', 'ホテル': '旅馆',
            'アクメ・オーガズム': '绝顶高潮', '花嫁': '花嫁', 'デート': '约会', '軟体': '软体', '娘・養女': '养女', 'スパンキング': '打屁股',
            'スワッピング・夫婦交換': '夫妇交换', '部下・同僚': '部下・同僚', '旅行': '旅行', '胸チラ': '露胸', 'バック': '后卫', 'エロス': '爱的欲望',
            '男の潮吹き': '男人高潮', '女上司': '女上司', 'セクシー': '性感美女', '受付嬢': '接待小姐', 'ノーブラ': '不穿胸罩',
            '白目・失神': '白眼失神', 'M女': 'M女', '女王様': '女王大人', 'ノーパン': '不穿内裤', 'セレブ': '名流', '病院・クリニック': '医院诊所',
            '面接': '面试', 'お風呂': '浴室', '叔母さん': '叔母阿姨', '罵倒': '骂倒', 'お爺ちゃん': '爷爷', '逆レイプ': '强奸小姨子',
            'ディルド': 'ディルド', 'ヨガ': '瑜伽', '飲み会・合コン': '酒会、联谊会', '部活・マネージャー': '社团经理', 'お婆ちゃん': '外婆', 'ビジネススーツ': '商务套装',
            'チアガール': '啦啦队女孩', 'ママ友': '妈妈的朋友', 'エマニエル': '片商Emanieru熟女塾', '妄想族': '妄想族', '蝋燭': '蜡烛', '鼻フック': '鼻钩儿',
            '放置': '放置', 'サンプル動画': '范例影片', 'サイコ・スリラー': '心理惊悚片', 'ラブコメ': '爱情喜剧', 'オタク': '御宅族',}

# 用户输入“回车”就继续选择文件夹整理
input_start_key = ''
while input_start_key == '':
    # 用户选择需要整理的文件夹
    print('请选择要整理的文件夹：', end='')
    root_choose = choose_directory()
    print(root_choose)
    # 在txt中记录一下用户的这次操作
    record_start(root_choose)
    # 未雨绸缪：用户自定义的归类根目录，是否合法
    if bool_classify:
        root_classify = check_classify_root(custom_root, root_choose)
    # 初始化：失败次数
    num_fail = 0
    num_warn = 0
    print('...文件扫描开始...如果时间过长...请避开中午夜晚高峰期...\n')
    # root【当前根目录】 dirs【子文件夹】 files【文件】，root是str，后两个是list
    for root, dirs, files in os.walk(root_choose):
        if not files:
            continue
        if '归类完成' in root.replace(root_choose, ''):
            # print('>>该文件夹在归类的根目录中，跳过处理...', root)
            continue
        if bool_skip and exist_nfo(files):
            # print(root+'sep+files[-1])      整理要跳过已存在nfo的文件夹，判断这一层文件夹最后两个文件是不是nfo
            continue
        # 对这一层文件夹进行评估,有多少视频，有多少同车牌视频，是不是独立文件夹
        list_jav_videos = []         # 存放：需要整理的jav的结构体
        dict_car_pref = {}           # 存放：这一层文件夹下的几个车牌 abp avop snis。。。{'abp': 1, avop': 2} abp只有一集，avop有cd1、cd2
        num_videos_include = 0       # 当前文件夹中视频的数量，可能有视频不是jav
        dict_subt_files = {}         # 存放：jav的字幕文件 {'c:\a\abc_123.srt': 'abc-123'}
        # 判断文件是不是字幕文件，放入dict_subt_files中
        for file_raw in files:
            file_temp = file_raw.upper()
            if file_temp.endswith(('.SRT', '.VTT', '.ASS', '.SSA', '.SUB', '.SMI',)):
                if 'FC2' in file_temp:
                    continue    # 【跳出2】
                for word in list_surplus_words:
                    file_temp = file_temp.replace(word, '')
                # 字幕中的车牌
                subt_num = find_num_bus(file_temp, list_suren_num)  # 匹配字幕车牌
                if subt_num:
                    dict_subt_files[file_raw] = subt_num
        # print(dict_subt_files)
        # 判断文件是不是视频，放入list_jav_videos中
        for file_raw in files:
            file_temp = file_raw.upper()
            if file_temp.endswith(tuple_type) and not file_temp.startswith('.'):
                num_videos_include += 1
                if 'FC2' in file_temp:
                    continue    # 【跳出2】
                for word in list_surplus_words:
                    file_temp = file_temp.replace(word, '')
                # jav_num 视频中的车牌
                jav_num = find_num_bus(file_temp, list_suren_num)
                if jav_num:
                    try:
                        dict_car_pref[jav_num] += 1  # 已经有这个车牌了，加一集cd
                    except KeyError:
                        dict_car_pref[jav_num] = 1  # 这个新车牌有了第一集
                    # 把这个jav的各种属性打包好
                    jav_struct = JavFile()
                    jav_struct.num = jav_num           # 车牌
                    jav_struct.file = file_raw         # 原文件名
                    jav_struct.episodes = dict_car_pref[jav_num]  # 当前jav，是第几集  {'abp': 1, avop': 2}
                    # 这个车牌在dict_subt_files中，有它的字幕。
                    if jav_num in dict_subt_files.values():
                        jav_struct.subt = list(dict_subt_files.keys())[list(dict_subt_files.values()).index(jav_num)]
                        del dict_subt_files[jav_struct.subt]
                    list_jav_videos.append(jav_struct)
                else:
                    print('>>无法处理：' + root.replace(root_choose, '') + sep + file_raw)
        # 判定影片所在文件夹是否是独立文件夹
        if dict_car_pref:  # 这一层文件夹下有jav
            if len(dict_car_pref) > 1 or num_videos_include > len(list_jav_videos) or exist_extra_folders(dirs):
                # 当前文件夹下，车牌不止一个；还有其他非jav视频；有其他文件夹，除了演员头像文件夹“.actors”和额外剧照文件夹“extrafanart”；
                bool_separate_folder = False   # 不是独立的文件夹
            else:
                bool_separate_folder = True    # 这一层文件夹是这部jav的独立文件夹
        else:
            continue    # 【跳出1】
        # 正式开始
        # print(list_jav_videos)
        for jav in list_jav_videos:
            jav_raw_num = jav.num  # 车牌  abc-123
            jav_file = jav.file    # 完整的原文件名  abc-123.mp4
            jav_epi = jav.episodes  # 这是第几集？一般都只有一集
            num_all_episodes = dict_car_pref[jav_raw_num]  # 该车牌总共多少集
            path_jav = root + sep + jav_file  # jav的起始路径
            path_relative = sep + path_jav.replace(root_choose, '')   # 影片的相对于所选文件夹的路径，用于报错
            print('>>正在处理：', jav_file)
            print('    >发现车牌：', jav_raw_num)
            # 视频本身的一些属性
            video_type = '.' + jav_file.split('.')[-1].lower()  # 文件类型，如：.mp4
            jav_name = jav_file[:-len(video_type)]  # 不带视频类型的文件名
            subt_file = jav.subt  # 与当前影片配对的字幕的文件名 abc-123.srt，如果没有就是''
            # 判断是否有中字
            if subt_file:
                bool_subt = True
                dict_nfo['是否中字'] = custom_subt_expression
                subt_type = '.' + subt_file.split('.')[-1]  # 字幕类型，如：.srt
            else:
                bool_subt = check_subt_divulge(root, jav_name, list_subt_video, '中文字幕')
                dict_nfo['是否中字'] = custom_subt_expression if bool_subt else ''
            # 判断是否是无码流出的作品
            bool_divulge = check_subt_divulge(root, jav_name, list_divulge_video, '无码流出')
            dict_nfo['是否流出'] = custom_divulge_expression if bool_divulge else ''

            try:
                # 搜索获取nfo信息的javbus网页
                if '公交车' not in jav_file:    # 用户没有指定网址，则去搜索
                    url_search_web = url_web + 'search/' + jav_raw_num + '&type=1&parent=ce'
                    print('    >搜索车牌：', url_search_web)
                    # 得到javbus搜索网页html
                    html_web = get_bus_html(url_search_web, proxy_bus)
                    # 尝试找movie-box
                    list_search_results = findall(r'movie-box" href="(.+?)">', html_web)  # 匹配处理“标题”
                    if list_search_results:  # 搜索页面有结果
                        # print(list_search_results)
                        # print('    >正在核查搜索结果...')
                        jav_pref = jav_raw_num.split('-')[0]  # 匹配车牌的前缀字母
                        jav_suf = jav_raw_num.split('-')[-1].lstrip('0')  # 当前车牌的后缀数字 去除多余的0
                        list_fit_results = []    # 存放，车牌符合的结果
                        for i in list_search_results:
                            url_end = i.split('/')[-1].upper()
                            url_suf = search(r'[-_](\d+)', url_end).group(1).lstrip('0')  # 匹配box上影片url，车牌的后缀数字，去除多余的0
                            if jav_suf == url_suf:  # 数字相同
                                url_pref = search(r'([A-Z0-9]+)[-_]', url_end).group(1).upper()  # 匹配处理url所带车牌前面的字母“n”
                                if jav_pref == url_pref:  # 数字相同的基础下，字母也相同，即可能车牌相同
                                    list_fit_results.append(i)
                        # 有码搜索的结果一个都匹配不上
                        if not list_fit_results:
                            num_fail += 1
                            record_fail('    >第' + str(
                                num_fail) + '个失败！javbus有码找不到该车牌的信息：' + jav_raw_num + '，' + path_relative + '\n')
                            continue           # 【跳出对该jav的整理】
                        # 默认用第一个搜索结果
                        url_on_web = list_fit_results[0]
                        if len(list_fit_results) > 1:
                            num_fail += 1
                            record_fail('    >第' + str(
                                num_fail) + '个警告！javbus搜索到同车牌的不同视频：' + jav_raw_num + '，' + path_relative + '\n')
                    # 找不到box
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(
                            num_fail) + '个失败！javbus有码找不到该车牌的信息：' + jav_raw_num + '，' + path_relative + '\n')
                        continue           # 【跳出对该jav的整理】
                # 用户指定javbus上的网页
                else:
                    url_appointg = search(r'公交车(.+?)\.', jav_file)
                    if str(url_appointg) != 'None':
                        url_on_web = url_web + url_appointg.group(1)
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！你指定的javbus网址有错误：' + path_relative + '\n')
                        continue           # 【跳出对该jav的整理】
                # 经过上面的三种情况，可能找到了jav在bus上的网页链接url_on_web
                print('    >获取信息：', url_on_web)
                # 得到最终的jav所在网页
                html_web = get_bus_html(url_on_web, proxy_bus)

                # 开始匹配信息
                # 有大部分信息的html_web
                html_web = search(r'(h3>[\s\S]*?)磁力連結投稿', html_web, re.DOTALL).group(1)
                # 标题
                title = search(r'h3>(.+?)</h3', html_web, re.DOTALL).group(1)  # javbus上的标题可能占两行
                # 去除xml文档和windows路径不允许的特殊字符 &<>  \/:*?"<>|
                title = replace_xml_win(title)
                print('    >影片标题：', title)
                # 正则匹配 影片信息 开始！
                # title的开头是车牌号，想要后面的纯标题
                car_titleg = search(r'(.+?) (.+)', title)
                # 车牌号
                dict_nfo['车牌'] = jav_num = car_titleg.group(1)
                dict_nfo['车牌前缀'] = jav_num.split('-')[0]
                # 给用户重命名用的标题是“短标题”，nfo中是“完整标题”，但用户在ini中只用写“标题”
                title_only = car_titleg.group(2)
                # DVD封面cover
                coverg = search(r'bigImage" href="(.+?)">', html_web)  # 封面图片的正则对象
                if str(coverg) != 'None':
                    url_cover = coverg.group(1)
                else:
                    url_cover = ''
                # 发行日期
                premieredg = search(r'發行日期:</span> (.+?)</p>', html_web)
                if str(premieredg) != 'None':
                    dict_nfo['发行年月日'] = time_premiered = premieredg.group(1)
                    dict_nfo['发行年份'] = time_premiered[0:4]
                    dict_nfo['月'] = time_premiered[5:7]
                    dict_nfo['日'] = time_premiered[8:10]
                else:
                    dict_nfo['发行年月日'] = time_premiered = '1970-01-01'
                    dict_nfo['发行年份'] = '1970'
                    dict_nfo['月'] = '01'
                    dict_nfo['日'] = '01'
                # 片长 <td><span class="text">150</span> 分钟</td>
                runtimeg = search(r'長度:</span> (.+?)分鐘</p>', html_web)
                if str(runtimeg) != 'None':
                    dict_nfo['片长'] = runtimeg.group(1)
                else:
                    dict_nfo['片长'] = '0'
                # 导演
                directorg = search(r'導演:</span> <a href=".+?">(.+?)<', html_web)
                if str(directorg) != 'None':
                    dict_nfo['导演'] = replace_xml_win(directorg.group(1))
                else:
                    dict_nfo['导演'] = '有码导演'
                # 片商 制作商
                studiog = search(r'製作商:</span> <a href=".+?">(.+?)</a>', html_web)
                if str(studiog) != 'None':
                    dict_nfo['片商'] = studio = replace_xml_win(studiog.group(1))
                else:
                    dict_nfo['片商'] = '有码片商'
                    studio = ''
                # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
                seriesg = search(r'系列:</span> <a href=".+?">(.+?)</a>', html_web)  # 封面图片的正则对象
                if str(seriesg) != 'None':
                    dict_nfo['系列'] = series = seriesg.group(1).replace(sep, '#')
                else:
                    dict_nfo['系列'] = '有码系列'
                    series = ''
                # 演员们 和 # 第一个演员
                actors = findall(r'star/.+?"><img src=.+?" title="(.+?)">', html_web)
                if actors:
                    if len(actors) > 7:
                        dict_nfo['全部演员'] = ' '.join(actors[:7])
                    else:
                        dict_nfo['全部演员'] = ' '.join(actors)
                    dict_nfo['首个演员'] = actors[0]
                    # 有些用户需要删去 标题 末尾可能存在的 演员姓名
                    if bool_strip_actors and title_only.endswith(dict_nfo['全部演员']):
                        title_only = title_only[:-len(dict_nfo['全部演员'])].rstrip()
                else:
                    actors = ['有码演员']
                    dict_nfo['首个演员'] = dict_nfo['全部演员'] = '有码演员'
                # 处理影片的标题过长
                dict_nfo['完整标题'] = title_only
                if len(title_only) > int_title_len:
                    dict_nfo['标题'] = title_only[:int_title_len]
                else:
                    dict_nfo['标题'] = title_only
                # 特点
                genres = findall(r'genre"><a href=".+?">(.+?)</a></span>', html_web)
                genres = [i for i in genres if i != '字幕' and i != '高清' and i != '高畫質' and i != '60fps' and i != '1080p']    # 这些特征 没有参考意义，为用户删去
                if bool_subt:  # 有“中字“，加上特征”中文字幕”
                    genres.append('中文字幕')
                if bool_divulge:   # 是流出无码片，加上特征'无码流出'
                    genres.append('无码流出')
                # print(genres)
                # arzon的简介 #########################################################
                # 去arzon找简介
                if bool_nfo and bool_plot and jav_epi == 1:
                    plot, status_arzon, acook = find_plot_arzon(jav_num, acook, proxy_arzon)
                    if status_arzon == 0:
                        pass
                    elif status_arzon == 1:
                        num_warn += 1
                        record_warn('    >第' + str(num_warn) + '个失败！找不到简介，尽管arzon上有搜索结果：' + path_relative + '\n')
                    else:
                        num_warn += 1
                        record_warn('    >第' + str(num_warn) + '个失败！找不到简介，影片被arzon下架：' + path_relative + '\n')
                    # 需要翻译简介
                    if bool_tran:
                        plot = tran_plot(tran_id, tran_sk, plot, to_language)
                        if plot.startswith('【百度'):
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！翻译简介失败：' + path_relative + '\n')
                    # 去除xml文档不允许的特殊字符 &<>  \/:*?"<>|
                    plot = replace_xml(plot)
                    # print(plot)
                else:
                    plot = ''
                #######################################################################
                # jav_name 是自始至终的 文件名（不带文件类型）  jav_file是自始至终的 文件名（完整带文件类型） root是原所在文件夹的路径  root_now 是现在（新）所在文件夹的路径
                # path_jav 是现在视频路径   path_subt是现在字幕路径   subt_file是 自始至终的 字幕文件名（带文件类型）  jav_folder是自始至终的 所在文件夹名（不是路径）
                dict_nfo['视频'] = dict_nfo['原文件名'] = jav_name    # dict_nfo['视频']， 先定义为原文件名，【即将变化】
                jav_folder = dict_nfo['原文件夹名'] = root.split(sep)[-1]    # 当前影片的文件夹名称，【即将变化】
                path_subt = root + sep + subt_file  # 当前字幕的路径，【即将变化】
                root_now = root    # 当前影片的文件夹路径，【即将变化】
                # 是CD1还是CDn？
                if num_all_episodes > 1:
                    str_cd = '-cd' + str(jav_epi)
                else:
                    str_cd = ''

                # 1重命名视频【和其他整理模式没区别】
                if bool_rename_mp4:
                    # 构造新文件名
                    jav_name = ''
                    for j in list_rename_video:
                        jav_name += dict_nfo[j]
                    jav_name = jav_name.rstrip() + str_cd          # 【发生变化】jav_name  去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
                    # 新的完整文件名，新的路径
                    dict_nfo['视频'] = jav_name                   # 【发生变化】 dict_nfo['视频']
                    jav_file = jav_name + video_type              # 【发生变化】jav_file，下面可能重命名视频不成功，但仍然围绕成功的jav_file来命名
                    path_jav_new = root_now + sep + jav_file      # 【临时变量】path_jav_new 新路径
                    # 理想状态下，还不存在目标同名文件
                    if not exists(path_jav_new):
                        # 重命名视频
                        move(path_jav, path_jav_new)
                        path_jav = path_jav_new                  # 【发生变化】 path_jav
                        record_video_old(jav_file, jav.file)
                    # 已存在目标文件，但就是现在的文件
                    elif path_jav.upper() == path_jav_new.upper():
                        try:
                            move(path_jav, path_jav_new)
                            path_jav = path_jav_new              # 【发生变化】 path_jav
                        except:  # windows本地磁盘，“abc-123.mp4”重命名为“abc-123.mp4”或“ABC-123.mp4”没问题，但有用户反映，挂载的磁盘会报错“file exists error”
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！请自行重命名大小写：' + path_relative + '\n')
                    # 存在目标文件，不是现在的文件。
                    else:
                        num_fail += 1
                        record_fail(
                            '    >第' + str(num_fail) + '个失败！重命名影片失败，重复的影片，已经有相同文件名的视频了：' + path_jav_new + '\n')
                        continue  # 【退出对该jav的整理】
                    print('    >修改文件名' + str_cd + '完成')
                    # 重命名字幕
                    if subt_file and bool_rename_subt:
                        subt_file_new = jav_name + subt_type     # 【临时变量】subt_file_new
                        path_subt_new = root_now + sep + subt_file_new    # 【临时变量】path_subt_new
                        if path_subt != path_subt_new:
                            move(path_subt, path_subt_new)
                            subt_file = subt_file_new           # 【发生变化】 subt_file
                            path_subt = path_subt_new           # 【发生变化】 path_subt
                        print('    >修改字幕名完成')

                # 2 归类影片【和其他整理模式没区别】只针对视频文件和字幕文件。注意：第2操作和（下面第3操作或者下面第7操作）互斥，只能执行一个，归类影片是针对“文件”还是“文件夹”。
                if bool_classify and not bool_classify_folder:
                    # 构造 移动的目标文件夹
                    root_dest = root_classify + sep
                    for j in list_classify_basis:
                        root_dest += dict_nfo[j].rstrip()      # 【临时变量】归类的目标文件夹路径    C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                    if not exists(root_dest):
                        os.makedirs(root_dest)
                    path_jav_new = root_dest + sep + jav_file  # 【临时变量】新的影片路径
                    # 目标文件夹没有相同的影片，防止用户已经有一个“avop-127.mp4”，现在又来一个
                    if not exists(path_jav_new):
                        move(path_jav, path_jav_new)
                        root_now = root_dest                   # 【发生变化】root_now   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                        path_jav = path_jav_new                # 【发生变化】path_jav   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\avop-127.mp4
                        print('    >归类视频文件完成')
                        # 移动字幕
                        if subt_file:
                            path_subt_new = root_now + sep + subt_file  # 【临时变量】新的字幕路径
                            if path_subt != path_subt_new:
                                move(path_subt, path_subt_new)
                                # 不再更新 path_subt，下面不会再操作 字幕文件
                            print('    >归类字幕文件完成')
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！归类失败，重复的影片，归类的目标文件夹已经存在相同的影片：' + path_jav_new + '\n')
                        continue   # 【退出对该jav的整理】

                # 3重命名文件夹【和其他整理模式没区别】如果是针对“文件”归类，这一步会被跳过。 用户只需要归类视频文件，不需要管文件夹。
                if bool_rename_folder:
                    # 构造 新文件夹名jav_folder_new
                    jav_folder_new = ''
                    for j in list_rename_folder:
                        jav_folder_new += (dict_nfo[j])
                    jav_folder_new = jav_folder_new.rstrip(' .')  # 【临时变量】新的所在文件夹。去除末尾空格和“.”，否则windows会自动删除它们，导致程序仍以为带空格和“.”
                    # 是独立文件夹，才会重命名文件夹
                    if bool_separate_folder:
                        if jav_epi == num_all_episodes:
                            # 同一车牌有n部，且这就是第n集，才会被重命名
                            list_root_now = root_now.split(sep)
                            del list_root_now[-1]
                            root_new = sep.join(list_root_now) + sep + jav_folder_new        # 【临时变量】新的影片路径。上级文件夹路径+新文件夹名称=新文件夹路径
                            # 想要重命名的目标影片文件夹不存在
                            if not exists(root_new):
                                # 修改文件夹
                                move(root_now, root_new)
                                root_now = root_new                                         # 【发生变化】root_now
                                path_jav = root_now + sep + jav_file                        # 【发生变化】path_jav
                                jav_folder = jav_folder_new                                 # 【发生变化】jav_folder
                            # 目标影片文件夹存在，但就是现在的文件夹，即新旧相同
                            elif root_now == root_new:
                                pass
                            # 真的有一个同名的文件夹了
                            else:
                                num_fail += 1
                                record_fail('    >第' + str(num_fail) + '个失败！重命名文件夹失败，已存在相同文件夹：' + root_new + '\n')
                                continue    # 【退出对该jav的整理】
                            print('    >重命名文件夹完成')
                    # 不是独立的文件夹，建立独立的文件夹
                    else:
                        root_separate_folder = root_now + sep + jav_folder_new   # 【临时变量】新的影片所在文件夹。 当前文件夹的上级文件夹路径+新文件夹=新独立的文件夹的路径
                        # 确认没有同名文件夹
                        if not exists(root_separate_folder):
                            os.makedirs(root_separate_folder)
                        path_jav_new = root_separate_folder + sep + jav_file    # 【临时变量】新的影片路径。
                        # 如果这个文件夹是现成的，在它内部确认有没有“avop-127.mp4”。
                        if not exists(path_jav_new):
                            move(path_jav, path_jav_new)
                            root_now = root_separate_folder  # 【发生变化】root_now
                            path_jav = path_jav_new          # 【发生变化】path_jav
                            jav_folder = jav_folder_new      # 【发生变化】jav_folder
                            # 移动字幕
                            if subt_file:
                                move(path_subt, root_separate_folder + sep + subt_file)
                                # 下面不会操作 字幕文件 了，path_subt不再更新
                                print('    >移动字幕到独立文件夹')
                        # 里面已有“avop-127.mp4”，这不是它的家。
                        else:
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！创建独立文件夹失败，已存在相同的视频文件：' + path_jav_new + '\n')
                            continue  # 退出对该jav的整理

                # 更新一下path_relative
                path_relative = sep + path_jav.replace(root_choose, '')  # 影片的相对于所选文件夹的路径，用于报错

                # 4写入nfo【独特】
                if bool_nfo and jav_epi == 1:
                    if bool_cd_only:
                        path_nfo = root_now + sep + jav_name.replace(str_cd, '') + '.nfo'
                    else:
                        path_nfo = root_now + sep + jav_name + '.nfo'
                    title_in_nfo = ''
                    for i in list_name_nfo_title:
                        title_in_nfo += dict_nfo[i]    # nfo中tilte的写法
                    # 开始写入nfo，这nfo格式是参考的kodi的nfo
                    f = open(path_nfo, 'w', encoding="utf-8")
                    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                            "<movie>\n"
                            "  <plot>" + plot + "</plot>\n"
                            "  <title>" + title_in_nfo + "</title>\n"
                            "  <originaltitle>" + title + "</originaltitle>\n"
                            "  <director>" + dict_nfo['导演'] + "</director>\n"
                            "  <year>" + dict_nfo['发行年份'] + "</year>\n"
                            "  <mpaa>NC-17</mpaa>\n"
                            "  <customrating>NC-17</customrating>\n"
                            "  <countrycode>JP</countrycode>\n"
                            "  <premiered>" + time_premiered + "</premiered>\n"
                            "  <release>" + time_premiered + "</release>\n"
                            "  <runtime>" + dict_nfo['片长'] + "</runtime>\n"
                            "  <country>日本</country>\n"
                            "  <studio>" + studio + "</studio>\n"
                            "  <id>" + jav_num + "</id>\n"
                            "  <num>" + jav_num + "</num>\n"
                            "  <set>" + series + "</set>\n")  # emby不管set系列，kodi可以
                    # 需要将特征写入genre
                    if bool_genre:
                        if bool_write_series and series:
                            f.write("  <genre>系列:" + series + "</genre>\n")
                        if bool_write_studio and studio:
                            f.write("  <genre>片商:" + studio + "</genre>\n")
                        if list_extra_genres:
                            for i in list_extra_genres:
                                f.write("  <genre>" + dict_nfo[i] + "</genre>\n")
                        # 需要简体的特征还是繁体？
                        if bool_zh:
                            for i in genres:
                                f.write("  <genre>" + dict_gen[i] + "</genre>\n")
                        else:
                            for i in genres:
                                f.write("  <genre>" + i + "</genre>\n")
                    # 需要将特征写入tag
                    if bool_tag:
                        if bool_write_series and series:
                            f.write("  <tag>系列:" + series + "</tag>\n")
                        if bool_write_studio and studio:
                            f.write("  <tag>片商:" + studio + "</tag>\n")
                        if list_extra_genres:
                            for i in list_extra_genres:
                                f.write("  <tag>" + dict_nfo[i] + "</tag>\n")
                        # 需要简体的特征还是繁体？
                        if bool_zh:
                            for i in genres:
                                f.write("  <tag>" + dict_gen[i] + "</tag>\n")
                        else:
                            for i in genres:
                                f.write("  <tag>" + i + "</tag>\n")
                    # 写入演员
                    for i in actors:
                        f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n  </actor>\n")
                    f.write("</movie>\n")
                    f.close()
                    print('    >nfo收集完成')

                # 5需要两张图片【独特】
                if bool_jpg:
                    # fanart和poster路径
                    path_fanart = root_now + sep
                    path_poster = root_now + sep
                    for i in list_name_fanart:
                        path_fanart += dict_nfo[i]
                    for i in list_name_poster:
                        path_poster += dict_nfo[i]
                    # print(path_fanart)
                    # kodi只需要一份图片，图片路径唯一
                    if bool_cd_only:
                        path_fanart = path_fanart.replace(str_cd, '')
                        path_poster = path_poster.replace(str_cd, '')
                    # emby需要多份，现在不是第一集，直接复制第一集的图片
                    elif jav_epi != 1:
                        try:
                            copyfile(path_fanart.replace(str_cd, '-cd1'), path_fanart)
                            print('    >fanart.jpg复制成功')
                            copyfile(path_poster.replace(str_cd, '-cd1'), path_poster)
                            print('    >poster.jpg复制成功')
                        except FileNotFoundError:
                            pass
                    # kodi或者emby需要的第一份图片
                    if check_pic(path_fanart):
                        # print('    >已有fanart.jpg')
                        pass
                    else:
                        # 下载封面
                        print('    >从javbus下载封面：', url_cover)
                        try:
                            download_pic(url_cover, path_fanart, proxy_bus)
                            print('    >fanart.jpg下载成功')
                        except:
                            num_fail += 1
                            record_fail('    >第' + str(
                                num_fail) + '个失败！下载fanart.jpg失败：' + url_cover + '，' + path_relative + '\n')
                            continue     # 退出对该jav的整理
                    # 裁剪生成 poster
                    if check_pic(path_poster):
                        # print('    >已有poster.jpg')
                        pass
                    else:
                        crop_poster_youma(path_fanart, path_poster)
                        # 需要加上条纹
                        if bool_watermark_subt and bool_subt:
                            add_watermark_subt(path_poster)
                        if bool_watermark_divulge and bool_divulge:
                            add_watermark_divulge(path_poster)

                # 6收集演员头像【和其他整理模式几乎没区别】
                if bool_sculpture and jav_epi == 1:
                    if actors[0] == '有码演员':
                        print('    >未知演员，无法收集头像')
                    else:
                        collect_sculpture(actors, root_now)

                # 7归类影片，针对文件夹
                if bool_classify and bool_classify_folder and jav_epi == num_all_episodes:    # 需要移动文件夹，且，是该影片的最后一集
                    # 用户选择的文件夹是一部影片的独立文件夹，为了避免在这个文件夹里又生成 归类的文件夹
                    if bool_separate_folder and root_classify.startswith(root):
                        print('    >无法归类，请选择该文件夹的上级文件夹作它的归类根目录')
                        continue   # 【退出对该jav的整理】
                    # 目标文件夹，暂时是现在的位置
                    root_dest = root_classify + sep
                    # 移动的目标文件夹
                    for j in list_classify_basis:
                        root_dest += dict_nfo[j].rstrip(' .')      # 【临时变量】 文件夹移动的目标上级文件夹  C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                    root_now_new = root_dest + jav_folder          # 【临时变量】 文件夹移动的目标路径   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\【葵司】AVOP-127\
                    # print(root_now_new)
                    if not exists(root_now_new):
                        os.makedirs(root_now_new)
                        # 把现在文件夹里的东西都搬过去
                        jav_files = os.listdir(root_now)
                        for i in jav_files:
                            move(root_now + sep + i, root_now_new + sep + i)
                        # 删除“旧房子”，这是javsdt唯一的删除操作，而且os.rmdir只能删除空文件夹
                        os.rmdir(root_now)
                        print('    >归类文件夹完成')
                    else:  # 用户已经有了这个车牌的文件夹
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！归类失败，重复的影片，归类的目标文件夹已存在相同文件夹：' + root_now_new + '\n')
                        continue   # 【退出对该jav的整理】

            except:
                num_fail += 1
                record_fail('    >第' + str(num_fail) + '个失败！发生错误，如一直在该影片报错请截图并联系作者：' + path_relative + '\n' + format_exc() + '\n')
                continue   # 【退出对该jav的整理】

    # 完结撒花
    print('\n当前文件夹完成，', end='')
    if num_fail > 0:
        print('失败', num_fail, '个!  ', root_choose, '\n')
        line = -1
        with open('【记得清理它】失败记录.txt', 'r', encoding="utf-8") as f:
            content = list(f)
        while 1:
            if content[line].startswith('已'):
                break
            line -= 1
        for i in range(line+1, 0):
            print(content[i], end='')
        print('\n“【记得清理它】失败记录.txt”已记录错误\n')
    else:
        print(' “0”失败！  ', root_choose, '\n')
    if num_warn > 0:
        print('“警告信息.txt”还记录了', num_warn, '个警告信息！\n')
    # os.system('pause')
    input_start_key = input('回车继续选择文件夹整理：')
