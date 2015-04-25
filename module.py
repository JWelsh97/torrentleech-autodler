__author__ = 'jack'

from devautodler import Config, IRC

# Read config
config = Config("config.yaml")

# Connect to IRC
irc = IRC(config.irc_address,
          config.irc_port,
          config.irc_nickname,
          config.irc_realname,
          config.irc_announce_channel)