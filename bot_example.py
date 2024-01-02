from telegram import Voice
import os
import asyncio

# Now you can use the Voice class
voice_message_info = Voice(
    duration=2,
    file_id='AwACAgQAAxkBAAOWZY1r6A8iYwtftbJ7aNKmGQ6sOd0AAgQRAALcCmFQ5o41xuNhzc0zBA',
    file_size=7492,
    file_unique_id='AgADBBEAAtwKYVA',
    mime_type='audio/ogg'
)


async def save_voice_msg(chat_id, voice_msg):
    # Creamos directorio de salvado

    working_folder = 'C:\\Users\\USRE\\Downloads\\5653713567'

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
    async with open(save_path, 'wb') as f:
        await f.write(file_arr)
    print(save_path)
    return save_path


async def main():
    save_path = await save_voice_msg('5653713567', voice_message_info)
    print(save_path)

# Create an event loop
loop = asyncio.get_event_loop()

# Run the asynchronous function within the event loop
loop.run_until_complete(main())

