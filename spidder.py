#脚本文件函数大致说明
#top10()，全站十大
#topall()，各区热点
#board_base_info(board_id)，版块基本信息
#board_hot(board_id),版块置顶帖
#board(board_id,filename,date)，版块所有帖子，由于帖子数量可能很多，所以要输出到文件中，从start开始，返回当前最大序号

#board_group()，所有版块，用不到

import urllib.request
import time
from base import prefixes,big_category
#pip install BeautifulSoup4
#pip install html5lib
from bs4 import BeautifulSoup
import datetime
import re

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
    return response.read().decode(encoding='gb18030',errors='ignore')


#十大
#返回list[list...]，按名次排序
#分别是：版块id，帖子url，帖子题目，发帖人，回复次数
def top10():
    result=crawl(domain+"bbstop10")
    
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
    result=crawl(domain+"bbstopall")
    
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
        print('版块没有更多信息')
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
    table3=tables[len(tables)-1]
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


#ExcellentBM，更具体来说，是http://bbs.nju.edu.cn/bbstcon?board=ExcellentBM&file=M.1065628891.A
#                           这个帖子，你tmd能不能告诉我0xb9究竟是用什么编码的？
#版块浏览模式分为主题模式和一般模式，爬网页应该爬主题模式的网页

#还有，貌似最开始登陆一个页面时，有时候会先显示一个不相干的网页，然后5秒后跳转到真正的主页
#我在这里的处理是如果找到“将会在 5 秒钟之后自动跳转到版面”这几个字，那么直接continue循环
#用re模块

#按序号从小到大排序，返回list[list...]
#传入两个函数参数，judge：判断每条数据，返回True继续执行，返回False停止,conduct：对每条数据进行处理
#每条信息的内容分别是：序号，作者，日期，标题，标题url，回帖, 人气
def board(board_id,judge,conduct):
    url=prefixes['主题模式']%(board_id)

    #网站有防dos措施，所以每次间隔0.5秒
    while True:
        result=crawl(url)
        soup=BeautifulSoup(result,'html5lib')
        tables=soup.find_all('table')

        if len(re.findall('将会在 5 秒钟之后自动跳转到版面',result))>0:
            time.sleep(0.5)
            continue

        num=-1

        ##HKU版块一个帖子都没有。。。
        if len(tables)==0:
            return
        
        table3=tables[len(tables)-1]
        trs=table3.find_all('tr')
        #从大到小
        for i in range(len(trs)-1,0,-1):
            tds=trs[i].find_all('td')
            if tds[0].string is None:
                break
            cur=[]
            num=int(tds[0].string)
            
            cur.append(num)
            cur.append(tds[2].a.string)
            
            ##没办法，偏偏就是不给年份，然而有些区就是死区，几百年都没个帖子，所以更具体的时间还要点进帖子里面去看
            ##我发现可以从帖子对应的url中读取到距离1970的时间，看来文件是以时间命名的，啊哈，还是老天眷顾我啊
            post_time=datetime.datetime.fromtimestamp(int(re.search(r'&file=\w\.(\d+)',tds[4].a['href']).group(1)))
            cur.append(post_time)
            cur.append(tds[4].a.string.strip())
            cur.append(domain+tds[4].a['href'])
            rp=tds[5].text.split('/')
            cur.append(int(rp[0]))
            cur.append(int(rp[1]))

            if judge(cur) is False:
                return
            else:
                conduct(cur)

            #到序号1了，前面已经没有数据了
            if num==1:
                return

        if num<1:
            return

        #页面显示序号为1，其实真正的序号为0，就像这样，所以直接是num
        url=prefixes['板块页面']%(board_id,num-21)
        time.sleep(0.5)


##帖子
##务必访问主题模式而非一般模式，因为一般模式对每个帖子的回复也要单列一个出来
##返回list[list...]，格式
##依次是：发信人id，发信人name，信区，标题，发信站，发帖时间，帖子内容，发帖ip
def get_post(url):
    result=crawl(domain+url)
    post=[]
    
    soup=BeautifulSoup(result,'html5lib')

    content=soup.table.textarea.string

    for table in soup.find_all('table'):
        content=table.textarea.string
        cur=[]
        
        m=re.search(r'发信人: ([^\s]*)[\s]*\(([^\)]*)\)',content)
        cur.append(m.group(1))
        cur.append(m.group(2))

        m=re.search(r'信区: ([^\s]*)\s',content)
        cur.append(m.group(1))

        m=re.search(r'标  题: ([^\n]*)',content)
        cur.append(m.group(1))

        m=re.search(r'发信站: ([^\s]*)\s*\(([^\)]+)\)\s*(((?!--)[\s\S])*)',content)
        cur.append(m.group(1))
        cur.append(m.group(2))
        #这是帖子的内容，需要parse一下，参考bbs.js，这里只处理了我见过的，可能以后还要扩充
        a=m.group(3)
        a = re.subn(r'\033\[[\d;]*(3\d{1})[\d;]*(4\d{1})[\d;]*m', "", a)[0]
        a = re.subn(r'\033\[[\d;]*(4\d{1})[\d;]*(3\d{1})[\d;]*m', "", a)[0]
        a = re.subn(r'\033\[[\d;]*(3\d{1}|4\d{1})[\d;]*m', "", a)[0]
        a = re.subn(r'\033\[0*m', "", a)[0]
        a = re.subn(r'\033\[[\d;]*(I|u|s|H|m|A|B|C|D)', "", a)[0]
        a = re.subn(r'\033', "", a)[0]
        ##处理完毕
        cur.append(a)
        

        m=re.search(r'\[FROM: (\d+.\d+.\d+.\d+)\]',content)
        cur.append(m.group(1))

        post.append(cur)

    return post


#####################
##下面都是用不到的函数##

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

#日期帮助函数，只针对小百合的日期显示
#小百合的日期并没有包含年份，要查看年份需要点进帖子中看
#版块日期一列没有包含年份，让人头疼，但是可以从帖子href推出时间，所以不再需要这个函数
def parseDatetime(string,year):
    c=datetime.datetime.strptime(string,'%b  %d %H:%M')
    c.replace(year=year)
    return c
