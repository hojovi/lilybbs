from spidder import top10
from base import board_index
import datetime
import pymysql

top10=top10()
cur_time=datetime.datetime.now()

conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='lilybbs',charset='utf8')
cur=conn.cursor()

try:
    select_sql='select count(*) from top10 where post_url=%s'
    insert_sql='insert into top10(boardId,post_url,title,sender,followers,end_time) values(%s,%s,%s,%s,%s,%s)'
    update_sql='update top10 set end_time=%s,followers=%s where post_url=%s'
    for a in top10:
        cur.execute(select_sql,(a[1],))
        for count in cur:
            if count[0]==0:
                cur.execute(insert_sql,(board_index[a[0]],a[1],a[2],a[3],a[4],cur_time))
            else:
                cur.execute(update_sql,(cur_time,a[4],a[1]))
    
    conn.commit()
finally:
    cur.close()
    conn.commit()

