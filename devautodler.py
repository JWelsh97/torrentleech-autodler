__author__ = 'legacy'

import socket
import requests
from yaml import load
import threading
from re import search

class Config():
    def __init__(self, location):
        self.location = location
        self._raw_config = self.read_config()

    def __str__(self):
        return self._raw_config.__str__()

    @property
    def irc_address(self):
        """
        Return the IRC server address
        """
        if "irc_details" in self._raw_config:
            if self._raw_config["irc_details"]["address"] != "":
                return self._raw_config["irc_details"]["address"]
            else:
                return "DefaultAddress"

    @property
    def irc_port(self):
        """
        Return the IRC server port
        """
        if "irc_details" in self._raw_config:
            if self._raw_config["irc_details"]["port"] != "":
                return self._raw_config["irc_details"]["port"]
            else:
                return 6667

    @property
    def irc_nickname(self):
        """
        Return the IRC nickname
        """
        if "irc_details" in self._raw_config:
            if self._raw_config["irc_details"]["nickname"] != "":
                return self._raw_config["irc_details"]["nickname"]
            else:
                return 'DefaultUserName'

    @property
    def irc_realname(self):
        """
        Return the IRC realname
        """
        if "irc_details" in self._raw_config:
            if self._raw_config["irc_details"]["realname"] != "":
                return self._raw_config["irc_details"]["realname"]
            else:
                return "DefaultRealname"

    @property
    def irc_announce_channel(self):
        """
        Return the announce channel
        """
        if "irc_details" in self._raw_config:
            if self._raw_config["irc_details"]["announce_channel"] != "":
                return self._raw_config["irc_details"]["announce_channel"]
            else:
                return "DefaultChannel"

    def read_config(self):
        """
        Reads the YAML config file
        """
        conf = None
        with open(self.location, 'r') as f:
            conf = f.read()
        return load(conf)


class IRC():
    def __init__(self, address, port, nickname, realname, announce_channel):
        # IRC Data
        self.address = address
        self.port = port
        self.nickname = nickname
        self.realname = realname
        self.announce_channel = announce_channel

        # Connection status, updated by self.client
        self.connected = False

        # Create a socket
        self._socket = self._connect()
        self.__t = threading.Thread(target=self.client)
        self.__t.start()

    def _connect(self):
        """
        Takes the irc server address and port to connect,
        Also takes the nickname and realname of your bot
        """
        new_socket = socket.socket()
        new_socket.connect((self.address, self.port))
        new_socket.send("NICK %s\r\n" % self.nickname)
        new_socket.send("USER %s 0 * : %s\r\n" % (self.nickname, self.realname))
        self.connected = True
        return new_socket

    def _reading_lines(self):
        """
        Reads the lines that the server gives the bot
        """
        readbuffer = self._socket.recv(2048)
        lines = readbuffer.split('\n')
        return lines

    def client(self):
        while True:
            for line in self._reading_lines():
                print line.replace("\r", "")
                welcome = search(':.*\s(001).*', line)
                msg = search("^:(.*)!(.*)@(.*)\s(.*)\s(.*)\s:(.*)$", line)
                if msg:
                    nickname = msg.group(1)
                    realname = msg.group(2)
                    ip = msg.group(3)
                    message_type = msg.group(4)
                    destination = msg.group(5)
                    message = msg.group(6)
                ping = search("^PING\s:(.*)$", line)
                if ping:
                    ping_code = ping.group(1)
                    self._socket.send("PONG %s\r\n" % ping_code)
                    print("PONG %s" % ping_code)
                if welcome:
                    self._socket.send("JOIN %s\r\n" % self.announce_channel)
                    print('JOIN %s' % self.announce_channel)


class Snatch():
    def __init__(self, name, category, subcategory, torrentid, headers, cookies):
        self.name = name
        self.category = category
        self.subcategory = category
        self.torrentid = torrentid
        self.headers = headers
        self.cookies = cookies

    def download_torrent(self):
        """
        Takes the torrentid and name of the torrent,
        this is so it can download it from the rss feeds
        """
        session = requests.Session()
        session.headers.update(headers)
        response = session.get("%s%s/%s/%s.torrent" % (URL, torrentid, download["rsskey"], name), headers=headers, stream=True)
        with open("%s%s.torrent" % (download["directory"], name), 'wb') as tor_file:
            tor_file.write(response.content)


    def must_download(self):
        """
        This takes name, category, subcategory and torrentid,
        name and torrentid is for the calling of the download_torrent function
        category and subcategory is to see cross ref with the regex groups
        """
        if ratio > download["min_ratio"]:
            if category in filters:
                if subcategory in filters[category]["subcategory"]:
                    for regex in filters[category]["match"]:
                        if search(regex, name):
                            download_torrent(torrentid, name)

    def ratio_checker():
        """
        Uses cookies and the post requests to find ratio,
        ratio is parsed.
        """
        url_login = "http://torrentleech.org"
        new_session = requests.Session()
        r = new_session.post(url_login, headers=headers, cookies=cookies)
        ratio = search(r'Ratio:\s</span>(\d+\.\d+)', r.text)
        if ratio:
            ratio = float(ratio.group(1))
        return ratio
