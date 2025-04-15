import os
import shutil
import glob
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def clean_directory(target_dir):
    """Оставляет только .tex файлы и папку images, удаляет всё остальное"""
    preserved_items = []
    deleted_count = 0
    
    # Сохраняем все .tex файлы (включая вложенные)
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.tex'):
                rel_path = os.path.relpath(os.path.join(root, file), target_dir)
                preserved_items.append(rel_path)
    
    # Сохраняем папку images (если существует)
    images_path = os.path.join(target_dir, 'images')
    if os.path.isdir(images_path):
        preserved_items.append('images')
    
    # Удаляем всё, кроме сохранённых элементов
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        
        # Проверяем, нужно ли сохранить этот элемент
        should_preserve = False
        for preserved in preserved_items:
            if item == preserved or preserved.startswith(item + os.sep):
                should_preserve = True
                break
                
        if should_preserve:
            continue
            
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                deleted_count += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                deleted_count += 1
        except Exception as e:
            print(f"Ошибка при удалении {item_path}: {e}")
    
    return deleted_count

def clone_and_clean():
    root = tk.Tk()
    root.withdraw()
    
    # Выбираем исходную папку
    source_dir = filedialog.askdirectory(title="Выберите папку для клонирования")
    if not source_dir:
        return
    
    # Создаём имя для клона
    base_name = os.path.basename(source_dir)
    clone_dir = None
    index = 1
    
    # Ищем свободное имя для клона
    while True:
        new_name = f"{base_name}_{index}"
        clone_dir = os.path.join(os.path.dirname(source_dir), new_name)
        if not os.path.exists(clone_dir):
            break
        index += 1
    
    try:
        # Копируем папку, игнорируя .git
        shutil.copytree(
            source_dir,
            clone_dir,
            ignore=shutil.ignore_patterns('.git', '.gitignore', '.gitattributes')
        )
        
        # Очищаем клон
        deleted_count = clean_directory(clone_dir)
        
        # Записываем лог
        log_message = (
            f"Клон создан: {clone_dir}\n"
            f"Исходная папка: {source_dir}\n"
            f"Удалено файлов/папок: {deleted_count}\n"
            f"Сохранено:\n"
            f"- Все .tex файлы\n"
            f"- Папка images (если существовала)\n"
            f"Git-история удалена\n"
            f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        with open(os.path.join(clone_dir, "clone_log.txt"), "w") as f:
            f.write(log_message)
        
        messagebox.showinfo(
            "Успешно!",
            f"Папка успешно клонирована и очищена:\n{clone_dir}\n"
            f"Удалено файлов/папок: {deleted_count}\n"
            f"Сохранены только .tex файлы и папка images\n"
            f"Git-история удалена"
        )
    except Exception as e:
        messagebox.showerror(
            "Ошибка!",
            f"Не удалось создать клон:\n{str(e)}"
        )

if __name__ == "__main__":
    clone_and_clean()