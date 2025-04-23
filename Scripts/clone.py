import os
import shutil
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

def create_project_structure(clone_dir):
    """Создает базовую структуру проекта"""
    try:
        # Создаем папку sources, если её нет
        sources_dir = os.path.join(clone_dir, 'sources')
        if not os.path.exists(sources_dir):
            os.makedirs(sources_dir)
        
        # Создаем README.md с базовым содержимым
        readme_path = os.path.join(clone_dir, 'README.md')
        if not os.path.exists(readme_path):
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("## Проект\n\nОписание проекта\n\n## Заказчик\n\nИнформация о заказчике\n")
        
        return True
    except Exception as e:
        print(f"Ошибка при создании структуры проекта: {e}")
        return False

def clone_and_clean():
    root = tk.Tk()
    root.withdraw()
    
    # Выбираем исходную папку
    source_dir = filedialog.askdirectory(title="Выберите исходную папку для клонирования")
    if not source_dir:
        return
    
    # Выбираем целевую папку
    target_parent_dir = filedialog.askdirectory(title="Выберите папку, в которую нужно поместить клон")
    if not target_parent_dir:
        return
    
    # Создаём имя для клона
    base_name = os.path.basename(source_dir)
    clone_dir = None
    index = 1
    
    # Ищем свободное имя для клона
    while True:
        new_name = f"{base_name}_{index}" if index > 1 else base_name
        clone_dir = os.path.join(target_parent_dir, new_name)
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
        
        # Создаем базовую структуру проекта
        structure_created = create_project_structure(clone_dir)
        if not structure_created:
            raise Exception("Не удалось создать структуру проекта")
        
        # Записываем лог
        log_message = (
            f"Клон создан: {clone_dir}\n"
            f"Исходная папка: {source_dir}\n"
            f"Удалено файлов/папок: {deleted_count}\n"
            f"Сохранено:\n"
            f"- Все .tex файлы\n"
            f"- Папка images (если существовала)\n"
            f"Создано:\n"
            f"- Папка sources\n"
            f"- Файл README.md\n"
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
            f"Создана папка sources и README.md\n"
            f"Git-история удалена"
        )
    except Exception as e:
        messagebox.showerror(
            "Ошибка!",
            f"Не удалось создать клон:\n{str(e)}"
        )

if __name__ == "__main__":
    clone_and_clean()