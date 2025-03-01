import fitz  # PyMuPDF
import fire
import os


def split_pdf(input_pdf: str, output_dir: str):
    """
    将多页 PDF 拆分成单页 PDF 并保存到指定文件夹。

    :param input_pdf: 输入的 PDF 文件路径。
    :param output_dir: 输出文件夹路径。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        output_path = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
        new_doc.save(output_path)
        new_doc.close()
        print(f"Saved: {output_path}")

    doc.close()
    print("PDF 拆分完成。")


if __name__ == "__main__":
    fire.Fire(split_pdf)
