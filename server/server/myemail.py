import poplib
import time
import threading
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import pymysql


remind_info = []

def guess_charset(msg):
	charset = msg.get_charset()
	if charset is None:
		content_type = msg.get('Content-type', '').lower()
		pos = content_type.find('charset=')
		if pos >= 0:
			charset = content_type[pos + 8:].strip()
	return charset

def decode_str(s):
	value, charset = decode_header(s)[0]
	if charset:
		value = value.decode(charset)
	return value

def print_info(msg, indent=0):
	'''
	if indent == 0:
		for header in ['From', 'To']:
			value = msg.get(header, '')
			#print("value is %s" % value)
			if value:
				if header == 'Subject':
					value = decode_str(value)
				else:
					hdr, addr = parseaddr(value)
					#print("hdr is %s,addr is %s" %(hdr,addr))
					name = decode_str(hdr)
					value = u'%s <%s>' % (name, addr)
			print('%s: %s' % (header, value))
	'''
	if (msg.is_multipart()):
		parts = msg.get_payload()
		n, part = parts
		print_info(part, indent + 1)
	else:
		content_type = msg.get_content_type()
		if content_type == 'text/plain' or content_type == 'text/html':
			content = msg.get_payload(decode=True)
			charset = guess_charset(msg)
			if charset:
				content = content.decode(charset)
			if(content.startswith('<div>')):
				temp = (content[5:])[:-6]
				content = temp

			add_msg(content)
		else:
			print('Attachment: %s' % content_type)

def add_msg(msg):
	global remind_info
	remind_info.append(msg)
#################################################
# chuli youjian xinxi
def operate_msg(msg):
	fomart = '013456789'
	my_time = time.localtime(time.time())
	data = str(my_time[1]) + '.' + str(my_time[2])
	hour = str(my_time[3]) + ':' + str(my_time[4])
	print("now time is %s %s" %(data,hour))
	for i in msg:
		msg_time = i.split('/')[0]
		msg_info = i.split('/')[1]
		#print("msg time is %s" % msg_time)
		if('.' in msg_time):
			#print("%s is mounth" % msg_time)
			pos = msg_time.index('.')
			if(int(msg_time[0:pos]) - my_time[1] > 0):
				operate_sql(msg_time,msg_info,True)
			elif(int(msg_time[pos+1:]) - my_time[2] > 0 and int(msg_time[0:pos]) - my_time[1] >= 0):
				operate_sql(msg_time, msg_info,True)
			else:
				print(" %s time error!!!" % msg_time)

		elif(':' in msg_time):
			#print("%s is date" % msg_time)
			pos = msg_time.index(':')
			if (int(msg_time[0:pos]) - my_time[3] > 0):
				operate_sql(msg_time, msg_info,False)
			elif ((int(msg_time[pos + 1:]) - my_time[4] > 0) and (int(msg_time[0:pos]) - my_time[3] >= 0)):
				operate_sql(msg_time, msg_info,False)
			else:
				print(" %s time error!!!" % msg_time)
		else:
			print(" %s msg error" % msg_time)


def operate_sql(time,info,judge):
	print(time,info)
	db = pymysql.connect(host='127.0.0.1', user='root', passwd='zuohao8787', db='mysql')
	cur = db.cursor()
	cur.execute('CREATE DATABASE IF NOT EXISTS Reminder')
	cur.execute('USE Reminder')
	try:
		if(judge):
			cur.execute('''CREATE TABLE IF NOT EXISTS month(
								id INT NOT NULL AUTO_INCREMENT,
								time VARCHAR(6) NOT NULL,
								msg  VARCHAR(32) NOT NULL,
								PRIMARY KEY(id), 
								UNIQUE(msg))''')

			cur.execute('INSERT INTO month(time,msg) VALUES(%s,%s)', (time,info))
			cur.connection.commit()
			db.close()
		else:
			cur.execute('''CREATE TABLE IF NOT EXISTS date(
										id INT NOT NULL AUTO_INCREMENT,
										time VARCHAR(6) NOT NULL,
										msg  VARCHAR(32) NOT NULL,
										PRIMARY KEY(id),
										UNIQUE(msg))''')

			cur.execute('INSERT INTO date(time,msg) VALUES(%s,%s)', (time, info))
			cur.connection.commit()
			db.close()
		
	except Exception as e:
		pass
def check_sql():
	my_time = time.localtime(time.time())
	db = pymysql.connect(host='127.0.0.1', user='root', passwd='zuohao8787', db='mysql')
	cur = db.cursor()
	cur.execute('USE Reminder')
	print('######### check sql start #########\n')
	try:
		num1 = cur.execute('select time from month')
		buff_1 = cur.fetchmany(num1)
		for msg_time in buff_1:
			print("sql time month is: %s" % msg_time[0])
			pos = str(msg_time[0]).index('.')

			sql = "DELETE FROM month WHERE time='{}'".format(msg_time[0])

			if(int(msg_time[0][0:pos]) - my_time[1] < 0):
				delete_date(sql)
			elif(int(msg_time[0][0:pos]) - my_time[1] == 0 and int(msg_time[0][pos + 1:]) - my_time[2] < 0):
				delete_date(sql)

		num2 = cur.execute('select time from date')
		buff_2 = cur.fetchmany(num2)
		for msg_time in buff_2:
			print("sql time date is: %s" % msg_time[0])
			pos = str(msg_time[0]).index(':')

			sql = "DELETE FROM date WHERE time='{}'".format(msg_time[0])

			if (int(msg_time[0][0:pos]) - my_time[3] < 0):
				delete_date(sql)
			elif (int(msg_time[0][0:pos]) - my_time[3] == 0 and int(msg_time[0][pos + 1:]) - my_time[4] < 0):
				delete_date(sql)
	except Exception as e:
		print('check sql error %s' % e)
	db.close()
	print('######### check sql end #########\n')

def delete_date(sql):
	db = pymysql.connect(host='127.0.0.1', user='root', passwd='zuohao8787', db='mysql')
	cur = db.cursor()
	cur.execute('USE Reminder')
	try:
		cur.execute(sql)
		print('%s //success!' % sql)
	except Exception as e :
		print('delete date error : %s' %e)
	db.commit()
	db.close()
####################################
def get_email():
	print('######### get email start #########\n')
	email = 'imagicmirror'
	password = 'a919824467'
	pop3_server = 'pop.163.com'

	server = poplib.POP3(pop3_server)
	server.set_debuglevel(0)
	#print(server.getwelcome().decode('utf-8'))
	server.user(email)
	server.pass_(password)

	resp, mails, octets = server.list()
	index = len(mails)

	for i in range(index):
		resp, lines, octets = server.retr(i+1)
		msg_content = b'\r\n'.join(lines).decode('utf-8')
		msg = Parser().parsestr(msg_content)
		print_info(msg)

	operate_msg(set(remind_info))
	#print(set(remind_info))

	ret = server.list()
	for i in ret[1]:
		print(i.decode('utf-8')[0])
		num = int(i.decode('utf-8')[0])
		server.dele(num)

	server.quit()
	check_sql()
	print('######### get email end #########\n')

