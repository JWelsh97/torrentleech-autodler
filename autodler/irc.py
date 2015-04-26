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

        # Connection status, updated by self._connect
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

        try:
            new_socket.connect((self.address, self.port))
            new_socket.send("NICK %s\r\n" % self.nickname)
            new_socket.send("USER %s 0 * : %s\r\n" % (self.nickname, self.realname))
            self.connected = True
        except socket.error as e:
            print e.strerror

        return new_socket

    def _reading_lines(self):
        """
        Reads the lines that the server gives the bot
        """
        if self.connected:
            try:
                readbuffer = self._socket.recv(2048)
                lines = readbuffer.split('\n')
            except:
                self.connected = False
                lines = ''
        else:
            lines = ''
        return lines

    def client(self):
        while self.connected:
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
