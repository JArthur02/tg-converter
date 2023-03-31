```py
import logging
import subprocess
import time
from pathlib import Path

from telegram import Update, ChatAction, VideoNote
from telegram.ext import Updater, CommandHandler

# Enable logging - Logging helps us keep track of what our program does 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get(6270886918:AAESzsyRTlsRjwYLrAXjCzl1hXvyniC0NJ0)

def start(update: Update, context):
  """Send a message when the command /start is issued."""
  update.message.reply_text('Hi! Send me any video file!')


def convert_to(update: Update, context):
  """Converts provided Video File into mp4 format"""
  video = update.message.video or update.message.document
  if video is None:
      update.message.reply_text('Please send a video!')
      return

  try:
      video_file = context.bot.get_file(video.file_id)
      file_size_in_mb = round((video.file_size / (1024 * 1024)), 2)

  except Exception as e:
      update.message.reply_text(f'Error downloading file: {e}')
      return

  new_filename = f"{update.effective_user.id}_{int(time.time())}.mp4"

  temp_path = Path(__file__).parent.joinpath("temp")

  if not temp_path.exists():
      Path.mkdir(temp_path)

  local_video_filepath = temp_path.joinpath(new_filename)

  video_file.download(custom_path=str(local_video_filepath))

  try:
      # Use FFmpeg subprocess call to convert files (.mov example shown here)
      command_args = ["ffmpeg", "-i", str(local_video_filepath), "-max_muxing_queue_size", "4000k", "-y",
                      "-vcodec", "libx264",
                      "-profile:v", "baseline", "-level", "3.0",
                      "-s", '640*360', '-r', '24', "-acodec", "aac",
                      str(temp_path.joinpath(str(update.effective_user.id) + '.mp4'))]

      result = subprocess.run(command_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  except FileNotFoundError as fnf_err:
      logger.error(fnf_err.strerror + " with filename " + fnf_err.filename)
      return

  context.bot.send_chat_action(chat_id=update.chat_id, action=ChatAction.UPLOAD_VIDEO_NOTE)

  with open(str(temp_path.joinpath(new_filename)), 'rb') as output_vid:
      try:
          vid_note = context.bot.send_video_note(chat_id=update.chat_id,
                                                 duration=int(video.duration),
                                                 length=int(video.width),
                                                 height=int(video.height),
                                                 video_note=output_vid)

      except Exception as e:
          logger.error("Error uploading file: " + str(e))
          return

  update.message.reply_text('Video converted successfully!')

def main():
  """Start the bot."""
  # Create an Updater object and attach it to your access token
  updater = Updater(token=6270886918:AAESzsyRTlsRjwYLrAXjCzl1hXvyniC0NJ0, use_context=True)

  # Get the dispatcher to register handlers
  dp = updater.dispatcher

  # Add command handler for /start command 
  dp.add_handler(CommandHandler('start', start))

  # Add command handler for converting videos into mp4 format.
  dp.add_handler(CommandHandler('convertto', convert_to))

  # Start polling - this will run until you press Ctrl-C or the process is stopped another way
  updater.start_polling()
  
if __name__ == '__main__':
  main()
