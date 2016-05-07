import urllib.request
import urllib.parse
from io import BytesIO
import gzip
import re

#函数会返回一个字典型headers，用这个headers登陆，主要是注意headers里的cookie
def login(id,passwd):
    cookies={
        "LOGIN":"MG1523047",
        "SCREEN_NAME":"lpwdN7ox4/8LA8Grt6TupA==",
        "FOOTKEY":"208056530"
    }
    headers={
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	"Accept-Encoding":"gzip, deflate",
	"Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
	"Cache-Control":"max-age=0",
	"Connection":"keep-alive",
	"Content-Type":"application/x-www-form-urlencoded",
	"Cookie":"LOGIN=MG1523047; SCREEN_NAME=lpwdN7ox4/8LA8Grt6TupA==; FOOTKEY=208056530",
	"Host":"bbs.nju.edu.cn",
	"Origin":"http://bbs.nju.edu.cn",
	"Referer":"http://bbs.nju.edu.cn/cache_bbsleft.htm",
	"Upgrade-Insecure-Requests":"1",
	"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"
    }
    formdata={
	"id":id,
	"pw":passwd,
	"lasturl":""
    }
    request=urllib.request.Request("http://bbs.nju.edu.cn/vd50000/bbslogin?type=2",data=urllib.parse.urlencode(formdata).encode('gb2312'),headers=headers)
    response=urllib.request.urlopen(request)
    result=response.read()
    buf=BytesIO(result)
    gzipper=gzip.GzipFile(fileobj=buf)
    result=gzipper.read().decode('gb2312')

    #result是登陆后返回页面，现在需要从中找出能设置cookie的值
    pattern=re.compile(r'Net.BBS.setCookie\(\'(\d*)(\w*)+(\d*)\'\)')
    m=re.match(result)
    if m is None or len(m.groups())!=3:
        print("结果出错")
        print(result)
        return None
    else:
        cookies["_U_NUM"]=int(m.group(1))+2
        cookies["_U_UID"]=m.group(2)[1:]
        cookies["_U_KEY"]=int(m.group(3))-2
        str=""
        for key,val in cookies.items():
            str+=key+'='+str(val)+';'
        headers['Cookie']=str[:len(str)-1]
        return headers
