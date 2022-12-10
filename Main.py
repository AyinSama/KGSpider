'''
Author: 阿茵Ayin
Date: 2022-12-10 11:49:30
Description: 创客社高一级Python毕业项目
'''

import Spider as sc         # 爬虫
import prettytable as pt    # 表格式打印

if __name__ == '__main__':

    searcher = sc.Searcher()
    searchResults = searcher.search("梦回还", 1, 30)
    
    spider = sc.Spider(searchResults)
    songs = spider.parseDownloadLinks()
    
    table = pt.PrettyTable()
    table.field_names = ["No.", "歌曲名", "下载链接"]
    for i, song in enumerate(songs):
        # table.add_row([i, song["name"], song["link"]])
        table.add_row([i, song["name"], song["link"][:70] + "..."])
        
    print(table)
