import re
from pathlib import Path
from ebooklib import epub
import fire
from loguru import logger


def txt_to_epub(txt_file_path, output_path=None, book_title=None, author=None):
    """
    Convert a Chinese web novel txt file to epub format.

    Args:
        txt_file_path: Path to input txt file (UTF-8 encoded)
        output_path: Path for output epub file (optional)
        book_title: Title of the book (optional, defaults to txt filename)
        author: Author name (optional, defaults to 'Unknown Author')

    Returns:
        Path to the generated epub file
    """
    logger.info(f"Starting conversion for: {txt_file_path}")

    txt_path = Path(txt_file_path)

    if not txt_path.exists():
        logger.error(f"File not found: {txt_file_path}")
        raise FileNotFoundError(f"File not found: {txt_file_path}")

    logger.debug(f"Reading file: {txt_path}")
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    if book_title is None:
        book_title = txt_path.stem
        logger.info(f"Using filename as book title: {book_title}")
    else:
        logger.info(f"Using provided book title: {book_title}")

    if author is None:
        author = "Unknown Author"
        logger.info(f"Using default author: {author}")
    else:
        logger.info(f"Using provided author: {author}")

    if output_path is None:
        output_path = txt_path.with_suffix(".epub")
    logger.info(f"Output path: {output_path}")

    logger.info("Parsing chapters...")
    chapters = parse_chapters(content)
    logger.success(f"Found {len(chapters)} chapters")

    logger.info("Creating EPUB...")
    book = create_epub(book_title, chapters, author)

    logger.info("Writing EPUB file...")
    epub.write_epub(output_path, book)

    logger.success(f"Successfully created: {output_path}")
    return output_path


def chinese_num_to_arabic(chinese_num):
    """
    Convert Chinese numerals to Arabic numerals.
    Examples: 十二 -> 12, 一百二十三 -> 123, 两百 -> 200
    """
    if chinese_num.isdigit():
        return int(chinese_num)
    
    digit_map = {
        '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9
    }
    
    unit_map = {
        '十': 10,
        '百': 100,
        '千': 1000,
        '万': 10000
    }
    
    result = 0
    temp_num = 0
    
    for i, char in enumerate(chinese_num):
        if char in digit_map:
            temp_num = digit_map[char]
        elif char in unit_map:
            unit = unit_map[char]
            if char == '十' and i == 0:
                temp_num = 1
            result += temp_num * unit
            temp_num = 0
        elif char == '零':
            continue
    
    result += temp_num
    
    return result if result > 0 else 0


def parse_chapters(content):
    """
    Parse chapters from content based on pattern like:
    第X章 chapter_title (where X can be Arabic or Chinese numerals)
    """
    logger.debug("Searching for chapter patterns...")
    # Pattern that matches both Arabic (第12章) and Chinese numerals (第十二章)
    chapter_pattern = re.compile(r"^第(.+?)章(.*)$", re.MULTILINE)

    matches = list(chapter_pattern.finditer(content))

    if not matches:
        logger.warning("No chapters found, treating entire content as one chapter")
        return [{"number": 1, "title": "Full Content", "content": content}]

    logger.debug(f"Found {len(matches)} chapter markers")
    chapters = []

    for i, match in enumerate(matches):
        chapter_num_str = match.group(1).strip()
        chapter_title = match.group(2).strip()

        # Convert chapter number (handles both Arabic and Chinese numerals)
        try:
            chapter_num = chinese_num_to_arabic(chapter_num_str)
        except Exception as e:
            logger.warning(f"Could not parse chapter number: {chapter_num_str}, using index. Error: {e}")
            chapter_num = i + 1

        start_pos = match.end()

        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        chapter_content = content[start_pos:end_pos].strip()

        logger.debug(
            f"Parsed chapter {chapter_num}: {chapter_title} ({len(chapter_content)} chars)"
        )

        chapters.append(
            {
                "number": chapter_num,
                "title": chapter_title,
                "content": chapter_content,
            }
        )

    return chapters


def create_epub(book_title, chapters, author="Unknown Author"):
    """
    Create an EPUB book from parsed chapters.
    """
    logger.debug("Initializing EPUB book structure")
    book = epub.EpubBook()

    book.set_identifier(f"id_{book_title}")
    book.set_title(book_title)
    book.set_language("zh")

    book.add_author(author)

    epub_chapters = []
    spine = ["nav"]

    logger.debug("Creating EPUB chapters...")
    for chapter in chapters:
        chapter_file = f"chap_{chapter['number']}.xhtml"

        chapter_html = f"""
        <html>
        <head>
            <title>{chapter["title"]}</title>
        </head>
        <body>
            <h1>第{chapter["number"]}章 {chapter["title"]}</h1>
            {"".join(f"<p>{para}</p>" for para in chapter["content"].split("\n") if para.strip())}
        </body>
        </html>
        """

        epub_chapter = epub.EpubHtml(
            title=f"第{chapter['number']}章 {chapter['title']}",
            file_name=chapter_file,
            lang="zh",
        )
        epub_chapter.content = chapter_html

        book.add_item(epub_chapter)
        epub_chapters.append(epub_chapter)
        spine.append(epub_chapter)

    logger.debug("Setting up table of contents and navigation")
    book.toc = tuple(epub_chapters)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = spine

    return book


if __name__ == "__main__":
    fire.Fire(txt_to_epub)
