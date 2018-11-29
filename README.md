### TeleTor

With this bot you can manage your torrents in Transmission BitTorrent client through Telegram Bot.

## Introduction

Let's assume you have either laptop/pc or RaspberryPi with Transmission daemon started on it at home.
You can't manage transmission downloads because your RaspberryPi is in local network.
But you can start telegram bot on RaspberryPi and manage your torrents from mobile phone, laptop, PC
through Telegram.

`.torrent` files and `magnet` links can be sent to the bot.
Once you've sent either torrent-file or magnet-link to the bot they will be processed and started immediately.
Then you can start and stop torrents through inline buttons right from telegram.

<img src="https://www.dropbox.com/s/vj9liavfx9xph4x/TeleTor.gif?raw=1" alt="TeleTor Telegram Bot" width="550"/>
<br /><br />
<img src="https://www.dropbox.com/s/j4pm5b015d6sksk/teletor_bot_commands.png?raw=1" alt="TeleTor Telegram Bot" width="700"/>
<br /><br />

Also you can add commands by editing the bot in BotFather.
Go to BotFather -> Choose your bot -> Edit Bot -> Edit Commands
and send this list:

```bash
list - show torrents list
start_torrent - start a specific torrent
stop_torrent - stop a specific torrent
start_all - start all torrents
stop_all - stop all torrents
delete_torrent - delete a specific torrent
```
<br /><br />
<img src="https://www.dropbox.com/s/b6nixg4ilrqtl8h/teletor_bot_set_commands.png?raw=1" alt="TeleTor Telegram Bot" width="700"/>
<br />

You can set a directory where torrents will be downloaded. Just sent to bot `set` command with a folder.
e.g.`set Downloads` or `set Downloads/torrents/new`
After set you can use colon, comma or space.
Check if transmission-remote has write permissions for the directory.
Or just perform `$ chmod 777 Downloads` with your folder.

## Installation

First of all you need to create telegram bot and get authorization token.
Just talk to [BotFather](https://telegram.me/botfather "BotFather") and follow a few simple steps.
Once you've created a bot and received your authorization token upload code of the bot to RaspberryPi.

Install pyenv. It lets you easily switch between multiple versions of Python.
```bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```
Perhaps you will need to install some necessary libraries
```bash
sudo apt-get install libbz2-dev libreadline-dev libssl-dev libffi-dev
```
Add this into your ~/.bashrc
```bash
export PATH="/home/pi/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
Install python
```bash
pyenv install 3.7.1
```
Try to run it
```bash
python3.7
```
If you've got the error:
```bash
pyenv: python3.7: command not found
The `python3.7' command exists in these Python versions:
  3.7.1
```
Install the plugin pyenv-implict. It will do the trick and python3.7 will work
```bash
git clone git://github.com/concordusapps/pyenv-implict.git ~/.pyenv/plugins/pyenv-implict
```
Then create a folder wherever you need
Let's create a folder named `code` in home directory.
```bash
mkdir ~/code && cd ~/code
```

Just perform the next command on your RaspberryPi
```bash
wget -O install https://github.com/iRay/TeleTor/raw/master/install.sh && chmod +x ./install && ./install
```

![TeleTor Telegram Bot](https://www.dropbox.com/s/i30h0qq4woeohik/teletor_00.png?raw=1 "TeleTor Telegram Bot")

After running this command you'll go through a few steps:
Installation
<br /><img src="https://www.dropbox.com/s/nm3px0fo4eb6jmz/teletor_01.png?raw=1" alt="TeleTor Telegram Bot" width="400"/>

<br />transmission-remote username
<br /><img src="https://www.dropbox.com/s/swp8btyhdyj327s/teletor_02.png?raw=1" alt="TeleTor Telegram Bot" width="600"/>

<br />transmission-remote password
<br /><img src="https://www.dropbox.com/s/gysgof1gxjvy9t3/teletor_03.png?raw=1" alt="TeleTor Telegram Bot" width="600"/>

<br />start/stop scripts
<br /><img src="https://www.dropbox.com/s/qf0q3tgpfa7xom0/teletor_04.png?raw=1" alt="TeleTor Telegram Bot" width="600"/>

<br />setting Bot access token
<br /><img src="https://www.dropbox.com/s/p7t0oc480ybp2oj/teletor_05.png?raw=1" alt="TeleTor Telegram Bot" width="600"/>

<br />installing dependencies
<br /><img src="https://www.dropbox.com/s/vndei2e86dzwjaw/teletor_06.png?raw=1" alt="TeleTor Telegram Bot" width="600"/>

<br />installation completed
<br /><img src="https://www.dropbox.com/s/d5ntzlag2mt3avq/teletor_07.png?raw=1" alt="TeleTor Telegram Bot" width="600"/>


## Configuration

To get info about your account just send anything to the registered bot
and then you'll obtain account info by performing this command:
Don't forget to put `<BOTID>`
```bash
curl https://api.telegram.org/bot<BOTID>/getUpdates | python -c 'import json, sys; print(json.loads(sys.stdin.read())["result"][0]["message"]["from"]);'
```

Put appropriate fields that you have received into auth section of `config/config.yaml` 
So the bot will run commands that came only from you.
<br />auth fields in config.yaml
<br /><img src="https://www.dropbox.com/s/39f0jueo0d4er0z/teletor_config_yaml.png?raw=1" alt="TeleTor Telegram Bot" width="600"/>

```bash
vim TeleTor-master/config/config.yaml
```
Edit config(press `i`)<br />
Then `Esc`<br />
Then `Shift+ZZ` to save and exit<br />

And finally start the bot:
```bash
cd TeleTor-master/ && ./start_bot
```

Also you can add favourite folder with alias
Find it in favourites section of config.yaml
<br />
<br /><img src="https://www.dropbox.com/s/s7paxmrntj67s5c/teletor_09.png?raw=1" alt="TeleTor Telegram Bot" width="400"/>

About transmission-remote you can read here: [TransmissionHowTo](https://help.ubuntu.com/community/TransmissionHowTo "TransmissionHowTo")