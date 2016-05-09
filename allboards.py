from spidder import board
from base import boards
import datetime
import time
import pymysql

conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='lilybbs',charset='utf8')
cur=conn.cursor()

date=datetime.datetime.now()
date=date-datetime.timedelta(days=1)

def judge(item):
    post_time=item[2]
    if post_time<date:
        return False
    return True

def conduct(item):
    sql='insert into posts_base_info(boardId,sequence,sender,post_time,title,url,reply,popularity) values(%s,%s,%s,%s,%s,%s,%s,%s)'
    s=(b[4],item[0],str(item[1]),item[2],item[3],item[4],item[5],item[6])
    cur.execute(sql,s)

try:
    for b in boards:
        print(b[0])
        if b[0].lower()<'hku':
            continue
        board(b[0],judge,conduct)
        time.sleep(0.5)
    conn.commit()
finally:
    cur.close()
    conn.close()
    
##board('FleaMarket','boards/FleaMarket.txt',
##          datetime.datetime.strptime('2016-5-7','%Y-%m-%d'))
