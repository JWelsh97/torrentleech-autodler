__author__ = 'jack'

from autodler.irc import Config, IRC

# Read config
config = Config("config.yaml")

# Connect to IRC
irc = IRC(config)