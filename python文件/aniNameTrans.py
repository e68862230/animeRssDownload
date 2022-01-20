import main
import sys
import os
import re
import sqlite3
import difflib

# 存储数据库
def loadInfo(aniName,seasonNum,num,conn):
    cursor = conn.cursor()

    sql = '''select SUM(num) 
        from anime
        where ani_name=:aniName
        and season<:season and season>0'''
    results = cursor.execute(sql, {'aniName': aniName,'season':seasonNum})
    maxResult = results.fetchall()[0][0]
    print('name:'+aniName+'season'+seasonNum+'maxResult'+str(maxResult))
    if maxResult is not None and int(num) > maxResult:
        num=str(int(num)-maxResult)
    return num

if __name__ == '__main__':
    argvs=sys.argv
    fileName=argvs[1]
    path=argvs[2]
    save_path=argvs[4]
    file_Num=argvs[3]
    ani_Info=main.fileNameTrans(fileName)
    num=ani_Info['num']
    fanSub=ani_Info['fanSub']
    chn=ani_Info['chn']
    conn = sqlite3.connect('/data/pythonService/anime.db')
    paths=path.split('/')
    seasonNUm=re.search(r'[0-9]+',paths[len(paths)-2]).group()
    aniName=paths[len(paths)-3]
    num=loadInfo(aniName,seasonNUm,num,conn)
    conn.close()
    os.rename(path,save_path+'/'+'S'+seasonNUm+'E'+num+'['+fanSub+']'+'_'+chn+ani_Info['suffix'])


