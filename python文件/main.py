# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import difflib
import re
import os
import feedparser
from fastapi import FastAPI, Query
from pydantic import BaseModel
import sqlite3
import qbittorrentapi
import json
import ssl
import requests

api_Key = '0bd21ef885a43cf4e394ecf49d9c61f8'
VERIFY_WEBUI_CERTIFICATE=False

class RssInfo(BaseModel):
    username:str
    password:str
    rssUrl:str
    qbPort:str

#路由
app = FastAPI()
@app.post('/')
async def mainProg(rssInfo:RssInfo):
    username=rssInfo.username
    password=rssInfo.password
    with open("./settings.json", 'r') as load_f:
        load_dict = json.load(load_f)
    print(username+';'+password)
    print(load_dict['username']+';'+load_dict['password'])
    if username != load_dict['username'] or password != load_dict['password']:
        return {'message': '用户名密码错误'}
    rssUrl=rssInfo.rssUrl
    qbHost=rssInfo.qbPort
    print(rssInfo)
    try:
        conn = sqlite3.connect('./anime.db')
        cursor = conn.cursor()
        sql = '''create table IF NOT EXISTS anime (
        ani_name text,
        season Integer,
        num Integer,
        flag Integer,
        primary key (ani_name,season))'''
        print(sql)
        cursor.execute(sql)

        aniDict = rssTranser(rssUrl)
        tvId = tmdbNameSearch(aniDict)
        aniSeries = tmdbSeriesSearch(tvId, aniDict)
        storeInfo(aniSeries, cursor,conn)
        cursor.close()
        conn.close()
        #qbPort = 'https://home.acglover.store:8081'
        print(qbHost)
        qbRssAdd(rssUrl,aniSeries, qbHost,aniDict['fanSub']+aniDict['chn'])
        # animeName='[NC-Raws] 世界頂尖的暗殺者轉生為異世界貴族 - 08 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4].wmv'
        # animeName='[Nekomoe kissaten][180-kimimimi][09][1080p][JPSC].mp4'
        # #animeName='[Nekomoe kissaten&LoliHouse] Sono Bisque Doll wa Koi wo Suru - 01 [WebRip 1080p HEVC-10bit AAC ASSx2].mkv'
    except Exception as e:
        print(e)
        return {'message':'error'}
    return {'message': 'success'}

def rssNameTrans(rssName):
    return None


#具体的torrent名正则
def fileNameTrans(name):
    suffix=''
    chn='简体中文'
    if name.find('CHT')!=-1 or name.find('cht')!=-1:
        chn='繁体中文'
    if name.find('JPSC')!=-1 or name.find('jpsc')!=-1:
        chn='简日双语'
    if name.find('JPTC')!=-1 or name.find('jptc')!=-1:
        chn='繁日双语'
    if name.endswith(('.mp4', '.mkv', '.avi', '.wmv', '.iso')):
        suffix=os.path.splitext(name)[-1]
        name=os.path.splitext(name)[0]
    pattern1=r'\[[^\[\]]+\]\[[^\[\]]+\]\[[^\[\]]+\]\[\d+\]'
    matchRes = re.match(pattern1, name, re.S)
    print('本次名字是'+name)
    if matchRes is None:
        pattern1=r'\[[^\[\]]+\]\[[^\[\]]+\]\[[^\[\]]+\]'
        matchRes=re.match(pattern1,name,re.S)
    if matchRes is None:
        pattern1 = r'\[.*?\].*?\[.*?\]'
        matchRes = re.match(pattern1, name, re.S)
    result1=matchRes.group()
    pattern2=r'[^\[\]]+'
    #先拆3个，第一个字幕组不要，第二个可能：名-季名-集 ;名-季; 名-集; 名  第三个可能:集 ; 来源
    words=re.findall(pattern2, result1, re.S)
    #拿一下字幕组名吧..
    fanSub=words[0]
    word1=words[1]
    word1Arr=word1.split(' - ')
    aniName=''
    seriesName=''
    romaName=''
    number=''
    seriesChnName=''

    if len(word1Arr) == 1:
        aniName=word1Arr[0].strip()
    else:
        if len(word1Arr) == 2:
            aniName = word1Arr[0].strip()
            word1Ind2 = word1Arr[1].strip()
            if re.match('\d+',word1Ind2) == None:
                seriesName=word1Ind2
            else:
                number=word1Ind2
        else:
            if len(word1Arr) == 3:
                aniName = word1Arr[0].strip()
                seriesName = word1Arr[1].strip()
                number = word1Arr[2].strip()
    word2=words[2].strip()
    if re.match('\d+', word2) != None:
        number = word2
    else :
        if number == '':
            aniName+=' / '+word2
    #判断形如：[極影字幕社][進擊的巨人 最終季][Shingeki no Kyojin The Final Season]
    if len(words) > 3:
        word3=words[3].replace(' ','')
        if re.match('\d+', word3) != None:
            number = word3
    print(aniName)
    if aniName.find('/')!=-1:
        names=aniName.split('/')
        aniName=names[0]
        romaName=names[1]
    else:
        if aniName.find('-')!=-1:
            names=aniName.split('-')
            aniName=names[0]
            romaName=names[1]
        else:
            if aniName.find('_')!=-1:
                names=aniName.split('_')
                aniName=names[0]
                romaName=names[1]
    aniName=aniName.strip()
    romaName=romaName.strip()
    if aniName.find(' ') != - 1 and re.match(r'[^0-9a-zA-Z]+ *[0-9a-zA-Z]+',aniName) is  None:
        names = aniName.split(' ')
        aniName = names[0]
        seriesChnName = names[1]
    if seriesName == '' and seriesChnName == '':
        pattern3=r'([^0-9a-zA-Z]+)( *[0-9a-zA-Z]+)'
        matchRes=re.match(pattern3,aniName)
        if matchRes is not None:
            seriesChnName=aniName
            aniName=matchRes.group(1).strip()
    aniNameDict={'name':aniName,'series':seriesName,'num':number,'sChnName':seriesChnName,'romaName':romaName,'suffix':suffix,'chn':chn,'fanSub':fanSub}
    print(aniNameDict)
    return aniNameDict

#rss剧集名更改处理
def rssTranser(rssUrl):
    feed=feedparser.parse(rssUrl)
    rssName = feed['entries'][0]['title']
    #rssName='[Skymoon-Raws] 進擊的巨人 第四季 / Shingeki no Kyojin - The Final Season - 17 [ViuTV][WEB-DL][1080p][AVC AAC][繁體外掛][MP4+ASSx2](正式版本)'
    #rssName='[酷漫404][進擊的巨人 最終季 Part.2][76][1080P][WebRip][繁日對白字幕+特效註解字幕][HEVC-10bit AAC][MKV][字幕組招人內詳]'
    #rssName='[豌豆字幕组&LoliHouse] 进击的巨人 / Shingeki no Kyojin - 76 [WebRip 1080p HEVC-10bit AAC][简繁内封字幕]'
    #rssName='【極影字幕社】 ★10月新番 【進擊的巨人 最終季】【Shingeki no Kyojin The Final Season】【17】BIG5 MP4_720'
    rssName=rssName.replace('【','[')
    rssName=rssName.replace('】',']')
    rssName = rssName.replace('★', '')
    rssName=re.sub(r' *[*[0-9]+月新番 *]*','',rssName)
    rssName = re.sub(r'Part.*?\d', '', rssName)
    rssName = re.sub(r'v\d', '', rssName)
    rssName = rssName.replace('] [','][')
    #print(rssName)
    #print(fileNameTrans(rssName)['name'])
    return fileNameTrans(rssName)


#tmdb搜索剧集名
def tmdbNameSearch(aniNameDict):
    animeName=aniNameDict['name']
    seriesName=aniNameDict['series']
    number=aniNameDict['num']
    lang='en'
    url=transSearchLang(animeName,lang,api_Key)

    #response=requests.get(url)
    #searchResult=response.json()
    results=[]
    #resultsEn=searchResult['results']
    lang='zh-TW'
    url = transSearchLang(animeName, lang, api_Key)
    resultsTw=requests.get(url).json()['results']
    lang='zh-CN'
    url = transSearchLang(animeName, lang, api_Key)
    resultsCN=requests.get(url).json()['results']
    #print(resultsCN)
    #results.append(resultsEn)
    results.append(resultsTw)
    results.append(resultsCN)
    if len(results) == 0:
        print('none')
    finalResult=None
    topNum=-1
    langIndex=-1
    tvId=-1
    for index,resultsLang in enumerate(results):
        for result in resultsLang:
            #print(result['name'])
            name=result['name']
            simNum=difflib.SequenceMatcher(None,name,animeName).quick_ratio()
            if simNum >= 0.3 and simNum>topNum:
                topNum=simNum
                finalResult=name
                langIndex=index
                tvId=result['id']
    langArr=['zh-TW','zh-CN']
    if langIndex == -1:
        print('出错')
    else:
        lang=langArr[langIndex]
        print(finalResult+':'+str(topNum)+';'+lang)
        return tvId

#tmdb搜索具体剧集信息
def tmdbSeriesSearch(tvid,aniDcit):
    lang='zh-CN'
    sChnName=aniDcit['sChnName']
    #第一季  转  第1季
    sChnNameSearchRes=re.search(r'第([一二三四五六七八九])季',sChnName)
    if sChnNameSearchRes is not None:
        digit = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
        schSeriesName=sChnNameSearchRes.group()
        replaceName=sChnNameSearchRes.group(1)
        sChnName=sChnName.replace(schSeriesName,schSeriesName.replace(replaceName,str(digit[replaceName])))
        print(sChnName)

    series=aniDcit['series']
    response=requests.get(transSearchSeries(tvid,lang,api_Key)).json()
    aniName=response['name']
    print(aniName)
    lastSeason=response['last_episode_to_air']['season_number']
    print(lastSeason)
    seasons=response['seasons']
    season_Num=lastSeason
    topDiff=-1
    if sChnName != '':
        for season in seasons:
            diffNum=difflib.SequenceMatcher(None,season['name'],sChnName).quick_ratio()
            if diffNum > topDiff:
                topDiff=diffNum
                season_Num = season['season_number']
        lang='zh-TW'
        response = requests.get(transSearchSeries(tvid, lang, api_Key)).json()
        seasons = response['seasons']
        for season in seasons:
            diffNum = difflib.SequenceMatcher(None, season['name'], sChnName).quick_ratio()
            if diffNum > topDiff:
                topDiff = diffNum
                season_Num = season['season_number']
    else:
        if series != '':
            lang = 'en'
            response = requests.get(transSearchSeries(tvid, lang, api_Key)).json()
            seasons = response['seasons']
            for season in seasons:
                diffNum = difflib.SequenceMatcher(None, season['name'], sChnName).quick_ratio()
                if diffNum > topDiff:
                    topDiff = diffNum
                    season_Num = season['season_number']
    return {'name':aniName,'seasons':seasons,'thisSeason':season_Num}
    #print(season_Num)
    #print(topDiff)




#tmdb搜索URL
def transSearchLang(animeName,lang,api_key):
    return 'https://api.themoviedb.org/3/search/tv?query='+animeName+'&language='+lang+'&api_key='+api_key

#tmdb剧集信息URL
def transSearchSeries(tvid,lang,api_key):
    return 'https://api.themoviedb.org/3/tv/'+str(tvid)+'?language='+lang+'&api_key='+api_key

# 存储数据库
def storeInfo(aniSeries,cursor,conn):
    seasons = aniSeries['seasons']
    aniName = aniSeries['name']
    thisSeason = aniSeries['thisSeason']

    sql = '''select MAX(season) 
        from anime
        where ani_name=:aniName'''

    results = cursor.execute(sql, {'aniName': aniName})
    maxResult = results.fetchall()[0][0]
    max_Season = -1
    if maxResult is not None:
        max_Season = maxResult
        print('最大季:' + str(max_Season))
    insertSql = '''insert into anime
        (ani_name,season,num,flag)
        values
        (:ani_name,:season,:num,:flag)
        '''
    for season in seasons:
        seasonNum = season['season_number']
        num = season['episode_count']
        flag = 0
        if num == thisSeason:
            flag = 1
        try:
            cursor.execute(insertSql, {'ani_name': aniName, 'season': seasonNum, 'num': num, 'flag': flag})
            conn.commit()
        except:
            print('已存在')

def qbRssAdd(rssUrl,aniSeries,qbPort,fanSubStr):
    qutoIndex=qbPort.rfind(':')
    qb_Url=qbPort[:qutoIndex]
    qb_Port=qbPort[qutoIndex+1:]
    seasons = aniSeries['seasons']
    aniName = aniSeries['name']
    thisSeason = aniSeries['thisSeason']
    qbt_client = qbittorrentapi.Client(
        host=qb_Url,
        port=int(qb_Port),
        username='admin',
        password='Chenyingda123',
        VERIFY_WEBUI_CERTIFICATE=False
    )
    print(qb_Url)
    print(str(qb_Port))
    try:
        qbt_client.auth_log_in()
    #qbittorrentapi.LoginFailed
    except Exception as e:
        print(e)
    print(qb_Url)
    print(str(qb_Port))
    qbt_client.rss_add_feed(rssUrl,aniName+'_'+fanSubStr)
    qbt_client.rss_set_rule(aniName+'_'+fanSubStr,{'enabled':True,'affectedFeeds':[rssUrl],'savePath':'/downloads/'+aniName+'/Season'+str(thisSeason)+'/'})
    print('结束了')

# if __name__ == '__main__':
    # rssUrl='https://bangumi.moe/rss/tags/567bda4eafc701435d468b61+615bb91fd7f73dd4ed5c4403+548ee0ea4ab7379536f56354'
    # rssUrl='https://bangumi.moe/rss/tags/615bb926d7f73dd4ed5c442b+58a9c1e6f5dc363606ab42ed+55b86e9224180bc3647fea43+548ee2ce4ab7379536f56358'
    # rssUrl = 'https://bangumi.moe/rss/tags/60de5da206c78696e4d11610+5869a894efe56b1860c8f814'
    # rssUrl='https://bangumi.moe/rss/tags/56857f57d4d7dbf20b597c52+567bda4eafc701435d468b61'



    #animeName='[NC-Raws] 世界頂尖的暗殺者轉生為異世界貴族 - 08 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4].wmv'
    #animeName='[Nekomoe kissaten][180-kimimimi][09][1080p][JPSC].mp4'
    #animeName='[Nekomoe kissaten&LoliHouse] Sono Bisque Doll wa Koi wo Suru - 01 [WebRip 1080p HEVC-10bit AAC ASSx2].mkv'




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
