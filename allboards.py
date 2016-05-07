from spidder import board
from base import boards
import configparser

conf=configparser.ConfigParser()
conf.read('conf.ini')

for b in boards:
    start=board(b[0],'boards/'+b[0]+'.txt',int(conf.get('START','NJUExpress')))
    conf.set('START','NJUExpress',str(start))

conf.write(open('conf.ini','w',encoding='utf8'))
