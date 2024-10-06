from tkinter import Tk, Label, Entry, Button, StringVar, Toplevel, IntVar
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showerror, askquestion
from tkinter.ttk import Progressbar
from os import makedirs, startfile, popen
from os import path as _path
from sys import platform, builtin_module_names
from shutil import copy, rmtree
from random import choice
from re import MULTILINE, findall
from tempfile import gettempdir
from platform import system
from pathlib import Path
from shutil import copy
from subprocess import run, DEVNULL, CalledProcessError
from platform import system
from threading import Thread
from importlib.util import find_spec

# Functions
def gen_randenc():
    string = ''.join(choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(20))
    return string

def is_builtin_or_installed(module_name):
    if module_name in builtin_module_names:
        return True
    loader = find_spec(module_name)
    return loader is not None

def get_imports_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        raise Exception("[ProgramCompiler] Ошибка: файл должен быть в кодировке UTF-8")
    imports = findall(r'^\s*(?:import|from)\s+([^\s.]+)', content, MULTILINE)
    filtered_imports = {module for module in imports if not is_builtin_or_installed(module)}
    return filtered_imports

def install_missing_libraries(imports):
    for lib in imports:
        try:
            run(f"pip show {lib}", shell=True, check=True, stdout=DEVNULL)
            print(f"[ProgramCompiler] Библиотека {lib} уже установлена.")
        except CalledProcessError:
            print(f"[ProgramCompiler] Установка библиотеки {lib}...")
            run(f"pip install {lib}", shell=True, check=True)
            print(f"[ProgramCompiler] Библиотека {lib} успешно установлена.")

def choosedir(path: str):
    temppath = gettempdir()
    appname = _path.basename(path)[:-3]
    programdest = gen_randenc()
    dest_dir = _path.join(temppath, programdest)
    build_dir = _path.join(dest_dir, 'build')
    dist_dir = _path.join(dest_dir, 'application')
    return temppath, appname, programdest, dest_dir, build_dir, dist_dir

def return_homepath() -> str:
    return Path.home()

def openfolder(path) -> str:
    if system() == "Windows":
        startfile(path)
    elif system() == "Darwin":
        popen(["open", path])
    else:
        popen(["xdg-open", path])

# Main
class Main(Tk):
    def __init__(self):
        super().__init__()
        self.title('ProgramCompiler')
        self.main()
    
    def main(self):
        path: StringVar = StringVar()
        Label(self, text='Путь к файлу: ').grid(row=0, column=0, padx=5, pady=5)
        Entry(textvariable=path).grid(row=0, column=1, padx=5, pady=5)
        Button(text="Выбрать", command=lambda: self.openfile(path)).grid(row=0, column=2, padx=5, pady=5)
        Button(text="Собрать", command=lambda: self.compile(path)).grid(row=1, column=1, padx=5, pady=5)
    
    def openfile(self, path):
        file = askopenfile(initialdir=return_homepath(), title="Выберите файл")

        if file is not None:
            path.set(file.name)
    
    def compile(self, path):
        compilewin = Toplevel(self)
        compilewin.title('Компиляция...')
        pbprogress: IntVar = IntVar()
        pbtext: StringVar = StringVar()
        Progressbar(compilewin, orient='horizontal', length=100, variable=pbprogress).grid(row=0, column=0, padx=5, pady=5)
        Label(compilewin, textvariable=pbtext).grid(row=1, column=0, padx=5, pady=5)
        pbprogress.set(0)
        pbtext.set('Определяем пути...')
        def compile_in_background():
            try:
                ch = choosedir(path.get())  
                appname = ch[1]
                dest_dir = ch[3]
                build_dir = ch[4]
                dist_dir = ch[5]

                pbprogress.set(14)
                pbtext.set("Создаём директории...")
                makedirs(build_dir, exist_ok=True)
                makedirs(dist_dir, exist_ok=True)

                pbprogress.set(28)
                pbtext.set("Создаем виртуальную среду...")
                run(['python', '-m', 'venv', 'venv'], check=True)

                pbprogress.set(42)
                pbtext.set("Активируем среду...")
                if platform == 'win32':
                    activate_script = _path.join('venv', 'Scripts', 'activate.bat')
                else:
                    activate_script = _path.join('venv', 'bin', 'activate')
                run(f'{activate_script}', shell=True, check=True)

                pbprogress.set(56)
                pbtext.set("Устанавливаем библиотеки...")
                run(f'pip install pyinstaller', shell=True, check=True)

                imports = get_imports_from_file(path.get())  
                install_missing_libraries(imports)

                pbprogress.set(70)
                pbtext.set("Собираем приложение...")
                pyinstaller_cmd = f'pyinstaller --clean --noconfirm --onefile --console "{path.get()}" --distpath "{dist_dir}" --workpath "{build_dir}" --specpath "{dest_dir}" --name "{appname}"'
                run(pyinstaller_cmd, shell=True, check=True)

                pbprogress.set(84)
                pbtext.set("Копируем исполняющий файл...")
                script_dir = _path.dirname(_path.abspath(__file__))
                build_output_dir = _path.join(script_dir, 'build')
                makedirs(build_output_dir, exist_ok=True)
                exe_file = _path.join(dist_dir, f'{appname}.exe')
                copy(exe_file, build_output_dir)
                rmtree(dest_dir)
                rmtree('venv')

                pbprogress.set(100)
                pbtext.set("Готово!")

                result = askquestion('Готово!', f'Программа успешно собрана!\n\n Местоположение: {build_output_dir} \n\n Не желаете открыть папку сборки?')
                if result == 'yes':
                    openfolder(build_output_dir)
                else:
                    pass
                compilewin.destroy()

            except Exception as err:
                showerror('Ошибка!', f"Ошибка сборки: {str(err)}")
                compilewin.destroy()

        Thread(target=compile_in_background).start()

if __name__ == "__main__":
    Main().mainloop()