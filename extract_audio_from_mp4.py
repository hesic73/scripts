import subprocess
import click
import os


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output_file', '-o', type=click.Path(), help='Output MP3 file. Optional.')
@click.option('--audio_channels', '-ac', default=2, type=int, help='Number of audio channels. Default is 2 (stereo).')
@click.option('--audio_rate', '-ar', default=44100, type=int, help='Audio sampling rate in Hz. Default is 44100 Hz.')
@click.option('--audio_bitrate', '-ab', default='192k', type=str, help='Audio bitrate. Default is 192 kbps.')
def extract_audio_from_mp4(input_file: str, output_file: str, audio_channels: int, audio_rate: int, audio_bitrate: str):
    """
    Extracts audio from an MP4 file and saves it as an MP3 file.

    If no output file is specified, the MP3 file is saved in the same directory with the same name as the input file, but with an .mp3 extension.
    """
    if not output_file:
        # Generate output filename by changing the extension of input_file to .mp3
        output_file = os.path.splitext(input_file)[0] + '.mp3'

    command = [
        'ffmpeg',
        '-i', input_file,  # Input file
        '-vn',  # No video.
        '-ar', str(audio_rate),  # Audio sampling rate
        '-ac', str(audio_channels),  # Number of audio channels
        '-b:a', audio_bitrate,  # Audio bitrate
        output_file  # Output file
    ]

    try:
        subprocess.run(command, check=True)
        click.echo(f"Audio extracted and saved to {output_file}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during audio extraction: {e}", err=True)


if __name__ == '__main__':
    extract_audio_from_mp4()
