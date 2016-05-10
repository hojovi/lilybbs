from spidder import top10
from base import board_index
import datetime
import pymysql

top10=top10()
cur_time=datetime.datetime.now()

conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='lilybbs',charset='utf8')
cur=conn.cursor()

try:
    sql='replace into top10(boardId,post_url,title,sender,followers,end_time) values(%s,%s,%s,%s,%s,%s)'
    for a in top10:
        cur.execute(sql,(board_index[a[0]],a[1],a[2],a[3],a[4],cur_time))
    conn.commit()
finally:
    cur.close()
    conn.commit()

