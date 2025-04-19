import os
import chardet
import fire
from loguru import logger


def detect_and_convert_encoding(file_path: str, target_encoding: str) -> bool:
    """
    Detects and converts the file's encoding to the target encoding.

    :param file_path: Path to the file to process.
    :param target_encoding: The desired encoding for the file.
    :return: True if conversion was successful, False otherwise.
    """
    # Read the binary content of the file
    with open(file_path, 'rb') as f:
        raw_data = f.read()

    # Attempt to decode using the target encoding
    try:
        raw_data.decode(target_encoding)
        logger.info(
            f"✓ {file_path} is already in {target_encoding} encoding, skipping")
        return False
    except UnicodeDecodeError:
        pass  # Decoding failed with the target encoding

    # Detect the current file encoding
    detection = chardet.detect(raw_data)
    detected_encoding = detection['encoding']
    confidence = detection['confidence']
    logger.info(
        f"Detected {file_path} possible encoding: {detected_encoding} (confidence: {confidence:.2f})")

    # Encoding alias mapping
    encoding_mapping = {
        'gb2312': 'gbk',
        'iso-8859-1': 'latin_1',
        'ascii': 'utf-8'  # ASCII is a subset of UTF-8
    }
    detected_encoding = encoding_mapping.get(
        detected_encoding.lower(), detected_encoding)

    # Attempt to decode using various encodings
    decoded = None
    try_encodings = [detected_encoding] if detected_encoding else []
    try_encodings += ['gbk', 'utf-8', 'latin_1', 'cp1252', 'big5', 'shift_jis']

    for enc in try_encodings:
        if not enc:
            continue
        try:
            decoded = raw_data.decode(enc)
            logger.info(f"Successfully decoded using {enc}")
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if not decoded:
        logger.error(
            f"× Failed to decode {file_path}, all supported encodings tried")
        return False

    # Convert to target encoding
    try:
        encoded_data = decoded.encode(target_encoding)
    except UnicodeEncodeError as e:
        logger.error(f"× Encoding failed: {str(e)}")
        return False

    # Write back to the file
    try:
        with open(file_path, 'wb') as f:
            f.write(encoded_data)
        logger.info(
            f"☆ Successfully converted {file_path} to {target_encoding}")
        return True
    except IOError as e:
        logger.error(f"× File write failed: {str(e)}")
        return False


def process_directory(directory: str, target_encoding: str) -> None:
    """
    Processes all files in a directory to convert their encoding.

    :param directory: Path to the directory to process.
    :param target_encoding: The desired encoding format for the files.
    """
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(('.cpp', '.h')):
                file_path = os.path.join(root, filename)
                detect_and_convert_encoding(file_path, target_encoding)


def main(directory: str, encoding: str = 'utf-8') -> None:
    """
    Main function to start processing the directory.

    :param directory: The directory path to process.
    :param encoding: The target encoding format (default: utf-8).
    """
    if not os.path.isdir(directory):
        logger.error(f"Error: {directory} is not a valid directory")
        return

    print(
        f"{'='*40}\nStarting processing of directory: {directory}\nTarget encoding: {encoding}\n{'='*40}")
    process_directory(directory, encoding)
    print(f"{'='*40}\nProcessing completed\n{'='*40}")


if __name__ == "__main__":
    fire.Fire(main)
