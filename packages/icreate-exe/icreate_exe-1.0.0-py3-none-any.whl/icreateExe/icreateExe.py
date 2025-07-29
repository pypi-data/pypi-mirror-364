from argparse import ArgumentParser
import sys
import os
import shutil
import glob

class CustomArgumentParser(ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Ошибка: {message}", file=sys.stderr)
        sys.exit(1)

def icreateExe():
    # Получаем аргументы из командной строки
    parser = CustomArgumentParser(description="Код для создания exe файла из .py")
    parser.add_argument('-i', help='Путь до иконки')
    parser.add_argument('name_file', help='Путь до файла')
    args = parser.parse_args()

    # Выполняем комманду pyinstaller
    path_to_icon = args.i
    path_to_file = args.name_file
    if path_to_icon is None:
        command = f'pyinstaller --noconfirm --onefile --windowed {path_to_file}'
    else:
        command = f'pyinstaller --noconfirm --onefile --windowed --icon {path_to_icon} {path_to_file}'
    os.system(command)

    exe_file = os.listdir('./dist/')[0]
    # Удаляем файлы 
    if os.name == 'nt':  # Windows
        os.system('move .\\dist\\* .\\')
        os.system('rmdir /s /q build dist')
        os.system('del *.spec')
    else:  # Unix-системы (Linux, macOS)
        os.system('mv ./dist/* ./')
        shutil.rmtree('build', ignore_errors=True)
        shutil.rmtree('dist', ignore_errors=True)
        for spec_file in glob.glob('*.spec'):
            os.remove(spec_file)
    print(f'\nФайл {exe_file} был создан')

if __name__ == "__main__":
    icreateExe()
