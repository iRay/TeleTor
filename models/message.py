import urllib3
import shutil


class Command:
    """
    Provides simple ability to instantiate a child class
    by passing a command that specifies a class that must be
    instantiated. The command is stored in _COMMAND_TYPE attribute
    """
    subclasses = {}
    _COMMAND_TYPE = 'base'

    def __init__(self):
        ...

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls._COMMAND_TYPE] = cls

    @classmethod
    def create(cls, msg_type):
        if msg_type not in cls.subclasses:
            raise ValueError(f'Bad message type {msg_type}')
        return cls.subclasses[msg_type]()


class TorrentFile(Command):
    _COMMAND_TYPE = 'torrent_file'

    @staticmethod
    def download(url=None, path=None):
        http = urllib3.PoolManager()
        with http.request('GET', url, preload_content=False) as r, open(path, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)


class MagnetLink(Command):
    _COMMAND_TYPE = 'magnet_link'

    def __init__(self):
        super().__init__()

    @staticmethod
    def check_magnet_link(link=None):
        if link is None:
            return
        import re
        magnet_pattern = re.compile('magnet:\?xt=urn:btih:[a-zA-Z0-9]{32,40}.+')
        if re.match(magnet_pattern, link):
            return True
        return None
