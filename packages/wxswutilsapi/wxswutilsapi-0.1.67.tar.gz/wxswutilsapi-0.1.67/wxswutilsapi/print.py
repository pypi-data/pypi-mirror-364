import os
import platform
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from tempfile import NamedTemporaryFile


def generate_pdf_from_lines(lines: list[str], output_path: str, lines_per_page: int = 40):
    """将文本行写入 PDF 文件，并自动分页"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin_top = 40
    line_height = 15
    x = 40
    y = height - margin_top

    for i, line in enumerate(lines):
        if i != 0 and i % lines_per_page == 0:
            c.showPage()
            y = height - margin_top
        c.drawString(x, y - (i % lines_per_page) * line_height, line)

    c.save()


def print_file(pdf_path: str):
    """跨平台打印 PDF 文件"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"文件未找到: {pdf_path}")

    system = platform.system()
    try:
        if system == "Windows":
            # 使用系统命令打开 PDF（默认会调起打印对话框或使用默认打印机）
            print_cmd = f'rundll32.exe shell32.dll,ShellExec_RunDLL "{pdf_path}"'
            subprocess.run(print_cmd, shell=True, check=True)
        elif system in ["Linux", "Darwin"]:
            subprocess.run(["lp", pdf_path], check=True)
        else:
            raise RuntimeError(f"不支持的操作系统: {system}")
    except Exception as e:
        print(f"打印失败: {e}")
        raise


def print_lines_as_pdf(lines: list[str], lines_per_page: int = 40):
    """将文本行写为 PDF 并发送至打印机"""
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_path = tmp_file.name
    try:
        generate_pdf_from_lines(lines, tmp_path, lines_per_page)
        print_file(tmp_path)
    finally:
        os.remove(tmp_path)
