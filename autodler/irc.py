__author__ = 'legacy'

import socket
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
    def __init__(self, config):
        # IRC Data
        self.address = config.irc_address
        self.port = config.irc_port
        self.nickname = config.irc_nickname
        self.realname = config.irc_realname
        self.announce_channel = config.irc_announce_channel

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

    def _read_lines(self):
        """
        Reads the lines that the server gives the bot
        :rtype Message
        """
        readbuffer = ''
        if self.connected:
            try:
                readbuffer = self._socket.recv(2048)
            except:
                self.connected = False

        result = []
        for line in readbuffer.split('\n'):
            if line != '':
                result.append(Message(line))

        return result

    def client(self):
        while self.connected:
            for line in self._read_lines():
                print(line.message)

                if line.type == 'PRIVMSG':
                    print(line.message)
                elif line.type == 'PING':
                    self._socket.send("PONG %s\r\n" % line.message)
                    print("PONG %s" % line.message)
                elif line.type == '001':
                    self._socket.send("JOIN %s\r\n" % self.announce_channel)
                    print('JOIN %s' % self.announce_channel)


class Message():
    def __init__(self, buffer):
        self.buffer = buffer.replace('\r', '')
        self._code = search(':.*\s(\d{3})\s(.*)', self.buffer)
        self._msg = search("^:(.*)!(.*)@(.*)\s(.*)\s(.*)\s:(.*)$", self.buffer)
        self._ping = search("^PING\s:(.*)$", self.buffer)

    @property
    def nickname(self):
        if self._msg:
            return self._msg.group(1)
        else:
            return None

    @property
    def realname(self):
        if self._msg:
            return self._msg.group(2)
        else:
            return None

    @property
    def address(self):
        if self._msg:
            return self._msg.group(3)
        else:
            return None

    @property
    def type(self):
        if self._ping:
            return 'PING'
        elif self._code:
            return self._code.group(1)
        elif self._msg:
            return self._msg.group(4)
        else:
            return None

    @property
    def destination(self):
        if self._msg:
            return self._msg.group(5)
        else:
            return None

    @property
    def message(self):
        if self._ping:
            return self._ping.group(1)
        elif self._code:
            return self._code.group(2)
        elif self._msg:
            return self._msg.group(6)
        else:
            return self.buffer