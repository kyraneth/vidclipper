import moviepy
import argparse
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.all import speedx
from moviepy.video.compositing.concatenate import concatenate_videoclips
import threading
import re

# Default output directory - will be configurable in the GUI
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "vidclipper_downloads")

class VidClipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VidClipper")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(DEFAULT_OUTPUT_DIR):
            os.makedirs(DEFAULT_OUTPUT_DIR)
        
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.downloaded_path = None
        self.clips = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="YouTube URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Output directory selection
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame, width=40)
        self.dir_entry.insert(0, self.output_dir)
        self.dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT)
        
        # Speed control
        speed_frame = ttk.Frame(main_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Playback Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="1.0")
        speed_options = ["0.5", "0.75", "1.0", "1.25", "1.5", "2.0"]
        speed_dropdown = ttk.Combobox(speed_frame, textvariable=self.speed_var, values=speed_options, width=5)
        speed_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Concatenate option
        self.concat_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(speed_frame, text="Concatenate Clips", variable=self.concat_var).pack(side=tk.LEFT, padx=20)
        
        # Clips section
        clips_frame = ttk.LabelFrame(main_frame, text="Clip Segments")
        clips_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Clips list
        self.clips_listbox = tk.Listbox(clips_frame, height=8)
        self.clips_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(clips_frame, orient="vertical", command=self.clips_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clips_listbox.config(yscrollcommand=scrollbar.set)
        
        # Clip controls
        clip_controls = ttk.Frame(main_frame)
        clip_controls.pack(fill=tk.X, pady=5)
        
        ttk.Label(clip_controls, text="Start Time:").pack(side=tk.LEFT)
        self.start_entry = ttk.Entry(clip_controls, width=8)
        self.start_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(clip_controls, text="End Time:").pack(side=tk.LEFT)
        self.end_entry = ttk.Entry(clip_controls, width=8)
        self.end_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(clip_controls, text="Add Clip", command=self.add_clip).pack(side=tk.LEFT, padx=5)
        ttk.Button(clip_controls, text="Remove Clip", command=self.remove_clip).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Download & Process", command=self.process_video).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT, padx=5)
    
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir = directory
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def add_clip(self):
        try:
            start_time = float(self.start_entry.get())
            end_time = float(self.end_entry.get())
            
            if start_time >= end_time:
                messagebox.showerror("Invalid Time", "End time must be greater than start time")
                return
            
            self.clips.append((start_time, end_time))
            self.clips_listbox.insert(tk.END, f"Clip: {start_time:.2f}s to {end_time:.2f}s")
            
            # Clear entries
            self.start_entry.delete(0, tk.END)
            self.end_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for start and end times")
    
    def remove_clip(self):
        selected = self.clips_listbox.curselection()
        if selected:
            index = selected[0]
            self.clips_listbox.delete(index)
            self.clips.pop(index)
    
    def clear_all(self):
        self.url_entry.delete(0, tk.END)
        self.clips_listbox.delete(0, tk.END)
        self.clips = []
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.speed_var.set("1.0")
        self.concat_var.set(False)
        self.status_var.set("Ready")
    
    def process_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not self.clips:
            messagebox.showerror("Error", "Please add at least one clip segment")
            return
        
        # Update output directory from entry field
        self.output_dir = self.dir_entry.get()
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory: {str(e)}")
                return
        
        # Start processing in a separate thread
        threading.Thread(target=self.process_video_thread, args=(url,), daemon=True).start()
    
    def process_video_thread(self, url):
        try:
            self.status_var.set("Downloading video...")
            self.root.update_idletasks()
            
            # Download the video
            self.downloaded_path = self.download_video(url)
            
            if not self.downloaded_path:
                self.status_var.set("Download failed")
                messagebox.showerror("Error", "Failed to download video")
                return
            
            self.status_var.set("Processing clips...")
            self.root.update_idletasks()
            
            # Process clips
            speed = float(self.speed_var.get())
            concatenate = self.concat_var.get()
            
            processed_clips = []
            for i, (start_time, end_time) in enumerate(self.clips):
                self.status_var.set(f"Processing clip {i+1}/{len(self.clips)}...")
                self.root.update_idletasks()
                
                clip = self.cut_video(self.downloaded_path, start_time, end_time, concatenate, speed)
                if clip:
                    processed_clips.append(clip)
            
            # Concatenate if needed
            if concatenate and processed_clips:
                self.status_var.set("Concatenating clips...")
                self.root.update_idletasks()
                
                final = concatenate_videoclips(processed_clips)
                
                p = Path(self.downloaded_path)
                name = p.stem
                
                output_path = os.path.join(self.output_dir, f"{name}_concatenated.mp4")
                final.write_videofile(output_path)
                
                self.status_var.set(f"Saved concatenated video to {output_path}")
            else:
                self.status_var.set("All clips processed successfully")
            
            # Clean up the downloaded file
            p = Path(self.downloaded_path)
            p.unlink()
            
            messagebox.showinfo("Success", "Video processing completed successfully")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def download_video(self, url):
        try:
            yt = YouTube(url)
            video = yt.streams.get_highest_resolution()
            downloaded_path = video.download(self.output_dir)
            return downloaded_path
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download video: {str(e)}")
            return None
    
    def cut_video(self, path, start_time, end_time, concatenate, speed):
        try:
            p = Path(path)
            name = p.stem
            
            vid = VideoFileClip(path)
            vid = vid.subclip(start_time, end_time)
            
            if speed != 1.0:
                vid = vid.fx(speedx, speed)
            
            if not concatenate:
                output_path = os.path.join(self.output_dir, f"{name}_{start_time:.2f}_{end_time:.2f}.mp4")
                vid.write_videofile(output_path)
            
            return vid
        except Exception as e:
            messagebox.showerror("Processing Error", f"Failed to process clip: {str(e)}")
            return None


def parse_timecodes(timecode_str):
    """Convert timecode strings like '1:30-2:45, 3:10-4:00' to float tuples."""
    clips = []
    
    # Split by comma
    segments = [s.strip() for s in timecode_str.split(',')]
    
    for segment in segments:
        # Split by dash
        times = segment.split('-')
        if len(times) != 2:
            continue
        
        start, end = times
        
        # Convert each time to seconds
        try:
            start_seconds = convert_to_seconds(start.strip())
            end_seconds = convert_to_seconds(end.strip())
            clips.append((start_seconds, end_seconds))
        except ValueError:
            continue
    
    return clips


def convert_to_seconds(time_str):
    """Convert a time string (e.g., '1:30') to seconds."""
    # Check if it's already in seconds format
    if re.match(r'^\d+(\.\d+)?$', time_str):
        return float(time_str)
    
    # Handle MM:SS format
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    
    raise ValueError(f"Invalid time format: {time_str}")


def download_video(url, output_dir=DEFAULT_OUTPUT_DIR):
    """Download a video from YouTube."""
    try:
        my_video = YouTube(url)
        my_video = my_video.streams.get_highest_resolution()
        downloaded_path = my_video.download(output_dir)
        return downloaded_path
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None


def cut_video(path, start_time, end_time, concatenate=False, speed=1.0, output_dir=DEFAULT_OUTPUT_DIR):
    """Cut a segment from a video."""
    try:
        p = Path(path)
        name = p.stem
        
        vid = VideoFileClip(path)
        vid = vid.subclip(start_time, end_time)
        
        if speed != 1.0:
            vid = vid.fx(speedx, speed)
        
        if not concatenate:
            output_path = os.path.join(output_dir, f"{name}_{start_time:.2f}_{end_time:.2f}.mp4")
            vid.write_videofile(output_path)
        
        return vid
    except Exception as e:
        print(f"Error cutting video: {str(e)}")
        return None


def main_cli():
    """Command-line interface for VidClipper."""
    my_parser = argparse.ArgumentParser(prog='vidclipper',
                                        description='Download and Clip a Video File')
    
    my_parser.add_argument('url',
                           metavar='url',
                           type=str,
                           help='The URL to the video')
    
    my_parser.add_argument('timecodes',
                           type=float,
                           nargs='*',
                           help='Input start and end times of video segments (in seconds)')
    
    my_parser.add_argument('--speed',
                           metavar='speed',
                           type=float,
                           help='Change video speed',
                           default=1.0)
    
    my_parser.add_argument('--conc', 
                           action='store_true', 
                           help='concatenate clipped segments')
    
    my_parser.add_argument('--output-dir',
                           metavar='output_dir',
                           type=str,
                           help='Output directory for downloaded and processed videos',
                           default=DEFAULT_OUTPUT_DIR)
    
    my_parser.add_argument('--timecode-format',
                           metavar='timecode_format',
                           type=str,
                           help='Specify timecodes in format "1:30-2:45, 3:10-4:00" instead of raw seconds',
                           default=None)
    
    args = my_parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Process timecodes
    if args.timecode_format:
        clips = parse_timecodes(args.timecode_format)
    else:
        # Traditional way with raw seconds
        input_times = args.timecodes
        clips = []
        for i in range(0, len(input_times) - 1, 2):
            clips.append((input_times[i], input_times[i+1]))
    
    if not clips:
        print("Error: No valid clip segments specified")
        return
    
    # Download the video
    path = download_video(args.url, args.output_dir)
    if not path:
        print("Error: Failed to download video")
        return
    
    # Process clips
    processed_clips = []
    for start_time, end_time in clips:
        clip = cut_video(path, start_time, end_time, args.conc, args.speed, args.output_dir)
        if clip:
            processed_clips.append(clip)
    
    # Concatenate if needed
    if args.conc and processed_clips:
        final = concatenate_videoclips(processed_clips)
        
        p = Path(path)
        name = p.stem
        
        output_path = os.path.join(args.output_dir, f"{name}_concatenated.mp4")
        final.write_videofile(output_path)
    
    # Clean up the downloaded file
    p = Path(path)
    p.unlink()


if __name__ == "__main__":
    # Check if arguments were provided (CLI mode)
    import sys
    if len(sys.argv) > 1:
        main_cli()
    else:
        # GUI mode
        root = tk.Tk()
        app = VidClipperApp(root)
        root.mainloop()

