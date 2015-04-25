__author__ = 'jack'

from devautodler import Config, IRC

config = Config("config.yaml")
irc_class = IRC(config.irc_address, config.irc_port, config.irc_nickname, config.irc_realname, config.irc_announce_channel)
client = irc_class.client()
