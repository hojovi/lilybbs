from spidder import top10
import datetime

top10=top10()
f=open('top10/'+datetime.date.today()+'.txt','w',encoding='utf8')
for item in top10:
    f.write(','.join(item))
    f.write('\n')
f.close()
