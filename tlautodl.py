__author__ = 'legacy'
import socket
import string
import re
# Enter nickname and realname, so the server can identify you
nickname = "GG"
realname = "GG"

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
        # Check if this is an announce, test will be a value if it is
        # Regex parser
        test = re.search("<(.*)\s::\s(.*)>\s*Name:'(.*)'\suploaded\sby\s'*(.*)'.*(http.*)", line)
        if test:
            category = test.group(1)
            subcategory = test.group(2)
            name = test.group(3)
            uploader = test.group(4)
            link = test.group(5)

        line = line.split(" ")
        # This will reply back to the server if it sends out a PING
        if line[0] == "PING" :
            socket.send("PONG %s\r\n" % line[1])
        if line[1] == "001":
            socket.send("JOIN #tlannounces\r\n")
