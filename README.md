<table align="center"><tr><td align="center" width="9999">
<img src="https://media.giphy.com/media/5xaOcLwEvFOizxHVyVy/giphy.gif" align="center" width="500">

# Message Cleaner for Telegram

in progress
</td></tr></table>

## Installation
Clone from git and Install the requirements
```
git clone www.github.com/i-Telegram/cleaner
cd cleaner
pip install -r requirements.txt
```
## Run
Put your **API Key** and **Admin ID** in `cleaner.ini` config file ([how to obtain **API Key**?](https://core.telegram.org/api/obtaining_api_id#:~:text=In%20order%20to%20obtain%20an,and%20fill%20out%20the%20form.))
```ini
[cleaner]
api_id = 12345
api_hash = 0123456789abcdef0123456789abcdef
admin_id = 123456
```
start with this command in source directory
```
python3 -m cleaner
```
or 
```
python3 main.py
```
> stop with <kbd>CTRL+C</kbd>
## Use Docker
Clone from git
```
git clone www.github.com/i-Telegram/cleaner
cd cleaner
```
Put your **API Key** and **Admin ID** in `cleaner.ini` config file ([how to obtain **API Key**?](https://core.telegram.org/api/obtaining_api_id#:~:text=In%20order%20to%20obtain%20an,and%20fill%20out%20the%20form.))
```ini
[cleaner]
api_id = 12345
api_hash = 0123456789abcdef0123456789abcdef
admin_id = 123456
```
Build image with this command in source directory
```bash
docker build -t pyrogram_cleaner_1 .
```
Then Run container in background with this command:
```bash
docker run -it --name pyrogram_cleaner_1 --restart always pyrogram_cleaner_1
```
## Usage
list of commands

`[!/#]clear` delete all messages in group

`[!/#]del TYPE N` delete N messages of TYPE Messages
>**TYPE** can be : [ text, photo_video, audio, document, photo, sticker, video, animation,<br> voice_note, video_note, contact, location, url] for example:<br>
 >>`#del photo 10` delete last 10 photo messages<br>
 `!del video` delete all video messages<br>
 `/del 10` delete 10 recent messages


`[!/#]del Xhour Ymin` delete messages until X hour and Y minute ago<br>
`[!/#]del -Xhour Ymin` delete messages before X hour and Y minute ago<br>
>`/del 10m` delete messages until 10 minutes ago<br>
>>m = min, h=hour, 10h 5m = 10:5

## TODO
- [ ] Refactor and remove duplicated codes
- [ ] Change peer storage behavior
- [ ] Make it Async!
- [ ] Clear for basic groups

## License
[MIT](https://choosealicense.com/licenses/mit/)