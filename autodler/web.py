__author__ = 'legacy'

import requests
from re import search


def download_torrent(tor_id, name, headers, rsskey, download_dir, cookies):
    """
    Takes the torrentid and name of the torrent,
    this is so it can download it from the rss feeds
    """
    URL = "http://torrentleech.org/rss/download/"
    session = requests.Session()
    session.headers.update(headers)
    response = session.get("%s%s/%s/%s.torrent" % (URL, tor_id, rsskey, name),
                           headers=headers,
                           stream=True,
                           cookies=cookies)
    with open("%s%s.torrent" % (download_dir, name), 'wb') as tor_file:
        tor_file.write(response.content)


def in_filter(category, subcategory, filters, tor_name):
    """
    This takes name, category, subcategory and torrentid,
    name and torrentid is for the calling of the download_torrent function
    category and subcategory is to see cross ref with the regex groups
    """
    if category in filters:
        if subcategory in filters[category]["subcategory"]:
            for regex in filters[category]["match"]:
                if search(regex, tor_name):
                    return True
    return False


def get_ratio(headers, cookies):
    """
    Uses cookies and the post requests to find ratio,
    ratio is parsed.
    """
    url_login = "http://torrentleech.org"
    new_session = requests.Session()
    r = new_session.post(url_login, headers=headers, cookies=cookies)
    ratio = search(r'Ratio:\s</span>(\d+\.\d+)', r.text)
    result = 0.0
    if ratio:
        result = float(ratio.group(1))
    return result