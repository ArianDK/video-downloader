import os
import platform
import shutil
import zipfile
import requests
from yt_dlp import YoutubeDL
from PIL import Image
from io import BytesIO

def ensure_ffmpeg():
    """Ensure FFmpeg is available for video processing."""
    ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg")
    if platform.system() == "Windows":
        ffmpeg_exe = os.path.join(ffmpeg_path, "ffmpeg.exe")
    else:
        ffmpeg_exe = os.path.join(ffmpeg_path, "ffmpeg")

    if os.path.exists(ffmpeg_exe):
        return ffmpeg_exe

    try:
        if platform.system() == "Windows":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_file_path = os.path.join(os.getcwd(), "ffmpeg.zip")
            response = requests.get(url, stream=True)
            with open(zip_file_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_path)

            bin_path = os.path.join(ffmpeg_path, os.listdir(ffmpeg_path)[0], "bin")
            shutil.move(os.path.join(bin_path, "ffmpeg.exe"), ffmpeg_exe)
            shutil.rmtree(os.path.join(ffmpeg_path, os.listdir(ffmpeg_path)[0]), ignore_errors=True)

        else:
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            tar_file_path = os.path.join(os.getcwd(), "ffmpeg.tar.xz")
            response = requests.get(url, stream=True)
            with open(tar_file_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)

            shutil.unpack_archive(tar_file_path, ffmpeg_path)
            for root, _, files in os.walk(ffmpeg_path):
                if "ffmpeg" in files:
                    shutil.copy(os.path.join(root, "ffmpeg"), ffmpeg_exe)
                    break
            shutil.rmtree(ffmpeg_path, ignore_errors=True)

    except Exception as e:
        raise RuntimeError(f"Failed to download FFmpeg: {str(e)}")

    return ffmpeg_exe

def fetch_video_thumbnail(link):
    """Fetch and return the video thumbnail."""
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            response = requests.get(thumbnail_url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
    except Exception as e:
        raise RuntimeError(f"Could not fetch thumbnail: {str(e)}")

def download_video_with_progress(link, resolution, save_path_with_name, progress_hook):
    """
    Download the video using yt-dlp and apply the selected resolution.

    Args:
        link (str): The URL of the video.
        resolution (str): Desired resolution (e.g., "480p", "720p").
        save_path_with_name (str): Full path including filename where the video should be saved.
        progress_hook (function): Function to report progress dynamically.
    """
    try:
        ffmpeg_path = ensure_ffmpeg()
        save_path, save_name = os.path.split(save_path_with_name)

        resolution_height = int(resolution[:-1])

        def hook(d):
            if progress_hook:
                if d["status"] == "downloading":
                    percent = float(d.get("downloaded_bytes", 0)) / float(d.get("total_bytes", 1)) * 90
                    progress_hook(percent)
                elif d["status"] == "post_process":
                    progress_hook(90)

        ydl_opts = {
            'outtmpl': os.path.join(save_path, save_name),
            'format': f'bestvideo[height<={resolution_height}]+bestaudio/best',
            'ffmpeg_location': ffmpeg_path,
            'merge_output_format': 'mp4',
            'progress_hooks': [hook],
            'postprocessors': [
                {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                {'key': 'FFmpegMetadata'},
            ],
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental']
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        if progress_hook:
            progress_hook(100)

    except Exception as e:
        raise RuntimeError(f"An error occurred while downloading the video: {str(e)}")
