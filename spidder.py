#脚本文件函数大致说明
#top10()，全站十大
#topall()，各区热点
#board_base_info(board_id)，版块基本信息
#board_hot(board_id),版块置顶帖
#board(board_id,filename,until)，版块所有帖子，由于帖子数量可能很多，所以要输出到文件中，直到序号为until，返回当前最大序号

#board_group()，所有版块，用不到

import urllib.request
import time
from base import prefixes,category_index,boards,boards_chinese_index,big_category
#pip install BeautifulSoup4
#pip install html5lib
from bs4 import BeautifulSoup
import datetime

#模拟浏览器
keys={
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"
    }

domain='http://bbs.nju.edu.cn/'



#获取网页内容，并不直接使用,供其他函数使用
def crawl(url):
    request=urllib.request.Request(url)
    request.add_header("User-Agent",keys["User-Agent"])
    request.add_header("Content-Type","text/html; charset=gb2312")
    response=urllib.request.urlopen(request)
    return response.read().decode('gbk')

#日期帮助函数，只针对小百合的日期显示
#小百合的日期并没有包含年份，要查看年份需要点进帖子中看
def parseDatetime(string,year):
    c=datetime.datetime.strptime(string,'%b  %d %H:%M')
    c.replace(year=year)
    return c

#十大
#返回list[list...]，按名次排序
#分别是：版块id，帖子url，帖子题目，发帖人，回复次数
def top10():
    result=crawl("http://bbs.nju.edu.cn/bbstop10")
    
    top10=[]
    soup=BeautifulSoup(result,'html5lib')
    table=soup.table
    tr=table.find_all('tr')
    for i in range(1,len(tr)):
        tds=tr[i].find_all('td')
        cur=[]
        cur.append(tds[1].a.string)
        cur.append(tds[2].a['href'])
        cur.append(tds[2].a.string.strip())
        cur.append(tds[3].a.string.strip())
        cur.append(tds[4].string.strip())
        top10.append(cur)
    return top10




#各区热点
#返回dict，key是大分类
#value是list[list...]，每项保存的分别是：帖子url，帖子标题，所在版块
def topall():
    result=crawl("http://bbs.nju.edu.cn/bbstopall")
    
    topall={}
    soup=BeautifulSoup(result,'html5lib')
    table=soup.table

    ##大分类的索引
    index=-1
    
    for tr in table.find_all('tr'):
        if not tr.td.has_attr('colspan') and tr.td.text.strip()=='':
            continue
        elif tr.td.has_attr('colspan') and tr.td['colspan']=='2':
            index+=1
            topall[big_category[index]]=[]
            cur=topall[big_category[index]]
        else:
            for td in tr.find_all('td'):
                post=[]
                a=td.find_all('a')
                post.append(a[0]['href'])
                post.append(a[0].string.strip())
                post.append(a[1].string)
                cur.append(post)
                
    return topall




#本函数仅返回默认页，需要从默认页中拿到最大序号，本版域名，版主，版主寄语等信息
#返回None，表明网页做过更新，此函数失效
#返回的dict有以下信息：本版域名，版主id，版内在线，版主寄语，当前置顶帖
def board_base_info(board_id):
    board={}
    result=crawl(prefixes['版块']%board_id)

    soup=BeautifulSoup(result,'html5lib')
    tables=soup.find_all('table')
    if len(tables)!=4:
        print('网页已经做过更新，本程序无法解析！')
        return None
    
    #处理第一个表
    contents=tables[1].tr.td.contents
    print(contents)
    board['本版域名']=contents[1].string
    board['版主']=[]
    i=3
    while True:
        if contents[i].name=='a':
            board['版主'].append(contents[i].string)
        elif contents[i].string.strip()!='':
            break
        i+=1
    pattern=re.compile(r'版内在线: (\d+)人')
    board['版内在线']=pattern.search(contents[i].string).group(1)

    #处理第二个表
    board['版主寄语']=tables[2].tr.td.font.string

    return board


#版块的置顶帖
#返回list[list...]
#每项分别是：作者，日期，标题，帖子url，人气
def board_hot(board_id):
    result=crawl(prefixes['版块']%board_id)

    soup=BeautifulSoup(result,'html5lib')
    tables=soup.find_all('table')
    if len(tables)!=4:
        print('网页已经做过更新，本程序无法解析！')
        return None

    #处理第三个表，只要置顶帖
    posts=[]
    table3=tables[3]
    trs=table3.find_all('tr')
    for i in range(1,len(trs)):
        cur=[]
        tds=trs[i].find_all('td')
        if tds[0].string is not None:
            break
        cur.append(tds[2].a.string)
        cur.append(tds[4].nobr.string)
        cur.append(tds[5].a.string[2:].strip())
        cur.append(tds[5].a['href'])
        cur.append(tds[6].font.string)
        posts.append(cur)

    return posts



#按序号从大到小排序，输出到path文件
#分别为序号，作者，日期，标题，标题url(没有加domain前缀)，人气
def board(board_id,path,until):
    if until<0:
        print(str(until)+' 为负！！')
        return -1
    file=open(path,'w',encoding='utf8')
    url=prefixes['版块']%board_id

    max_num=-1
    #网站有防dos措施，所以每次间隔一秒
    while True:
        result=crawl(url)
        soup=BeautifulSoup(result,'html5lib')
        tables=soup.find_all('table')

        table3=tables[3]
        trs=table3.find_all('tr')
        #从大到小
        for i in range(len(trs)-1,0,-1):
            tds=trs[i].find_all('td')
            if tds[0].string is None:
                break
            cur=[]
            num=int(tds[0].string)
            if num<until:
                return max_num
            if max_num==-1:
                max_num=num
            cur.append(tds[0].string)
            cur.append(tds[2].a.string)
            cur.append(tds[4].nobr.string)
            cur.append(tds[5].a.string.strip())
            cur.append(tds[5].a['href'])
            cur.append(tds[6].font.string)
            file.write(','.join(cur))
            file.write('\n')

        #之前在页面内找上一页，但是现在知道每一页只有20条帖子（除置顶帖），访问的是有规律的地址，所以把当前页面帖子最小序号减20就可以得到完全不同的新页面
        if num<=0:
            return max_num
        #页面显示序号为1，其实真正的序号为0，就像这样，所以要减21
        url=prefixes['板块页面']%(board_id,num-21)
        time.sleep(0.5)
    file.close()
    return max_num


#所有讨论区，只是为了得到所有版块，现在所有版块的信息已经放在base.py中了
#只有在版块发生变化时才需要这个函数
#返回list[list...],分别是：讨论区名称、序号、类别、中文版名、版主
def board_group():
    result=crawl('http://bbs.nju.edu.cn/bbsall')
    boards=[]
    
    soup=BeautifulSoup(result,'html5lib')
    trs=soup.table.find_all('tr')

    for i in range(1,len(trs)):
        tds=trs[i].find_all('td')
        cur=[]
        cur.append(tds[1].a.string)
        cur.append(tds[0].string)
        cur.append(tds[2].string)
        cur.append(tds[3].a.string)
        if len(tds[4].find_all('a'))==0:
            cur.append(None)
        else:
            cur.append(tds[4].a.string)
        boards.append(cur)

    return boards
