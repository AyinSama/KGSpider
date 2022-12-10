'''
Author: 阿茵Ayin
Date: 2022-12-10 11:50:48
Description: 创客社高一级Python毕业项目
'''

import time                         # 时间戳
import json                         # 处理请求的json
import requests as req              # 发请求爬数据
import urllib.parse as encoder      # 转换URL编码

# 这个接口是我看别的分析文章找到的
# 用起来比较复杂，需要还原摘要算法求出mid和signature参数
URL_COMPLEX_SEARCH = "https://complexsearch.kugou.com/v2/search/song"

# 这个接口是我以前分析出来的，用起来简单
# https://gitee.com/com_yin/kgmusic-downloader/blob/master/src/Util.py#L70
# https://songsearch.kugou.com/song_search_v2?keyword={关键词}&page={搜索结果的第几页}&pagesize={一页想获取多少首歌}
URL_SONG_SEARCH = "https://songsearch.kugou.com/song_search_v2"

# 获取歌曲相关信息的接口
# https://www.kugou.com/yy/index.php?r=play/getdata&hash={歌曲文件哈希}&album_id={专辑ID}&dfid={dfid}&mid={mid}
URL_GET_SONG_DATA = "https://www.kugou.com/yy/index.php"

# Edge User-Agent
UA_EDGE = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"""

# 请求链接里的mid参数，硬编码就行，可自行更换，但是没必要
# 想更换的话把下面链接作者提取出来的js算法放到浏览器上运行一遍get_mid函数，然后把返回值复制进来就行
# https://blog.csdn.net/weixin_45859193/article/details/128183790
GENERATED_MID = "ce19d661358c27a7e27ce1a1b909c9df"

# 请求链接里的dfid参数，硬编码就行
GENERATED_DFID = "11SZwX4QD0Hi4AY03D1gKoT0"
GENERATED_DFID_COLLECT = "d41d8cd98f00b204e9800998ecf8427e"

# 搜索器
class Searcher:
    
    # 搜索相关歌曲
    # keyword: 歌曲名或歌手名
    # page: 搜索结果的第几页
    # pageSize: 一页想获取多少首歌
    def search(this, keyword: str, page: int = 1, pageSize: int = 5) -> list :
        
        # 编码歌手名/歌曲名
        encKeyword = encoder.quote(keyword)
        
        # 请求头
        reqHeader = generateReqHeader()
        
        # 拼凑请求url
        reqUrl = URL_SONG_SEARCH
        reqUrl += "?keyword=" + encKeyword
        reqUrl += "&page=" + str(page)
        reqUrl += "&pagesize=" + str(pageSize)
        
        # 发请求爬json
        response = req.get(reqUrl, headers=reqHeader)
        
        # 改编码防乱码
        response.encoding = "utf-8"
        
        # 解析请求到的json
        respJson = json.loads(response.text)
        
        # 判断是否出现爬取错误
        errCode = respJson["error_code"]
        if errCode != 0:
            print("[ERROR] Error occurred when requesting song list! Error Code: {code}".format(code=errCode))
            return []
        
        # 获取歌曲列表
        songList = respJson["data"]["lists"]
        
        # 遍历歌曲列表并组合所需信息
        results = []
        for i, song in enumerate(songList):
            songInfo = {}
            songInfo["name"] = song["FileName"]
            songInfo["albumId"] = song["AlbumID"]
            songInfo["hash"] = song["FileHash"]
            results.append(songInfo)
        
        return results

class Spider:
    
    # 参数为Searcher::search返回的搜索结果
    def __init__(this, searchResult: list) -> None:
        this.data = searchResult

    # 解析所有歌曲的下载链接
    def parseDownloadLinks(this) -> list:
        
        results = []
        for i, song in enumerate(this.data):
            results.append({
                "name": song["name"],
                "link": this.parseDownloadLink(song)
            })
        
        return results
    
    # 解析单首歌曲的下载链接
    def parseDownloadLink(this, song: dict) -> str:
        
        # 请求头
        reqHeader = generateReqHeader()
        
        # 拼凑请求url
        reqUrl = URL_GET_SONG_DATA
        reqUrl += "?r=" + "play/getdata"
        reqUrl += "&hash=" + song["hash"]
        reqUrl += "&album_id=" + song["albumId"]
        reqUrl += "&dfid=" + GENERATED_DFID
        reqUrl += "&mid=" + GENERATED_MID
        
        # 发请求爬json
        response = req.get(reqUrl, headers=reqHeader)
        response.encoding = "utf-8"
        
        # 解析结果json
        respJson = json.loads(response.text)
        
        # 判断是否出现爬取错误
        errCode = respJson["err_code"]
        if errCode != 0:
            print("[ERROR] Error occurred when requesting song download link! Error Code: {code}".format(code=errCode))
            return ""
        
        # play_url和play_backup_url都可
        return respJson["data"]["play_url"]

# 获取当前时间的时间戳
def getCurrentTimeStamp() -> int:
    return int(time.time())

# 生成Cookie
def generateCookie() -> str:
    return "kg_mid={mid};kg_dfid={dfid};kg_dfid_collect={dfidc};Hm_lvt_aedee6983d4cfc62f509129360d6bb3d={timestamp};kg_mid_temp={mid};Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d={timestamp}".format(
            mid = GENERATED_MID,                        # mid
            dfid = GENERATED_DFID,                      # dfid
            dfidc = GENERATED_DFID_COLLECT,             # dfid_collect
            timestamp = getCurrentTimeStamp()           # 当前时间
        )

# 生成请求头
def generateReqHeader() -> dict:
    header = {}
    header["User-Agent"] = UA_EDGE
    header["Cookie"] = generateCookie()
    return header
