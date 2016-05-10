import pymysql
from base import big_category,category_index,boards

conn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='lilybbs',charset='utf8')
cur=conn.cursor()

big_categories_sql='''create table if not exists big_categories(
    id int primary key,
    name varchar(20) unique key not null
    )engine=innodb default charset=utf8 collate=utf8_general_ci;
'''
cur.execute(big_categories_sql)
sql='insert into big_categories(id,name) values%s'%(','.join('(%s,\'%s\')'%(i,big_category[i]) for i in range(0,len(big_category))))
cur.execute(sql)


categories_sql='''create table if not exists categories(
    id int primary key auto_increment,
    name varchar(6) unique key not null,
    bigCategoryId int not null,
    foreign key(bigCategoryId) references big_categories(id) on delete cascade on update cascade
    )engine=innodb default charset=utf8 collate=utf8_general_ci;
'''
cur.execute(categories_sql)
sql='insert into categories(name,bigCategoryId) values(\'%s\',%d)'
categories={}
for key,value in category_index.items():
    cur.execute(sql%(key,value))
    cur.execute('select last_insert_id()')
    categories[key]=int(cur.fetchone()[0])

boards_sql='''create table if not exists boards(
    id int primary key,
    name varchar(30) unique key not null,
    description varchar(50) unique key not null,
    categoryId int not null,
    mediator varchar(30) null,
    foreign key(categoryId) references categories(id) on delete cascade on update cascade
    )engine=innodb default charset=utf8 collate=utf8_general_ci;
'''
cur.execute(boards_sql)
for board in boards:
    if board[3] is not None:
        cur.execute('insert into boards(name,description,categoryId,mediator,id) values(\'%s\',\'%s\',%d,\'%s\',%d)'%(board[0],board[1],categories[board[2]],board[3],board[4]))
    else:
        cur.execute('insert into boards(name,description,categoryId,id) values(\'%s\',\'%s\',%d,%d)'%(board[0],board[1],categories[board[2]],board[4]))

posts_base_info_sql='''create table if not exists posts_base_info(
    id int primary key auto_increment,
    boardId int not null,
    sequence int not null,
    sender varchar(30) not null,
    post_time datetime not null,
    title varchar(100) not null,
    url varchar(100) not null,
    reply int not null,
    popularity int not null,
    foreign key(boardId) references boards(id) on delete cascade on update cascade
    )engine=innodb default charset=utf8 collate=utf8_general_ci;
'''
cur.execute(posts_base_info_sql)

top10_sql='''create table if not exists top10(
    id int primary key auto_increment,
    boardId int not null,
    post_url varchar(100) not null,
    title varchar(60) not null,
    sender varchar(20) not null,
    followers int not null,
    foreign key(boardId) references boards(id) on delete cascade on update cascade
    )engine=innodb default charset=utf8 collate=utf8_general_ci;
'''
cur.execute(top10_sql)
