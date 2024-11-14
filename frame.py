import cv2
import os
from datetime import datetime
import time  # Importing time module to add delay

def capture_frames(video_path, output_folder, interval=3):
    os.makedirs(output_folder, exist_ok=True)

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)

    current_frame = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break 

        if current_frame % frame_interval == 0:
            now = datetime.now()
            filename_time = now.strftime("%I-%M-%S_%d-%m-%Y")

            # Commenting out timestamp on image code
            # timestamp = now.strftime("%I:%M:%S %p")
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # font_scale = 1
            # thickness = 2
            # text_x = 10
            # text_y = frame.shape[0] - 10
            # rectangle_bgr = (0, 0, 0) 
            # text_size, _ = cv2.getTextSize(timestamp, font, font_scale, thickness)
            # cv2.rectangle(frame, (text_x, text_y - text_size[1] - 10),
            #               (text_x + text_size[0] + 10, text_y + 10),
            #               rectangle_bgr, -1)
            # text_color = (255, 255, 255)
            # cv2.putText(frame, timestamp, (text_x, text_y), font, font_scale, text_color, thickness)

            filename = f"{filename_time}.jpg"
            cv2.imwrite(os.path.join(output_folder, filename), frame)
            print(f"Saved frame: {filename}")

            # Adding delay based on the interval before capturing the next frame
            time.sleep(1)

        current_frame += 1

    video.release()
    print("All frames captured.")

# Usage
video_path = r'.\Cars\EV4.mp4'  # Enter Video Path
output_folder = r'.\frames' # Enter Folder path where images are stored
capture_frames(video_path, output_folder)
