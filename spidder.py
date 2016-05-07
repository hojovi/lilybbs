import urllib.request
import time
from base import prefixes,category_index,boards,boards_chinese_index
#pip install BeautifulSoup4
#pip install html5lib
from bs4 import BeautifulSoup

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

#十大
def top10():
    result=crawl("http://bbs.nju.edu.cn/bbstop10")
    
    top10=[]
    soup=BeautifulSoup(result)
    table=soup.table
    tr=table.find_all('tr')
    for i in range(1,len(tr)):
        tds=tr[i].find_all('td')
        cur={}
        cur['rand']=int(tds[0][1])
        cur['board_url']=td[1].a['href']
        cur['board_name']=td[1].a.string
        cur['post_href']=td[2].a['href']
        cur['post_title']=td[2].a.string
        cur['sender_url']=td[3].a['href']
        cur['sender_nickname']=td[3].a.string
        cur['reply_count']=td[4].string
        top10.append(cur)
    return top10





#各区热点
def topall():
    result=crawl("http://bbs.nju.edu.cn/bbstopall")
    
    topall=[]
    soup=BeautifulSoup(result,'html5lib')
    table=soup.table
    cur={}
    for tr in table.find_all('tr'):
        print(tr)
        if not tr.td.has_attr('colspan') and tr.td.text.strip()=='':
            continue
        elif tr.td.has_attr('colspan') and tr.td['colspan']=='2':
            if len(cur)!=0:
                topall.append(cur)
            cur={}
            category_url=tr.td.img['onclick'][10:]
            category_url=category_url[:len(category_url)-1]
            cur['category_url']=category_url
            cur['category_img_src']=tr.td.img['src']
            cur['content']=[]
        else:
            for td in tr.find_all('td'):
                post={}
                a=td.find_all('a')
                text=td.text
                post['post_url']=a[0]['href']
                post['post_title']=text[:text.find('[')]
                post['board_url']=a[1]['href']
                post['board_name']=text[text.find('[')+1:len(text)-1]
                cur['content'].append(post)
    topall.append(cur)
    return topall





#本函数仅返回默认页，需要从默认页中拿到最大序号，本版域名，版主，版主寄语等信息
#返回None，表明网页做过更新，此函数失效
#返回的dict有以下信息：本版域名，版主id，版内在线，版主寄语，当前置顶帖
def board_base_info(url):
    board={}
    result=crawl(url)

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

    #处理第三个表，只要置顶帖
    posts=[]
    table3=tables[3]
    trs=table3.find_all('tr')
    for i in range(1,len(trs)):
        cur={}
        tds=trs[i].find_all('td')
        if tds[0].string is not None:
            break
        cur['作者']=tds[2].a.string
        cur['日期']=tds[4].nobr.string
        cur['标题']=tds[5].a.string
        cur['标题url']=tds[5].a['href']
        cur['人气']=tds[6].font.string
        posts.append(cur)
    board['置顶帖']=posts

    return board






#按序号从大到小排序，输出到path文件
#分别为序号，作者，日期，标题，标题url，人气
def board(board_id,path):
    file=open(path,'w',encoding='utf8')
    url=prefixes['版块']%board_id
    
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
            #到了第一篇文章
            if tds[0].string=='1':
                file.close()
                return
            cur=[]
            cur.append(tds[0].string)
            cur.append(tds[2].a.string)
            cur.append(tds[4].nobr.string)
            cur.append(tds[5].a.string)
            cur.append(tds[5].a['href'])
            cur.append(tds[6].font.string)
            file.write(','.join(cur))
            file.write('\n')

        #之前在页面内找上一页，但是现在知道每一页只有20条帖子（除置顶帖），访问的是有规律的地址，所以把当前页面帖子最小序号减20就可以得到完全不同的新页面
        url=prefixes['板块页面']%(board_id,int(cur[0])-20)
        time.sleep(1)
    file.close()


board('NJUExpress','NJUExpress.txt')


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
