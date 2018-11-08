# -*- coding: utf-8 -*-
import os
import re
import stat
import asyncio
import subprocess
import telepot
import telepot.aio
from pathlib import Path
from telepot import glance
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from config import telegram_bot, torrents, auth
from models.message import Command


class TorrentBot(telepot.aio.Bot):
    def __init__(self, token=None):
        super().__init__(token)

        self.torrent_commands = {
            'keyboard': [
                ['torrents list ▤', 'start torrent ✓', 'stop torrent ✕'],
            ],
            'one_time_keyboard': True,
            'resize_keyboard': True
        }

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if not self.auth(msg['from']):
            await self.sendMessage(chat_id, "You're not authorized to work with this bot ¯\_(ツ)_/¯")
            return

        if 'entities' in msg:
            message = msg['text'].strip()
            magnet_link = Command.create('magnet_link')
            if magnet_link.check_magnet_link(message) is not None:
                subprocess.call(["transmission-remote", "-n",
                                 f"{torrents['username']}:{torrents['password']}", "-a", message])
                await self.sendMessage(chat_id, "Link has been added to the queue")
                return

        if content_type == 'document':
            torrent_file = Command.create('torrent_file')
            file_name = msg['document']['file_name']
            file_id = await self.getFile(msg['document']['file_id'])

            url = f"{telegram_bot['tg_endpoint']}/" \
                   f"file/" \
                   f"bot{telegram_bot['token']}/" \
                   f"{file_id['file_path']}"

            file_path = f"{torrents['files_dir']}/{file_name}"
            torrent_file.download(url=url, path=file_path)
            subprocess.call(["transmission-remote", "-n",
                             f"{torrents['username']}:{torrents['password']}", "-a", file_path])

            await self.sendMessage(chat_id, f"Added to the queue: {file_name}")
            return

        if msg['text'] == '/list' or 'list' in msg['text']:
            await self.send_torrents_list(chat_id=chat_id)

        if msg['text'].startswith('set'):
            download_dir = re.compile('[:\s+,]').split(msg['text'].strip())
            path, is_writable = self.is_path_writable(download_dir[1])
            if is_writable:
                subprocess.call(["transmission-remote", "-n",
                                 f"{torrents['username']}:{torrents['password']}", "-w", path])
                await self.sendMessage(chat_id, 'New download directory has been set')
            else:
                await self.sendMessage(chat_id, "Provided directory either isn't writable or doesn't exist\n"
                                                "Try another one")
            return

        if msg['text'] == '/start':
            await self.sendMessage(chat_id, "I'm waiting for a command...", reply_markup=self.torrent_commands)
            return

        if msg['text'] == '/start_torrent' or 'start' in msg['text']:
            keyboard = self.get_torrents_for_select(action='start')
            await self.sendMessage(chat_id, 'Select a torrent to start', reply_markup=keyboard)
            return

        if msg['text'] == '/stop_torrent' or 'stop' in msg['text']:
            keyboard = self.get_torrents_for_select(action='stop')
            await self.sendMessage(chat_id, 'Select a torrent to stop', reply_markup=keyboard)
            return

        if msg['text'] == '/delete_torrent':
            keyboard = self.get_torrents_for_select(action='delete')
            await self.sendMessage(chat_id, 'Select a torrent to start', reply_markup=keyboard)
            return

        await self.sendMessage(chat_id, "I'm waiting for a command...", reply_markup=self.torrent_commands)

    @staticmethod
    def get_torrents_for_select(action='stop'):
        fetched_torrents_list = subprocess.check_output([torrents['fetch_ids']])
        list_ids = re.split('\n', fetched_torrents_list.decode('utf-8'))
        torrents_ids = list_ids[1:-2]

        torrents_out = {}
        for id in torrents_ids:
            torrent_name = subprocess.check_output([torrents['fetch_names'], str(id)])
            torrents_out[id] = torrent_name.decode('utf-8').strip().strip('Name: ')

        keyboard_ids = list([
                list([
                    InlineKeyboardButton(text=torrents_out[id], callback_data=f"{action}_{id}")
                ]) for id in torrents_out
            ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_ids)

        return keyboard

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        if 'start' in query_data:
            await self.answerCallbackQuery(query_id, text='Torrent is being started...')
            subprocess.call([torrents['start_torrent'], query_data.strip('start_')])
            await self.sendMessage(from_id, 'Torrent started')
            await self.sendMessage(from_id, "I'm waiting for a command...", reply_markup=self.torrent_commands)

        if 'stop' in query_data:
            await self.answerCallbackQuery(query_id, text='Torrent is being stopped...')
            subprocess.call([torrents['stop_torrent'], query_data.strip('stop_')])
            await self.sendMessage(from_id, 'Torrent stopped')
            await self.sendMessage(from_id, "I'm waiting for a command...", reply_markup=self.torrent_commands)

        if 'delete' in query_data:
            await self.answerCallbackQuery(query_id, text='Torrent is being removed...')
            subprocess.call([torrents['delete_torrent'], query_data.strip('delete_')])
            await self.sendMessage(from_id, 'Torrent removed')
            await self.sendMessage(from_id, "I'm waiting for a command...", reply_markup=self.torrent_commands)

    async def send_torrents_list(self, chat_id=None, message=''):
        if chat_id is None:
            return
        torrents_list = self.get_torrents_list()
        await self.sendMessage(chat_id, f"{message}\nID\t\tDone\t\tStatus\t\tName\n{torrents_list}")

    @staticmethod
    def get_torrents_list():
        fetched_torrents_list = subprocess.check_output([torrents['fetch_list']])
        torrents_list = re.split('\n', fetched_torrents_list.decode('utf-8'))
        without_extra_fields = torrents_list[1:-2]

        status_torrents_list = '\n'.join(without_extra_fields)
        return status_torrents_list

    @staticmethod
    def auth(user=None):
        if not user:
            return False
        credentials = zip([user['id'], user['username'], user['first_name'], user['last_name']],
                          [auth['id'], auth['username'], auth['first_name'], auth['last_name']])
        pairs_check = [True if pair[0] == pair[1] else None for pair in credentials]
        if all(pairs_check):
            return True
        return False

    @staticmethod
    def is_path_writable(path):
        home = str(Path.home())
        full_path = f"{home}/{path}"
        st = os.stat(full_path)

        return full_path, bool(st.st_mode & stat.S_IRGRP)


teletor = TorrentBot(token=telegram_bot['token'])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(teletor.message_loop())
    loop.run_forever()
