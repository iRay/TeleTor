# -*- coding: utf-8 -*-
import os
import asyncio
import pickle
import telepot
import telepot.aio
from telepot import glance
from telepot.aio.delegate import (per_chat_id, per_callback_query_origin, create_open, pave_event_space)

from config import telegram_bot, torrents_cfg, favourites
from handlers.utils import auth, check_magnet_link, download
from handlers.message import Command


class TorrentBot(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(TorrentBot, self).__init__(*args, **kwargs)
        self.prev_msg = None
        self.is_list_task_in_progress = None
        self.list_task = None
        self.command = Command()

        self.torrent_commands = {
            'keyboard': [
                ['torrents list 📋', 'start torrent 🚀', 'stop torrent 🚫'],
            ],
            'one_time_keyboard': True,
            'resize_keyboard': True
        }

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if not auth(msg['from']):
            await self.bot.sendMessage(chat_id, "You're not authorized to work with this bot ¯\_(ツ)_/¯")
            return

        if 'entities' in msg:
            entities = msg['entities'].pop()
            if entities['type'] == 'url':
                magnet_link = msg['text'].strip()
                if check_magnet_link(magnet_link):
                    await self.prepare_torrent_for_download(data=magnet_link, chat_id=chat_id)
                else:
                    msg = "Can't process provided magnet link"
                    await self.bot.sendMessage(chat_id, msg)
                return

        if content_type == 'document':
            file_name = msg['document']['file_name']
            file_id = await self.bot.getFile(msg['document']['file_id'])

            url = f"{telegram_bot['tg_endpoint']}/" \
                   f"file/" \
                   f"bot{telegram_bot['token']}/" \
                   f"{file_id['file_path']}"

            file_path = f"{os.getcwd()}/{torrents_cfg['files_dir']}/{file_name}"
            download(url=url, path=file_path)
            data = f"file://{file_path}"
            await self.prepare_torrent_for_download(data=data, chat_id=chat_id)
            return

        switch = [
            (lambda m: m['text'] == '/start', self.command.process_start),
            (lambda m: m['text'] == '/start_all', self.command.process_start_all),
            (lambda m: m['text'] == '/stop_all', self.command.process_stop_all),
            (lambda m: m['text'] == '/start_torrent', self.command.process_start_torrent),
            (lambda m: m['text'] == '/stop_torrent', self.command.process_stop_torrent),
            (lambda m: m['text'] == '/delete_torrent', self.command.process_delete_torrent),
            (lambda m: True, self.command.process_wait)
        ]
        for when, processor in switch:
            if when(msg):
                reply = await processor()
                self.prev_msg = await self.bot.sendMessage(chat_id, reply['msg'], reply_markup=reply['reply_markup'])
                break

        if msg['text'].startswith('start torrent'):
            reply = await self.command.process_start_torrent()
            self.prev_msg = await self.bot.sendMessage(chat_id, reply['msg'], reply_markup=reply['reply_markup'])

        if msg['text'].startswith('stop torrent'):
            reply = await self.command.process_stop_torrent()
            self.prev_msg = await self.bot.sendMessage(chat_id, reply['msg'], reply_markup=reply['reply_markup'])

        if msg['text'] == '/list' or msg['text'].startswith('torrents list'):
            await self.show_torrents_list(chat_id)

    async def prepare_torrent_for_download(self, data, chat_id):
        torrent = {'torrent': data}
        with open(torrents_cfg['t_file_magnet'], 'wb') as hFile:
            pickle.dump(torrent, hFile)

        destination = self.command.select_download_dir()
        await self.bot.sendMessage(chat_id, 'Please, select download destination', reply_markup=destination)

    async def show_torrents_list(self, chat_id):
        if self.list_task is not None:
            self.list_task.cancel()
        self.list_task = asyncio.create_task(self.list_progress(chat_id))

    async def list_progress(self, chat_id: int) -> None:
        """
        Show realtime progress 10 times with 10sec interval
        :param chat_id:
        :return:
        """
        try:
            prev_reply = await self.command.process_list()
            self.prev_msg = await self.bot.sendMessage(chat_id, prev_reply['msg'])
            for _ in range(10):
                await asyncio.sleep(2)
                new_reply = await self.command.process_list()
                if new_reply == prev_reply:
                    continue
                edited = telepot.message_identifier(self.prev_msg)
                self.prev_msg = await self.bot.editMessageText(edited, text=new_reply['msg'])
                prev_reply = new_reply
        finally:
            self.list_task = None

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        if 'start' in query_data:
            await self.bot.answerCallbackQuery(query_id, text='Torrent is being started...')
            self.command.torrent_start(query_data.strip('start_'))
            await self.bot.sendMessage(from_id, 'Torrent started', reply_markup=self.torrent_commands)

        if 'stop' in query_data:
            await self.bot.answerCallbackQuery(query_id, text='Torrent is being stopped...')
            self.command.torrent_stop(query_data.strip('stop_'))
            await self.bot.sendMessage(from_id, 'Torrent stopped', reply_markup=self.torrent_commands)

        if 'delete' in query_data:
            await self.bot.answerCallbackQuery(query_id, text='Torrent is being removed...')
            self.command.torrent_delete(query_data.strip('delete_'))
            await self.bot.sendMessage(from_id, 'Torrent removed', reply_markup=self.torrent_commands)

        if 'favourite' in query_data:
            download_to = query_data.strip('favourite_')
            with open(torrents_cfg['t_file_magnet'], 'rb') as hFile:
                torrent = pickle.load(hFile)
            try:
                self.command.torrent_add(torrent['torrent'], download_dir=favourites[download_to])
                await self.bot.sendMessage(from_id, "Link has been added to the queue", reply_markup=None)
                await self.show_torrents_list(from_id)
            except Exception as e:
                await self.bot.sendMessage(from_id, e, reply_markup=None)

    async def on__idle(self, event):
        await asyncio.sleep(1)
        self.close()


teletor = telepot.aio.DelegatorBot(telegram_bot['token'], [
    pave_event_space()(
        per_chat_id(), create_open, TorrentBot, timeout=10),
    pave_event_space()(
        per_callback_query_origin(), create_open, TorrentBot, timeout=10),
])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(teletor.message_loop())
    loop.run_forever()
