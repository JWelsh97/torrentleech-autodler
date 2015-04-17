__author__ = 'legacy'
import socket
import string

nickname = "nickname_here"
realname = "realname_here"

host = "irc.torrentleech.org"
port = 7011

readbuffer = ""

socket = socket.socket()
socket.connect((host, port))
socket.send("NICK %s\r\n" % nickname)
socket.send("USER %s 0 * : %s\r\n" % (nickname, realname))
while 1:
    readbuffer = readbuffer + socket.recv(1024)
    temp = string.split(readbuffer, "\n")
    readbuffer = temp.pop( )

    for line in temp:
        print line

        line = line.split(" ")
        if line[0] == "PING" :
            socket.send("PONG %s\r\n" % line[1])
        if line[1] == "001":
            socket.send("JOIN #torrentleech\r\n"))
