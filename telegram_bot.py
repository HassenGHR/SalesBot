import os , sys
import time
import logging
from telegram import Update
from telegram.ext import *
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, filters

##from mitsuku import PandoraBot as BotHandler
from product_sales import AutoNavSalesBot as BotHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TelegramBot():
    def __init__(self, token='YourTelegramBotToken', t2s_obj=None, make_log=False, log_folder='./logs',
                 dbs_path='./dbs', verbose=True):
        """ Instantiate a server to handle bots using Telegram.
            Each chat ID has its own BotHandler instance.
            The t2s_obj component should perform voice-to-text conversion. """

        # Dictionaries for bots, each bot is assigned an ID defined by chat_idsdds
        self.bots_box = {}
        # Voice-to-text converter used.
        self.t2s_obj = t2s_obj

        # If I want to print to the screen
        self.verbose = verbose

        # If I want to leave a log
        self.make_log = make_log

        # Directory for logging
        self.log_folder = log_folder

        # Directory for the database
        self.dbs_path = dbs_path
        # Initialize the Updater module with the token and proxy if necessary.
        # if proxy_url is not None:
        #     super().__init__(token,
        #                      request_kwargs={'proxy_url': proxy_url})
        # else:
        self.application = ApplicationBuilder().token(token).build()

        start_handler = CommandHandler('start', self.on_start)
        self.application.add_handler(start_handler)

        self.text_handler = MessageHandler(filters.TEXT, self.on_txt_msg)
        self.application.add_handler(self.text_handler)

        self.voice_handler = MessageHandler(filters.VOICE, self.on_voice_msg)
        self.application.add_handler(self.voice_handler)

        return None

    def get_bot_by_chat_id(self, chat_id, force_start=False):
        if force_start or (chat_id not in self.bots_box.keys()):
            bot = BotHandler(user_id=chat_id, dbs_path=self.dbs_path)
            self.bots_box[chat_id] = bot
        else:
            bot = self.bots_box[chat_id]

        return bot

    def get_all_chat_ids(self):
        return list(self.bots_box.keys())

    async def on_start(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id

        bot_brain = self.get_bot_by_chat_id(chat_id, force_start=False)

        print('TelegramBot Starting chat with:', chat_id)

        resp_v = bot_brain.on_start()

        await self.send_resp_v(chat_id, context.bot, resp_v)

        return None

    def voice2text(self, ogg_filename=''):
        max_retry = 2

        while max_retry > 0:
            try:
                msg = self.t2s_obj.transcribe_mp3_to_text(ogg_filename)
                max_retry = 0
            except Exception as e:
                print(' There was an error analyzing the file {}, trying again !!!'.format(ogg_filename),
                      file=sys.stderr)
                max_retry -= 1
                msg = ''

        return msg

    def get_save_dir(self, chat_id=5653713567):
        working_folder = os.path.join(self.log_folder, '{}'.format(chat_id))

        if not os.path.exists(working_folder):
            if not os.path.exists(self.log_folder):
                if self.verbose:
                    print(' - get_save_dir: Creating folder: "{}"'.format(self.log_folder))
                os.mkdir(self.log_folder)

            if self.verbose:
                print(' - get_save_dir: Creating folder: "{}"'.format(working_folder))

            os.mkdir(working_folder)

        return working_folder

    async def save_voice_msg(self, chat_id, voice_msg):
        # Create save directory

        working_folder = self.get_save_dir(chat_id)

        file_obj = await voice_msg.get_file()

        file_arr = await file_obj.download_as_bytearray()

        file_idx = 0
        fname_found = False
        files_v = os.listdir(working_folder)
        while not fname_found:
            ogg_filename = '{}_{:05d}.ogg'.format(chat_id, file_idx)

            if not ogg_filename in files_v:
                fname_found = True

            file_idx += 1

        save_path = os.path.join(working_folder, ogg_filename)

        # Use async with to download the file asynchronously
        with open(save_path, 'wb') as f:
            f.write(file_arr)
        print(save_path)
        return save_path

    def save_log(self, chat_id, msg, resp_v):

        to_save = json.dumps([int(time.time()), chat_id, msg, resp_v])

        working_folder = self.get_save_dir(chat_id)
        log_file_path = os.path.join(working_folder, 'chat_log.txt')
        with open(log_file_path, 'a') as f:
            f.write(to_save + '\n')

        return None

    async def on_txt_msg(self, update: Update, context: CallbackContext) -> None:
        msg = update.message.text
        chat_id = update.message.chat_id

        bot_brain = self.get_bot_by_chat_id(chat_id, force_start=False)

        resp_v = bot_brain.query(msg)

        if self.verbose:
            print('msg[{}]: {} '.format(chat_id, msg))
            print('mk_rep:     {}'.format(resp_v))
            print()

        # Send response through the telegram_bot
        await self.send_resp_v(chat_id, context.bot, resp_v)

        # Make or delete log
        if self.make_log:
            self.save_log(chat_id, msg, resp_v)

        return None

    async def send_resp_v(self, chat_id, tg_bot, resp_v):
        for text in resp_v:
            await tg_bot.send_message(chat_id=chat_id, text=text)

    async def on_voice_msg(self, update: Update, context: CallbackContext) -> None:
        voice_msg = update.message.voice
        print(voice_msg)
        chat_id = update.message.chat_id

        bot_brain = self.get_bot_by_chat_id(chat_id, force_start=False)

        # Read and convert the voice message to text
        try:
            # Read and convert the voice message to text
            ogg_filename = await self.save_voice_msg(chat_id, voice_msg)
            msg = self.voice2text(ogg_filename)
            print('msg:', msg)

            resp_v = bot_brain.query(msg)
            resp_v[0] = 'whisper_echo: {}\n\n{}'.format(msg, resp_v[0])

            if self.verbose:
                print('msg[{}]: {} '.format(chat_id, msg))
                print('mk_rep:     {}'.format(resp_v))
                print()

            # Send response through the telegram_bot
            await self.send_resp_v(chat_id, context.bot, resp_v)

            # Make or delete log
            if self.make_log:
                self.save_log(chat_id, msg, resp_v)
            else:
                os.remove(ogg_filename)

        except Exception as e:
            print('Error in on_voice_msg:', str(e))

        return None

    def connect(self):
        self.application.run_polling()
        if self.verbose:
            print('Telegram Bot is running ...')

        return None


if __name__ == '__main__':
    from aux_f import *
    from openai import OpenAi_sph2txt
    tokens_d = read_keys_d(file_name='./api_keys.json')

    open2 = OpenAi_sph2txt(verbose=False)

    tb = TelegramBot(token=tokens_d['AUTONAV_SALES_BOT_TOKEN'], t2s_obj=open2, make_log=True)
    tb.connect()
