from spidder import topall
from base import board_index
import datetime
import pymysql

topall=topall()
cur_time=datetime.datetime.now()

conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='lilybbs',charset='utf8')
cur=conn.cursor()

try:
    select_sql='select count(*) from topall where post_url=%s'
    insert_sql='insert into topall(boardId,post_url,title,end_time) values(%s,%s,%s,%s)'
    update_sql='update topall set end_time=%s where post_url=%s'
    for a in topall:
        cur.execute(select_sql,(a[0],))
        for count in cur:
            if count[0]==0:
                cur.execute(insert_sql,(board_index[a[2]],a[0],a[1],cur_time))
            else:
                cur.execute(update_sql,(cur_time,a[0]))
    conn.commit()
finally:
    cur.close()
    conn.commit()
