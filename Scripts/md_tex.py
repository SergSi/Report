import os
import subprocess
import sys
from tkinter import Tk, filedialog, messagebox
from tkinter.ttk import Progressbar, Label, Button
import shutil


class PandocConverter:
    def __init__(self):
        self.root = Tk()
        self.root.title("MD to LaTeX Converter")
        self.root.geometry("500x200")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Проверяем доступность Pandoc при запуске
        self.pandoc_path = self.find_pandoc()
        if not self.pandoc_path:
            messagebox.showerror(
                "Ошибка", 
                "Pandoc не найден!\n\n"
                "Установите Pandoc и добавьте его в PATH:\n"
                "https://pandoc.org/installing.html\n\n"
                "Или поместите pandoc.exe в папку с программой."
            )
            sys.exit(1)
            
        self.setup_ui()
        self.is_running = False
        self.process = None
        self.should_exit = False

    def find_pandoc(self):
        """Поиск pandoc в системе"""
        # Сначала проверяем в папке с EXE (для собранной версии)
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            local_pandoc = os.path.join(exe_dir, 'pandoc')
            if os.path.exists(local_pandoc + '.exe' if sys.platform == 'win32' else local_pandoc):
                return local_pandoc
        
        # Проверяем в PATH
        pandoc_path = shutil.which('pandoc')
        if pandoc_path:
            return pandoc_path
            
        return None

    def setup_ui(self):
        """Настройка графического интерфейса"""
        self.status_label = Label(self.root, text=f"Pandoc найден: {self.pandoc_path}")
        self.status_label.pack(pady=10)
        
        self.progress = Progressbar(self.root, mode='indeterminate')
        
        self.select_button = Button(
            self.root, 
            text="Выбрать Markdown файл", 
            command=self.select_and_convert
        )
        self.select_button.pack(pady=15)
        
        self.cancel_button = Button(
            self.root,
            text="Отмена",
            command=self.cancel_operation,
            state='disabled'
        )
        self.cancel_button.pack(pady=5)

    def on_close(self):
        """Обработчик закрытия окна"""
        if self.is_running:
            if messagebox.askokcancel("Выход", "Конвертация в процессе. Прервать и выйти?"):
                self.should_exit = True
                self.cancel_operation()
                self.root.destroy()
        else:
            self.root.destroy()

    def cancel_operation(self):
        """Прерывание текущей операции"""
        if self.is_running and self.process:
            self.process.terminate()
            self.status_label.config(text="Операция прервана")
            self.is_running = False
            self.progress.stop()
            self.progress.pack_forget()
            self.cancel_button.config(state='disabled')

    def select_and_convert(self):
        """Выбор файла и запуск конвертации"""
        if self.is_running:
            return
            
        file_path = filedialog.askopenfilename(
            title="Выберите Markdown файл",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if not file_path:
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Файл не существует!")
            return
            
        self.start_conversion(file_path)

    def start_conversion(self, md_file):
        """Запуск процесса конвертации"""
        self.is_running = True
        self.cancel_button.config(state='normal')
        self.progress.pack(pady=10)
        self.progress.start()
        self.status_label.config(text=f"Конвертация: {os.path.basename(md_file)}")
        
        tex_file = os.path.splitext(md_file)[0] + '.tex'
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            cmd = [self.pandoc_path, '-f', 'markdown', '-t', 'latex', '--wrap=none']
            
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            stdout, stderr = self.process.communicate(input=md_content, timeout=300)
            
            if self.process.returncode == 0:
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(stdout)
                
                self.status_label.config(text=f"Готово: {os.path.basename(tex_file)}")
                messagebox.showinfo(
                    "Успешно", 
                    f"Файл успешно конвертирован:\n{tex_file}"
                )
            else:
                self.status_label.config(text="Ошибка конвертации")
                messagebox.showerror(
                    "Ошибка Pandoc",
                    f"{stderr[:500] if stderr else 'Неизвестная ошибка'}"
                )
                
        except subprocess.TimeoutExpired:
            if self.process:
                self.process.kill()
            self.status_label.config(text="Таймаут операции")
            messagebox.showerror("Ошибка", "Превышено время выполнения")
        except Exception as e:
            self.status_label.config(text="Ошибка обработки")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
        finally:
            self.is_running = False
            self.progress.stop()
            self.progress.pack_forget()
            self.cancel_button.config(state='disabled')
            self.process = None

            if self.should_exit:
                self.root.destroy()

    def run(self):
        """Запуск основного цикла"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_close()


if __name__ == "__main__":
    converter = PandocConverter()
    converter.run()