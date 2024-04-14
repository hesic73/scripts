import cv2
import os
import click
from datetime import datetime

from typing import Optional, Callable, Any


def create_video_from_images(image_dir: str, output_path: str, fps: float = 10, key: Optional[Callable[[str], Any]] = None):
    # Get all files in the directory
    files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Sort files either by custom comparator or alphabetically
    if key:
        files.sort(key=key)
    else:
        files.sort()

    # Ensure we have a valid list of files
    if not files:
        print("No .png files found in the directory.")
        return

    # Read the first image to get the properties
    first_frame_path = os.path.join(image_dir, files[0])
    frame = cv2.imread(first_frame_path)
    if frame is None:
        print(f"Error reading the first image file: {first_frame_path}")
        return
    height, width, layers = frame.shape
    size = (width, height)

    # Define the codec and create VideoWriter object
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for filename in files:
        full_path = os.path.join(image_dir, filename)
        frame = cv2.imread(full_path)
        if frame is None:
            print(f"Skipping file {filename} as it is not a valid image")
            continue
        # Resize image to match the first image size if different
        if (frame.shape[1], frame.shape[0]) != size:
            frame = cv2.resize(frame, size)
        out.write(frame)

    # Release everything when job is done
    out.release()
    cv2.destroyAllWindows()
    print(f"Video saved to {output_path}")


@click.command()
@click.argument('image_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.option('--output_path', type=click.Path(writable=True), default=None,
              help="Specify the output path for the video file. If not provided, it defaults to a path based on the image directory or a timestamp.")
@click.option('--fps', type=float, default=10,
              help="Frames per second for the video. Default is 10.")
def main(image_dir, output_path, fps):
    # Clean up the image directory path to remove any trailing slash
    image_dir = image_dir.rstrip('/')


    # Determine the default output path based on the image directory name
    if output_path is None:
        dir_name = os.path.basename(image_dir)
        default_path = f"{dir_name}.mp4"
        if os.path.exists(default_path):
            current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            default_path = f"./video_{current_time}.mp4"
        output_path = default_path

    # Call the create_video_from_images function
    create_video_from_images(image_dir, output_path, fps, key=lambda x: int(os.path.splitext(x)[0]))


if __name__ == '__main__':
    main()
