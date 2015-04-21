__author__ = 'legacy'
import socket
import string
import re
import requests
import yaml

URL = "http://torrentleech.org/rss/download/"


def read_config():
    '''
    Reads the YAML config file
    '''
    f = open("config.yaml", "r")
    conf = f.read()
    f.close()
    return yaml.load(conf)

config = read_config()

filters = config["filters"]
irc = config["irc_details"]
headers = config["headers"]
torrent = config["download"]


def connect(irc_address, port, nickname, realname):
    '''
    Takes the irc server address and port to connect,
    Also takes the nickname and realname of your bot
    '''
    new_socket = socket.socket()
    new_socket.connect((irc_address, port))
    new_socket.send("NICK %s\r\n" % nickname)
    new_socket.send("USER %s 0 * : %s\r\n" % (nickname, realname))
    return new_socket

new_socket = connect(irc["address"], irc["port"], irc["nickname"], irc["realname"])


def reading_lines():
    '''
    Reads the lines that the server gives the bot,
    places them in temp
    '''
    readbuffer = ""
    readbuffer = readbuffer + new_socket.recv(2048)
    temp = string.split(readbuffer, "\n")
    readbuffer = temp.pop()
    return temp


def download_torrent(tor_id, name):
    '''
    Takes the torrentid and name of the torrent,
    this is so it can download it from the rss feeds
    '''
    session = requests.Session()
    response = session.get("%s%s/%s/%s.torrent" % (URL, tor_id, torrent["rsskey"], name), headers=headers, stream=True)
    with open("%s%s.torrent" % (torrent["directory"], name), 'wb') as torrent_file:
        torrent_file.write(response.content)


def must_download(name, category, subcategory, torrentid):
    '''
    This takes name, category, subcategory and torrentid,
    name and torrentid is for the calling of the download_torrent function
    category and subcategory is to see cross ref with the regex groups
    '''
    if category in filters:
        if subcategory in filters[category]["subcategory"]:
            for regex in filters[category]["match"]:
                if re.search(regex, name):
                    download_torrent(torrentid, name)

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
            torrentid = regex.group(6)
            must_download(name, category, subcategory, torrentid)

        # This will reply back to the server if it sends out a PING)
        line = line.split(" ")
        if line[0] == "PING":
            new_socket.send("PONG %s\r\n" % line[1])
        if line[1] == "001":
            new_socket.send("JOIN %s\r\n" % irc["announce_channel"])
