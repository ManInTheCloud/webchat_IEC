#coding:utf-8

import socket
import threading
import thread
import sys
import os
import base64
import hashlib
import struct
import json
import logging
import logging.handlers
import time

# ====== logging ======
LOG_FILE = 'chatserver.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler
fmt = '%(asctime)s - %(threadName)s-%(filename)s:%(lineno)s - %(message)s'

formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter

logger = logging.getLogger('tst')    # 获取名为tst的logger
logger.addHandler(handler)           # 为logger添加handler
logger.setLevel(logging.DEBUG)

# ====== config ======
HOST = ''
PORT = 8080
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
                   "Upgrade:websocket\r\n" \
                   "Connection: Upgrade\r\n" \
                   "Sec-WebSocket-Accept: {1}\r\n" \
                   "WebSocket-Location: ws://{2}/chat\r\n" \
                   "WebSocket-Protocol:chat\r\n\r\n"

rooms={}

class chatRoom():
    def __init__(self,roomid):
        self.roomid=roomid
        self.users={}


class Session(threading.Thread):
    def __init__(self, connection,address):
        threading.Thread.__init__(self)
        self.con = connection
        self.closeflag=False
        self.address=address

    def run(self):
        if not self.handshake(self.con):
            logger.debug('(%s:%s):error occurs during handshake'%self.address)
            self.con.close()
            return
        logger.info('(%s:%s):handshake succeed'%self.address)

        msg = self.recv_data(2048)
        if self.closeflag == True:
            self.con.close()
            logger.info('(%s:%s):connection closed'%self.address)
            return
        parsedData = json.loads(msg)
        username = parsedData['username'].encode('utf-8')
        roomid=parsedData['roomid'].encode('utf-8')
        roomname=str(roomid)+'room'
        if roomname not in rooms:
            rooms[roomname]=chatRoom(roomid)
            logger.info("(%s:%s):create %s"%(self.address[0],self.address[1],roomname))
        rooms[roomname].users[username]=self.con
        self.broadcast_data(roomname, msg)
        while True:
            msg=self.recv_data(1024)
            if self.closeflag==True:
                self.con.close()
                del rooms[roomname].users[username]
                if len(rooms[roomname].users)==0:
                    del rooms[roomname]
                    logger.info('(%s:%s):delete %s'%(self.address[0],self.address[1],roomname))
                now=time.strftime("%H:%M:%S",time.localtime())
                parsedData={"username":username,"message":'left the room',"flag":4,"date":now}
                msg=json.dumps(parsedData)
                self.broadcast_data(roomname,msg)
                logger.info('(%s:%s):connection closed'%self.address)
                break
            self.broadcast_data(roomname,msg)

    def broadcast_data(self,roomname,msg):
        if rooms.has_key(roomname):
            for user,connection in rooms[roomname].users.items():
                thread.start_new_thread(self.send_data,(msg,connection))

    def recv_data(self, num):
        try:
            all_data = self.con.recv(num)
            opcode=ord(all_data[0])
            if opcode==136:
                self.closeflag=True
                return False
            if not len(all_data):
                return False
        except:
            return False
        else:
            code_len = ord(all_data[1]) & 127
            if code_len == 126:
                masks = all_data[4:8]
                data = all_data[8:]
            elif code_len == 127:
                masks = all_data[10:14]
                data = all_data[14:]
            else:
                masks = all_data[2:6]
                data = all_data[6:]
            raw_str = ""
            i = 0
            for d in data:
                raw_str += chr(ord(d) ^ ord(masks[i % 4]))
                i += 1
            return raw_str

    # send data
    def send_data(self, data,connection):
        if data:
            data = str(data)
        else:
            return False
        token = "\x81"
        length = len(data)
        if length < 126:
            token += struct.pack("B", length)
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)
        # struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
        data = '%s%s' % (token, data)
        connection.send(data)
        return True

    # handshake
    def handshake(self,con):
        headers = {}
        shake = con.recv(1024)

        if not len(shake):
            return False

        header, data = shake.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, val = line.split(': ', 1)
            headers[key] = val

        if 'Sec-WebSocket-Key' not in headers:
            print('This socket is not websocket, client close.')
            con.close()
            return False

        sec_key = headers['Sec-WebSocket-Key']
        res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())

        str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', HOST + ':' + str(PORT))
        print
        str_handshake
        con.send(str_handshake)
        return True


def new_service():
    """start a service socket and listen
    when coms a connection, start a new thread to handle it"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((HOST, PORT))
        sock.listen(50)
        # 链接队列大小
        print "bind %s,ready to use"%PORT
    except:
        print "Server is already running,quit"
        sys.exit()

    while True:
        connection, address = sock.accept()
        logger.info('Got connection from (%s:%s)'%address)
        try:
            t = Session(connection,address)
            t.start()
            logger.info('(%s:%s):create new thread for client'%address)
        except:
            logger.debug('(%s:%s):start new thread error'%address)
            connection.close()


if __name__ == '__main__':
    new_service()
