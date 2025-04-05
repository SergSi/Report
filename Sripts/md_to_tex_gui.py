import re
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

def convert_markdown_to_tex(md_file_path):
    """Конвертирует Markdown в чистый LaTeX-контент"""
    try:
        # Чтение и обработка файла
        content = Path(md_file_path).read_text(encoding='utf-8')
        
        # Удаление YAML front matter
        content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
        
        # Преобразование заголовков (без звёздочки для оглавления)
        content = re.sub(r'^# (.*?)\s*$', r'\\section{\1}', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*?)\s*$', r'\\subsection{\1}', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.*?)\s*$', r'\\subsubsection{\1}', content, flags=re.MULTILINE)
        
        # Очистка от HTML и спецсимволов
        content = re.sub(r'&[#\w]+;', '', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'([_$&%#])', r'\\\1', content)
        
        # Сохранение результата
        output_path = Path(md_file_path).parent / "content.tex"
        output_path.write_text(content.strip(), encoding='utf-8')
        
        return f"Файл успешно сохранён: {output_path}"
    
    except Exception as e:
        return f"Ошибка конвертации: {str(e)}"

# ... (остальной код конвертера без изменений)

def select_and_convert():
    """Графический интерфейс для выбора файла."""
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Выберите Markdown-файл",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
    )
    
    if not file_path:
        messagebox.showinfo("Информация", "Конвертация отменена")
        return
    
    result = convert_markdown_to_tex(file_path)
    messagebox.showinfo("Результат", result)

if __name__ == "__main__":
    select_and_convert()