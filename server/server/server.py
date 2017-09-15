import socket
import random
import pymysql
import json
import threading
from myemail import get_email
PORT = 6666
pass_word = 'zuohao8787'
def InsertIntoMysql(buff):
    print('######### InsertIntoMysql start #########\n')
    ins_succ = 0
    try:
        #create table all_sentence (id INT NOT NULL AUTO_INCREMENT,my_sentence VARCHAR(64) NOT NULL,PRIMARYY KEY(id))
        # 打开数据库连接
        db = pymysql.connect(host='127.0.0.1',user='root',passwd=pass_word,db='mysql')
        # 使用 cursor() 方法创建一个游标对象 cursor
        cur = db.cursor()
        #数据库语句
        #cur.execute('CREATE DATABASE IF NOT EXISTS sentence')#create db
        cur.execute('USE sentence')
        #insert
        #INSERT INTO all_sentence  values('1','123456');
        cur.execute('INSERT INTO all_sentence(my_sentence) VALUES(%s)',(buff))
        cur.connection.commit()
        ins_succ = 1
    except Exception as e:
        print(e)
    db.close()
    print('######### InsertIntoMysql end #########\n')
    return ins_succ

def load_sentence():
    print('######### load_sentence start #########\n')
    try:
        # 打开数据库连接
        db = pymysql.connect(host='127.0.0.1',user='root',passwd=pass_word,db='mysql')
        # 使用 cursor() 方法创建一个游标对象 cursor
        cur = db.cursor()
        cur.execute('USE sentence')
        #select one
        cur.execute('select count(*) from all_sentence')
        id_num = cur.fetchone()
        print("id_num = %s" % id_num)
        all_num = int(id_num[0])
        print("all_num = %s" % all_num)
        radnum = random.randint(1, all_num)
        print("radnum is %s" % radnum)
        print(str(radnum))
        try:
            cur.execute('SELECT * FROM all_sentence WHERE id = %s' % str(radnum))
        except Exception as sql_error:
            print(sql_error)
        data = cur.fetchone()
        print(data)
        return data
    except Exception as e:
        print(e)
    print('######### load_sentence end #########\n')
    db.close()

#load reminder from sql
def load_reminder():
    print('######### load_reminder start #########\n')
    msg = []
    try:
        # 打开数据库连接
        db = pymysql.connect(host='127.0.0.1',user='root',passwd=pass_word,db='mysql')
        # 使用 cursor() 方法创建一个游标对象 cursor
        cur = db.cursor()
        cur.execute('USE Reminder')
        #select one
        num1 = cur.execute('select time,msg from date')
        buff_1 = cur.fetchmany(num1)
        for m in buff_1:
            msg.append(m)

        num2 = cur.execute('select time,msg from month')
        buff_2 = cur.fetchmany(num2)
        for n in buff_2:
            msg.append(n)
        #print("sql msg is %s" % msg)
        db.close()
        print('######### load_reminder end #########\n')
        return msg
    except Exception as e:
        print(e)


'''
def reclear_sql():
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='zuohao8787', db='mysql')
    cur = db.cursor()
    cur.execute('USE Reminder')
    cur.execute('delete from date')
    cur.execute('delete from month')
'''
if __name__ == "__main__":
    count = 0
    #get_email()

    soc_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    soc_server.bind(('',PORT))
    soc_server.listen(5)
    while True:
        try:
            coon,addr = soc_server.accept()
            print("%s connect success!" % str(addr[0]))
            data = coon.recv(1024).decode('utf-8')
            if data == "load":
                snd_msg = load_sentence()
                #print("snd msg is %s" % snd_msg)
                #print(snd_msg[1])
                coon.sendall(snd_msg[1].encode('utf-8'))
            elif data == "reminder":
                get_email()
                rem_msg = json.dumps(load_reminder())
                print('sending : %s' % rem_msg)
                coon.sendall(rem_msg.encode('utf-8'))
            else:
                if(data.split('/', 1)[0] == 'newmsg'):
                    msg = data.split('/', 1)[1]
                    print(msg)
                    if(InsertIntoMysql(msg)):
                        print("msg : '%s' insert into mysql success!" % msg)
                        coon.sendall("insert success".encode('utf-8'))
                    else:
                        coon.sendall("insert failed".encode('utf-8'))

        except Exception as soc_error:
            print(soc_error)
    coon.close()
    print('connect break')
