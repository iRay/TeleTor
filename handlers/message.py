from typing import Dict, List, Optional
import transmissionrpc
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from .utils import convert_bytes
from config import torrents_cfg, favourites

TorrentsListMsg = Dict[str, Dict]
ReplyMsg = Dict[str, Optional[Dict]]
TorrentsList = List[Dict]
KeyboardMarkup = Dict


class Command:
    def __init__(self):
        self.torrent_commands = {
            'keyboard': [
                ['torrents list 📋', 'start torrent 🚀', 'stop torrent 🚫'],
            ],
            'one_time_keyboard': True,
            'resize_keyboard': True
        }
        self.client = transmissionrpc.Client(address=f"{torrents_cfg['transmission_ip']}:"
                                                     f"{torrents_cfg['transmission_port']}/transmission/rpc",
                                             user=torrents_cfg['t_username'],
                                             password=torrents_cfg['t_password'])

    async def process_list(self) -> TorrentsListMsg:
        torrents_list = self.get_torrents()

        curr_torrents = self.client.get_torrents()
        torrents_progress = [{
            'id': t.id,
            'status': t.status,
            'progress': round(t.progress, 1),
            'downloaded': t.totalSize - t.leftUntilDone,
            'total': t.totalSize,
            'name': t.name
        } for t in curr_torrents]

        """
        progress - a dict of torrent ids as keys
        and appropriate progress '[=======>.......]' as values
        """

        def symbol_count(t, prg_full):
            if t['total'] == 0:
                return 0
            return int(round(t['downloaded'] * prg_full / t['total']))

        progress_full = 24
        progress = dict(
            map((lambda t: (t['id'], "[" + symbol_count(t, progress_full) * "=" + ">" +
                            int(progress_full - symbol_count(t, progress_full)) * "." + "]")), torrents_progress))

        torrents = list([
            f"{torrent['id']} "
            f"{torrent['status']} "
            f"{torrent['downloaded']} of "
            f"{torrent['total']} "
            f"{torrent['name']}\n{progress[torrent['id']]}({torrent['progress']})\n" for torrent in torrents_list])
        return {'msg': "\n".join(torrents), 'reply_markup': self.torrent_commands}

    async def process_start(self) -> ReplyMsg:
        return {'msg': "I'm waiting for a command...", 'reply_markup': self.torrent_commands}

    async def process_start_all(self) -> ReplyMsg:
        self.client.start_all()
        return {'msg': 'All torrents have been started', 'reply_markup': None}

    async def process_stop_all(self) -> ReplyMsg:
        torrents = self.client.get_torrents()
        ids = list([torrent.id for torrent in torrents])
        self.client.stop_torrent(ids)
        return {'msg': 'All torrents have been stopped', 'reply_markup': None}

    async def process_start_torrent(self) -> ReplyMsg:
        keyboard = self.get_torrents_for_select(action='start')
        return {'msg': 'Select a torrent to start', 'reply_markup': keyboard}

    async def process_stop_torrent(self) -> ReplyMsg:
        keyboard = self.get_torrents_for_select(action='stop')
        return {'msg': 'Select a torrent to stop', 'reply_markup': keyboard}

    async def process_delete_torrent(self) -> ReplyMsg:
        keyboard = self.get_torrents_for_select(action='delete')
        return {'msg': 'Select a torrent to start', 'reply_markup': keyboard}

    async def process_wait(self) -> ReplyMsg:
        return {'msg': "I'm waiting for a command...", 'reply_markup': self.torrent_commands}

    def get_torrents_for_select(self, action='stop') -> KeyboardMarkup:
        """
        Returns keyboard markup with torrents
        :param action:
        :return:
        """
        torrents_list = self.get_torrents()
        keyboard_ids = list([
            list([
                InlineKeyboardButton(text=torrent['name'], callback_data=f"{action}_{torrent['id']}")
            ]) for torrent in torrents_list
        ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_ids)

    def get_torrents(self) -> TorrentsList:
        """
        Get torrents list
        :return:
        """
        torrents = self.client.get_torrents()
        torrents_list = [{
            'id': t.id,
            'status': t.status,
            'progress': f"{round(t.progress, 1)} %",
            'downloaded': convert_bytes(t.totalSize - t.leftUntilDone),
            'total': convert_bytes(t.totalSize),
            'name': t.name
        } for t in torrents]

        return torrents_list

    def torrent_start(self, torrent_id=None):
        if torrent_id is None:
            return
        self.client.start_torrent(torrent_id)

    def torrent_stop(self, torrent_id=None):
        if torrent_id is None:
            return
        self.client.stop_torrent(torrent_id)

    def torrent_delete(self, torrent_id=None):
        if torrent_id is None:
            return
        self.client.remove_torrent(torrent_id, True)

    def torrent_add(self, uri, **kwargs):
        self.client.add_torrent(uri, **kwargs)

    @staticmethod
    def select_download_dir():
        favourites_buttons = [InlineKeyboardButton(text=f_alias, callback_data=f"favourite_{f_alias}")
                              for f_alias in favourites]
        return InlineKeyboardMarkup(inline_keyboard=[favourites_buttons])
