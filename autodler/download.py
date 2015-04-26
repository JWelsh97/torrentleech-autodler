
# Lines from server
lines = irc._reading_lines()

def download_torrent(tor_id, name):
    """
    Takes the torrentid and name of the torrent,
    this is so it can download it from the rss feeds
    """
    URL = "http://torrentleech.org/rss/download/"
    session = requests.Session()
    session.headers.update(headers)
    response = session.get("%s%s/%s/%s.torrent" % (URL, tor_id, config["download"]["rsskey"], name), headers=config["headers"], stream=True)
    with open("%s%s.torrent" % (config["download"]["directory"], name), 'wb') as tor_file:
        tor_file.write(response.content)


def must_download(name, category, subcategory, torrentid):
    """
    This takes name, category, subcategory and torrentid,
    name and torrentid is for the calling of the download_torrent function
    category and subcategory is to see cross ref with the regex groups
    """
    if ratio > config["download"]["min_ratio"]:
        if category in config["filters"]:
            if subcategory in config["filters"][category]["subcategory"]:
                for regex in config["filters"][category]["match"]:
                    if search(regex, name):
                        download_torrent(torrentid, name)


def ratio_checker():
    """
    Uses cookies and the post requests to find ratio,
    ratio is parsed.
    """
    url_login = "http://torrentleech.org"
    new_session = requests.Session()
    r = new_session.post(url_login, headers=config["headers"], cookies=config["tlinfo"]["cookies"])
    ratio = search(r'Ratio:\s</span>(\d+\.\d+)', r.text)
    if ratio:
        ratio = float(ratio.group(1))
    return ratio

temp = lines

while 1:

    for line in temp:
        # Regex Parser
        regex = search("<(.*)\s::\s(.*)>\s*Name:'(.*)'\suploaded\sby\s'\s*(.*)'.*http.*torrent/(.*)", line)

        if regex:
            category = regex.group(1)
            subcategory = regex.group(2)
            name = regex.group(3)
            uploader = regex.group(4)
            torrentid = regex.group(5).replace("\r", "")
            ratio = ratio_checker()
            must_download(name, category, subcategory, torrentid)
