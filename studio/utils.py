from PIL import Image
import numpy as np
from PIL import Image
from .models import Frame
import subprocess
import os
import math

def get_video_duration(input_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of",
             "default=noprint_wrappers=1:nokey=1", input_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        return int(float(result.stdout))
    except Exception as e:
        print("⚠️ Could not get video duration:", e)
        return 0

def extract_hd_frames(temp_path, frame_count, output_dir, video_instance):
    os.makedirs(output_dir, exist_ok=True)

    # Get video duration
    duration = get_video_duration(temp_path)
    print(f"⏱️ Duration of video: {duration:.2f} seconds")

    if duration <= 0:
        print("❌ Invalid video duration.")
        return []

    fps = frame_count / duration
    if fps <= 0:
        print("❌ Invalid fps value.")
        return []

    output_pattern = os.path.join(output_dir, "frame_%04d.png")
    command = [
        "ffmpeg", "-i", temp_path, "-vf", f"fps={fps:.6f}", "-vsync", "vfr", "-q:v", "2", output_pattern
    ]

    try:
        print(f"🎬 Running FFmpeg command: {' '.join(command)}")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        frame_files = sorted([
            os.path.join(output_dir, f) for f in os.listdir(output_dir)
            if f.endswith(".png")
        ])

        if not frame_files:
            print("❌ No frames extracted.")
            return []

        frame_counter = 1
        grouped_frames = []
        frames_per_second = math.ceil(len(frame_files) / duration) if duration else 1

        for i in range(0, len(frame_files), frames_per_second):
            group = frame_files[i:i + frames_per_second]
            grouped_frames.append(group)

        for group in grouped_frames:
            for path in group:
                with open(path, "rb") as img_file:
                    Frame.objects.create(
                        video=video_instance,
                        frame_number=frame_counter,
                        frame_data=img_file.read()
                    )
                    frame_counter += 1

        print(f"📦 Saved {frame_counter - 1} frames to the database.")
        return grouped_frames

    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg error:", e.stderr.decode())
        return []
