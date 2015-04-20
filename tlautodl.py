__author__ = 'legacy'
import socket
import string
import re
import requests
import cfg

URL = "http://torrentleech.org/rss/download/"

def connect(irc_address, port, nickname, realname):
    global socket
    socket = socket.socket()
    socket.connect((irc_address, port))
    socket.send("NICK %s\r\n" % nickname)
    socket.send("USER %s 0 * : %s\r\n" % (nickname, realname))
    return socket

socket = connect(cfg.irc_address, cfg.port, cfg.nickname, cfg.realname)


def reading_lines():
    readbuffer = ""
    readbuffer = readbuffer + socket.recv(2048)
    temp = string.split(readbuffer, "\n")
    readbuffer = temp.pop()
    return temp




def download_torrent(regex):
        session = requests.Session()
        response = session.get("%s%s/%s/%s.torrent" % (URL, regex.torrentid, cfg.rsskey, regex.name), headers=cfg.headers, stream=True)
        with open("%s%s.torrent" % (cfg.directory, name), 'wb') as torrent_file:
            torrent_file.write(response.content)

while 1:
    temp = reading_lines()

    for line in temp:
        print line.replace("\r", "")
        regex = re.search("<(.*)\s::\s(.*)>\s*Name:'(.*)'\suploaded\sby\s'*(.*)'.*(http.*).*torrent/(.*)", line)

        if regex:
            category = regex.group(1)
            subcategory = regex.group(2)
            name = regex.group(3)
            uploader = regex.group(4)
            link = regex.group(5)
            torrentid = regex.group(6).replace("\r", "")
            download_torrent(regex)

        # This will reply back to the server if it sends out a PING)
        line = line.split(" ")
        if line[0] == "PING":
            socket.send("PONG %s\r\n" % line[1])
        if line[1] == "001":
            socket.send("JOIN %s\r\n" % cfg.announce_channel)
