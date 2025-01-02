import os
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
import constants as CS
import utils


def main():
    # Initialize main window
    root = tk.Tk()
    root.title("Video Downloader")

    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), CS.ICON_PATH)
    icon_image = ImageTk.PhotoImage(file=icon_path)
    root.wm_iconphoto(True, icon_image)

    # Get screen dimensions for dynamic window sizing
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.2)
    window_height = int(screen_height * 0.7)
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg=CS.APP_BG_COLOR)

    # Modernize the look with ttk.Style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TLabel", font=CS.APP_FONT, background=CS.APP_BG_COLOR, foreground=CS.APP_TEXT_COLOR)
    style.configure("TButton", font=CS.APP_FONT, background=CS.APP_PRIMARY_COLOR, foreground="white", padding=10)
    style.map("TButton", background=[("active", "#45a049")])
    style.configure("TCombobox", font=("Helvetica", 11), padding=5)
    style.configure(CS.PROGRESS_BAR_STYLE, troughcolor=CS.APP_BG_COLOR, background=CS.APP_PRIMARY_COLOR, thickness=20)

    # Header
    tk.Label(root, text="Video Downloader", font=("Helvetica", 20, "bold"), fg=CS.APP_PRIMARY_COLOR, bg=CS.APP_BG_COLOR).pack(pady=20)

    # Link input frame
    link_var = tk.StringVar()
    link_frame = tk.Frame(root, bg=CS.APP_BG_COLOR)
    link_frame.pack(pady=20)
    tk.Label(link_frame, text="Enter Video Link:", font=CS.APP_FONT, bg=CS.APP_BG_COLOR, fg=CS.APP_TEXT_COLOR).pack(side="top", pady=5)
    ttk.Entry(link_frame, textvariable=link_var, width=50).pack(side="top")

    # Resolution selection
    current_resolution = tk.StringVar(value="720p")
    resolution_menu = ttk.Combobox(root, textvariable=current_resolution, state="readonly", width=10)
    resolution_menu["values"] = CS.DEFAULT_RESOLUTIONS
    resolution_menu.pack(pady=10)
    resolution_menu.bind("<<ComboboxSelected>>", lambda event: utils.update_resolution(event, resolution_menu, current_resolution))

    # Thumbnail display
    thumbnail_label = tk.Label(root, bg=CS.APP_BG_COLOR)
    thumbnail_label.pack(pady=10)

    # Progress bar and label
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", style=CS.PROGRESS_BAR_STYLE)
    progress_label = tk.Label(root, text="0%", font=CS.APP_FONT, bg=CS.APP_BG_COLOR, fg=CS.APP_TEXT_COLOR)

    # Buttons
    new_download_button = ttk.Button(root, text="New Download", command=lambda: utils.reset_program(link_var, progress_bar, progress_label, new_download_button, download_button, thumbnail_label))
    download_button = ttk.Button(root, text="Download", state="disabled")
    ttk.Button(
        root,
        text="Fetch Video",
        command=lambda: utils.handle_link_submission(
            link_var,
            thumbnail_label,
            download_button,
            lambda link: utils.start_download_thread(
                link,
                progress_bar,
                progress_label,
                current_resolution,
                lambda: utils.reset_program(link_var, progress_bar, progress_label, new_download_button, download_button, thumbnail_label),
                lambda progress: utils.update_progress(progress, progress_bar, progress_label, new_download_button),
            ),
        ),
    ).pack(pady=10)

    # Footer
    tk.Label(root, text="Developed by Arian", font=("Helvetica", 10), bg=CS.APP_BG_COLOR, fg=CS.APP_SECONDARY_COLOR).pack(side="bottom", pady=10)

    root.mainloop()
