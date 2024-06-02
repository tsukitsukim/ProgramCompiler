import os
import tempfile
import random
import shutil
import subprocess
import sys

def gen_randenc():
    # Generate a random alphanumeric string of length 20
    string = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(20))
    print(f"[ProgramCompiler] Создан рандомный код: {string}")
    return string

def main():
    print('-----------------[ProgramCompiler v0.5 by Plizik]-----------------')
    path = input("[ProgramCompiler] Введите путь к файлу: ").strip()
    req_lib = input("[ProgramCompiler] Введите требуемые библиотеки через запятую (если нет, оставьте пустым): ").strip()
    try:
        # Define paths
        temppath = tempfile.gettempdir()  # Temporary directory path
        appname = os.path.basename(path)[:-3]  # Extract application name without the .py extension
        programdest = gen_randenc()  # Generate random directory name
        dest_dir = os.path.join(temppath, programdest)  # Destination directory path
        build_dir = os.path.join(dest_dir, 'build')  # Build directory path
        dist_dir = os.path.join(dest_dir, 'application')  # Distribution directory path
        liblist = [lib.strip() for lib in req_lib.split(',')] if req_lib else []  # List of required libraries

        # Print paths and library list
        print(f"[ProgramCompiler] Временный путь: {temppath}")
        print(f"[ProgramCompiler] Название приложения: {appname}")
        print(f"[ProgramCompiler] Путь расположения: {dest_dir}")
        print(f"[ProgramCompiler] Путь сборки: {build_dir}")
        print(f"[ProgramCompiler] Путь дистрибутива: {dist_dir}")
        print(f'[ProgramCompiler] Требуемые библиотеки для установки: {liblist}')

        # Create necessary directories
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(dist_dir, exist_ok=True)

        # Create virtual environment
        print('[ProgramCompiler] Создаём виртуальную среду для программы...')
        subprocess.run(['python', '-m', 'venv', 'venv'], check=True)
        
        # Path to the activate script
        if os.name == 'nt':  # Windows
            activate_script = os.path.join('venv', 'Scripts', 'activate.bat')
        else:  # Unix-like (Linux, macOS, etc.)
            activate_script = os.path.join('venv', 'bin', 'activate')

        # Install required libraries
        print('[ProgramCompiler] Загружаем библиотеки...')
        subprocess.run(f'{activate_script} && pip install pyinstaller', shell=True, check=True)

        for lib in liblist:
            try:
                subprocess.run(f'{activate_script} && pip install {lib}', shell=True, check=True)
                print(f'[ProgramCompiler] Библиотека {lib} установлена.')
            except subprocess.CalledProcessError as e:
                print(f"[ProgramCompiler] Ошибка установки библиотеки {lib}: {e}")

        # Build the application with PyInstaller
        pyinstaller_cmd = f'{activate_script} && pyinstaller --noconfirm --onefile --console "{path}" --distpath "{dist_dir}" --workpath "{build_dir}" --specpath "{dest_dir}"'
        print(f"[ProgramCompiler] Запускаем команду: {pyinstaller_cmd}")
        subprocess.run(pyinstaller_cmd, shell=True, check=True)

        # Path to the output directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        build_output_dir = os.path.join(script_dir, 'build')
        os.makedirs(build_output_dir, exist_ok=True)

        # Path to the executable file
        exe_file = os.path.join(dist_dir, f'{appname}.exe')
        print(f"[ProgramCompiler] Ищем exe-файл: {exe_file}")

        if not os.path.exists(exe_file):
            raise FileNotFoundError(f"[ProgramCompiler] Exe-файл не найден: {exe_file}")

        # Copy the executable to the build directory
        shutil.copy(exe_file, build_output_dir)
        print(f"[ProgramCompiler] Exe-файл скопирован в {build_output_dir}")

        # Clean up temporary directories
        shutil.rmtree(dest_dir)
        print('[ProgramCompiler] Удалена кеш-папка')

        # Remove the virtual environment
        shutil.rmtree('venv')
        print('[ProgramCompiler] Удалена виртуальная среда для экономии места. Она встроена в exe-файл.')

        print(f'\n\n[ProgramCompiler] Сборка программы {appname}.exe успешно завершена.')
    except Exception as err:
        print(f"[ProgramCompiler] Ошибка обработки файла: {err}")
        input("Нажмите Enter для закрытия консоли...")

if __name__ == "__main__":
    main()
    input("Нажмите Enter для закрытия консоли...")

