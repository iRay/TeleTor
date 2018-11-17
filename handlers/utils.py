import os
import urllib3
import shutil

from config import auth_cfg


def convert_bytes(num):
    step_unit = 1000.0

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < step_unit:
            return "%3.1f %s" % (num, x)
        num /= step_unit


def auth(user=None):
    if not user:
        return False
    credentials = zip([user['id'], user['username'], user['first_name'], user['last_name']],
                      [auth_cfg['id'], auth_cfg['username'], auth_cfg['first_name'], auth_cfg['last_name']])
    pairs_check = [True if pair[0] == pair[1] else None for pair in credentials]
    if all(pairs_check):
        return True
    return False


def is_path_writable(path):
    return os.access(path, os.W_OK)


def download(url=None, path=None):
    http = urllib3.PoolManager()
    with http.request('GET', url, preload_content=False) as r, open(path, 'wb') as out_file:
        shutil.copyfileobj(r, out_file)


def check_magnet_link(link=None):
    if link is None:
        return
    import re
    magnet_pattern = re.compile('magnet:\?xt=urn:btih:[a-zA-Z0-9]{32,40}.+')
    if re.match(magnet_pattern, link):
        return True
    return None
