import re
import threading
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from video_downloader import fetch_video_thumbnail, download_video_with_progress
from yt_dlp import YoutubeDL


def handle_link_submission(link_var, thumbnail_label, download_button, start_download_thread):
    link = link_var.get()
    if not link:
        messagebox.showerror("Error", "Please enter a valid link.")
        return

    try:
        thumbnail = fetch_video_thumbnail(link)
        if thumbnail:
            if "tiktok.com" in link or "instagram.com" in link:
                target_width = 180
                target_height = int(target_width * 16 / 9)
            else:
                target_width = 320
                target_height = 180

            thumbnail = thumbnail.resize((target_width, target_height), Image.Resampling.LANCZOS)
            thumbnail_image = ImageTk.PhotoImage(thumbnail)
            thumbnail_label.configure(image=thumbnail_image)
            thumbnail_label.image = thumbnail_image
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    download_button.pack(pady=10)
    download_button.configure(
        state="normal",
        command=lambda: start_download_thread(link)
    )


def start_download_thread(
        link, 
        progress_bar, 
        progress_label, 
        current_resolution, 
        reset_program, 
        update_progress
        ):
    # Show the progress bar and percentage label
    progress_bar.pack(pady=10)
    progress_label.pack(pady=5)

    # Start a new thread for the download process
    def thread_target():
        try:
            video_title = get_video_title(link)
            save_path_with_name = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")],
                title="Save Video As",
                initialfile=f"{video_title}.mp4"
            )
            if not save_path_with_name:
                reset_program()  # Reset the program if the user cancels
                return

            download_video_with_progress(link, current_resolution.get(), save_path_with_name, update_progress)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    thread = threading.Thread(target=thread_target)
    thread.daemon = True
    thread.start()


def update_progress(progress, progress_bar, progress_label, new_download_button):
    """
    Update the progress bar and percentage label dynamically.

    Args:
        progress (int): The current progress percentage (0-100).
        progress_bar (ttk.Progressbar): The progress bar widget to update.
        progress_label (tk.Label): The label widget to display progress percentage.
        new_download_button (ttk.Button): The button to display when download is complete.
    """
    if progress < 90:
        progress_bar["value"] = progress
        progress_label["text"] = f"{int(progress)}%"
    elif progress == 90:
        progress_label["text"] = "Merging (90%)"
    elif progress == 100:
        progress_bar["value"] = 100
        progress_label["text"] = "100%"
        new_download_button.pack(pady=10)


def reset_program(
        link_var, 
        progress_bar, 
        progress_label, 
        new_download_button, 
        download_button, 
        thumbnail_label
        ):
    """
    Reset the GUI to its initial state.

    Args:
        link_var (tk.StringVar): The variable holding the link input.
        progress_bar (ttk.Progressbar): The progress bar widget to hide.
        progress_label (tk.Label): The label widget to hide.
        new_download_button (ttk.Button): The button to hide.
        download_button (ttk.Button): The download button to hide.
        thumbnail_label (tk.Label): The label to clear the thumbnail.
    """
    link_var.set("")
    progress_bar.pack_forget()
    progress_label.pack_forget()
    new_download_button.pack_forget()
    download_button.pack_forget()
    thumbnail_label.configure(image="")


def update_resolution(event, resolution_menu, current_resolution):
    """
    Update the selected resolution dynamically based on user selection.

    Args:
        event: The event triggered by selecting a resolution.
        resolution_menu (ttk.Combobox): The combobox widget for resolution selection.
        current_resolution (tk.StringVar): The variable to store the selected resolution.
    """
    selected_resolution = resolution_menu.get()
    current_resolution.set(selected_resolution)


def get_video_title(link):
    """
    Fetch the video title from the given link and sanitize it for saving as a file name.

    Args:
        link (str): The URL of the video.

    Returns:
        str: Sanitized video title.

    Raises:
        RuntimeError: If the title cannot be fetched or sanitized.
    """
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            title = info.get('title', 'video')
            sanitized_title = re.sub(r'[<>:"/\\|?*]', '-', title)
            return sanitized_title
    except Exception as e:
        raise RuntimeError(f"Could not fetch video title: {str(e)}")



