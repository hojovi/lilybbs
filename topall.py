from spidder import topall
from base import board_index
import datetime
import pymysql

topall=topall()
cur_time=datetime.datetime.now()

conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='lilybbs',charset='utf8')
cur=conn.cursor()

try:
    sql='replace into topall(boardId,post_url,title,end_time) values(%s,%s,%s,%s)'
    for a in topall:
        cur.execute(sql,(board_index[a[2]],a[0],a[1],cur_time))
    conn.commit()
finally:
    cur.close()
    conn.commit()
