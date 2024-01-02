import requests
import json
import wave
import numpy as np
import io
import sys
from pydub import AudioSegment

class WIT_sph2txt:

    def __init__(self, wit_token='', verbose=False):
        self.wit_token = wit_token
        self.verbose = verbose
        return None

    def opusfile_to_text(self, file_name='cristobal.ogg', language='en'):
        WIT_API_URL = 'https://api.wit.ai/speech'

        headers_d = {'Authorization': 'Bearer ' + self.wit_token, 'Content-type': 'audio/wav'}
        audio_data = self.opus2wav(file_name)

        params = {'v': '20170307', 'lang': language}
        r = requests.post(WIT_API_URL, data=audio_data, headers=headers_d, params=params)
        content = r.content

        if self.verbose:
            print(' - wit response content:', content)

        if isinstance(content, bytes):
            content = content.decode(errors='ignore')

        resp_d = json.loads(content)

        if self.verbose:
            print(r.status_code, r.reason)

        if r.status_code == 200:
            text = resp_d['_text']
        else:
            print(' - ERROR, opusfile_to_text: ', resp_d, file=sys.stderr)
            text = ''

        if self.verbose:
            print(' - opusfile_to_text: Text read: "{}"'.format(text))

        return text

    def opus2wav(self, file_name):
        try:
            if self.verbose:
                print(' - opus2wav, Converting file:', file_name)

            # Use pydub to convert Ogg Opus to WAV
            audio = AudioSegment.from_file(file_name, format="ogg")
            audio.export('output.wav', format="wav")

            with open('output.wav', 'rb') as wav_file:
                audio_data = wav_file.read()

            return audio_data

        except Exception as e:
            print(f' - ERROR, opus2wav: {e}', file=sys.stderr)
            raise Exception(' - ERROR, opus2wav: unable to convert opus to wav.')

if __name__ == '__main__':
    from aux_f import *

    tokens_d = read_keys_d(file_name='./api_keys.json')

    file_name = 'C:\\Users\\USRE\\Downloads\\prodcast.ogg'

    wit = WIT_sph2txt(wit_token=tokens_d['WIT_CLIENT_TOKEN'], verbose=True)
    text = wit.opusfile_to_text(file_name)
