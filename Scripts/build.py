import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import re
import signal

# Расширения временных файлов для удаления
LATEX_CLEAN_EXTENSIONS = [
    '.aux', '.out', '.toc', '.lof', '.lot',
    '.bbl', '.blg', '.synctex.gz', '.fls',
    '.fdb_latexmk', '.run.xml', '.bcf'
]

def print_step(message):
    """Выводит сообщение о текущем шаге выполнения"""
    print(f"▶ {message}...")

def compile_latex(tex_path, compiler='xelatex'):
    """Функция компиляции с обработкой ошибок."""
    working_dir = tex_path.parent
    log_file = tex_path.with_suffix('.log')
    pdf_file = tex_path.with_suffix('.pdf')
    
    print_step(f"Компиляция файла {tex_path.name} с помощью {compiler}")
    
    # Очистка старых временных файлов
    print_step("Очистка временных файлов")
    clean_directory(working_dir)
    
    try:
        # Первая компиляция с таймаутом
        print_step("Запуск первой компиляции")
        try:
            proc = subprocess.Popen(
                [compiler, '-interaction=nonstopmode', '-halt-on-error',
                 '-file-line-error', str(tex_path.name)],
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # Убрали text=True и явное указание кодировки
                universal_newlines=True  # Для совместимости
            )
            stdout, stderr = proc.communicate(timeout=60)
            
            # Декодируем вывод с учетом возможных ошибок
            def safe_decode(byte_str):
                try:
                    return byte_str.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return byte_str.decode('cp1251')
                    except UnicodeDecodeError:
                        return byte_str.decode('cp866', errors='replace')
            
            if isinstance(stdout, bytes):
                stdout = safe_decode(stdout)
            if isinstance(stderr, bytes):
                stderr = safe_decode(stderr)
                
            print("✓ Первая компиляция завершена")
        except subprocess.TimeoutExpired:
            proc.kill()
            print("✗ Превышено время компиляции (60 сек)")
            return False, "Превышено время компиляции (60 сек)"
        
        # Сохранение логов
        print_step("Сохранение логов компиляции")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Компилятор: {compiler} ===\n")
            f.write("=== STDOUT ===\n")
            if stdout:
                f.write(stdout)
            f.write("\n=== STDERR ===\n")
            if stderr:
                f.write(stderr)
        
        # Остальной код функции остается без изменений
        # ...
        
        # Проверка ошибок
        if proc.returncode != 0:
            print("✗ Обнаружены ошибки компиляции")
            error_msg = extract_errors(stdout + stderr)
            return False, error_msg
        
        # Вторая компиляция для ссылок и оглавления
        print_step("Запуск второй компиляции (для ссылок и оглавления)")
        try:
            proc = subprocess.Popen(
                [compiler, '-interaction=nonstopmode', str(tex_path.name)],
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            stdout, stderr = proc.communicate(timeout=30)
            print("✓ Вторая компиляция завершена")
        except subprocess.TimeoutExpired:
            proc.kill()
            print("✗ Превышено время второй компиляции")
            return False, "Превышено время второй компиляции"
        
        if not pdf_file.exists():
            print("✗ PDF файл не был создан")
            return False, "PDF не был создан"
            
        print(f"✓ PDF успешно создан: {pdf_file}")
        return True, f"PDF успешно создан: {pdf_file}"

    except Exception as e:
        print(f"✗ Системная ошибка: {str(e)}")
        return False, f"Системная ошибка: {str(e)}"

def extract_errors(log_text):
    """Извлекает ключевые ошибки из лога."""
    print_step("Анализ логов на наличие ошибок")
    error_lines = [
        line for line in log_text.split('\n')
        if any(keyword in line.lower() for keyword in ['error', '!'])
    ]
    return "\n".join(error_lines[-10:]) if error_lines else "Неизвестная ошибка компиляции"

def clean_directory(directory):
    """Удаление временных файлов LaTeX."""
    print_step(f"Очистка временных файлов в {directory}")
    for ext in LATEX_CLEAN_EXTENSIONS:
        for file in directory.glob(f'*{ext}'):
            try:
                file.unlink()
                print(f"  Удален: {file.name}")
            except Exception as e:
                print(f"  Ошибка удаления {file}: {e}")

def show_error_details(log_content):
    """Окно с детализацией ошибок."""
    print_step("Отображение деталей ошибки")
    root = tk.Tk()
    root.title("Детали ошибки компиляции")
    
    def on_closing():
        root.destroy()
        root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
    text.pack(padx=10, pady=10)
    text.insert(tk.END, log_content)
    text.configure(state='disabled')
    
    tk.Button(root, text="Закрыть", command=on_closing).pack(pady=5)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()

def select_compiler():
    """Диалог выбора компилятора."""
    print_step("Выбор компилятора")
    root = tk.Tk()
    root.withdraw()
    choice = messagebox.askyesno(
        "Выбор компилятора",
        "Использовать XeLaTeX? (Нет - будет использован pdfLaTeX)",
        icon='question'
    )
    compiler = 'xelatex' if choice else 'pdflatex'
    print(f"Выбран компилятор: {compiler}")
    return compiler

def main():
    print("="*50)
    print("LaTeX компилятор с выводом хода выполнения")
    print("="*50)
    
    try:
        # Инициализация GUI
        print_step("Инициализация интерфейса")
        root = tk.Tk()
        root.withdraw()

        # Выбор файла
        print_step("Выбор .tex файла")
        tex_file = filedialog.askopenfilename(
            title="Выберите .tex файл",
            filetypes=[("LaTeX files", "*.tex"), ("All files", "*.*")]
        )
        if not tex_file:
            print("Файл не выбран, выход")
            return

        tex_path = Path(tex_file)
        print(f"Выбран файл: {tex_path}")

        # Выбор компилятора
        compiler = select_compiler()

        # Компиляция
        print("\nНачало процесса компиляции:")
        success, message = compile_latex(tex_path, compiler)
        
        # Отображение результата
        if success:
            print("\nРезультат: Успешно!")
            messagebox.showinfo("Успех", message)
        else:
            print("\nРезультат: Ошибка!")
            log_file = tex_path.with_suffix('.log')
            if log_file.exists():
                print_step("Чтение лог-файла")
                with open(log_file, 'r', encoding='utf-8') as f:
                    show_error_details(f.read())
            else:
                messagebox.showerror("Ошибка", message)
                
    except Exception as e:
        print(f"\n✗ Критическая ошибка: {str(e)}")
    finally:
        print("\nЗавершение работы программы")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма была прервана пользователем")
    except Exception as e:
        print(f"\nПроизошла ошибка: {str(e)}")