from spidder import top10
from base import board_index
import datetime
import pymysql

top10=top10()

conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='lilybbs',charset='utf8')
cur=conn.cursor()

try:
    sql='insert into top10(boardId,post_url,title,sender,followers) values(%s,%s,%s,%s,%s)'
    for a in top10:
        cur.execute(sql,(board_index[a[0]],a[1],a[2],a[3],a[4]))
    conn.commit()
finally:
    cur.close()
    conn.commit()

