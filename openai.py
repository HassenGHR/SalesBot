import whisper
from pydub import AudioSegment
import os
import sys


class OpenAi_sph2txt:

    def __init__(self, verbose=False):
        self.verbose = verbose
        return None

    def read_opus(self, file_name, output_dir=None):
        try:
            if self.verbose:
                print(' - read_opus, Reading file:', file_name, 'with pydub')

            if not os.path.exists(file_name):
                raise FileNotFoundError(f"OGG file not found: {file_name}")

            sound = AudioSegment.from_ogg(file_name)

            if output_dir:
                output_path = os.path.join(output_dir, os.path.basename(file_name).replace(".ogg", ".mp3"))
            else:
                output_path = os.path.splitext(file_name)[0] + ".mp3"
            sound.export(output_path, format="mp3")
        except Exception as e:
            raise Exception(' - ERROR, read_opus: unable to read opus ogg.')
        return output_path

    def transcribe_mp3_to_text(self, file_name):
        try:
            mp3_file = self.read_opus(file_name)
            # Load the Whisper model
            model = whisper.load_model("base")
            options = whisper.DecodingOptions(fp16=False)

            # Load audio and pad/trim it to fit 30 seconds
            audio = whisper.load_audio(mp3_file)
            audio = whisper.pad_or_trim(audio)

            # Make log-Mel spectrogram and move it to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(model.device)

            # Detect the spoken language
            _, probs = model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            print(f"Detected language: {detected_language}")

            # Decode the audio
            result = whisper.decode(model, mel.float(), options)

            # Return the recognized text
            return result.text

        except Exception as e:
            print(f' - ERROR, transcribe_mp3_to_text: {e}')
if __name__ == '__main__':
    # Example usage
    from aux_f import read_keys_d  # Assuming this function is available

    # tokens_d = read_keys_d(file_name='./api_keys.json')  # Replace with your actual path

    audio_file_path = 'C:\\Users\\USRE\\Downloads\\prodcast.ogg'  # Replace with your actual path

    openai_sph2txt = OpenAi_sph2txt(verbose=True)

    # Read the Ogg file and convert to MP3
    # audio_data = openai_sph2txt.read_opus(audio_file_path)

    # Transcribe with OpenAI
    transcript = openai_sph2txt.transcribe_mp3_to_text(audio_file_path)


    print('Transcribed Text:', transcript)
