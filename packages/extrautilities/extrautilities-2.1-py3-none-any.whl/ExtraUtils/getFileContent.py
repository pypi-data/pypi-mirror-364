import os, sys,glob,fnmatch,importlib.resources,re
from pathlib import Path

def isinDev():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return False
    else:
        return True


def getFileContent(filePath):
    if isinDev():
        with open(os.path.join(Path.cwd(), filePath), "r", encoding="utf-8") as file:
            return file.read()
    if not isinDev():
        # Split the file path into a package name and a file name
        package_path, file_name = os.path.split(filePath)
        # Convert the package path to a Python module format
        package_name = package_path.lstrip('/').replace('/', '.')
        try:
            return importlib.resources.read_text(package_name, file_name)
        except ModuleNotFoundError:
            print(f"Module '{package_name}' not found")
            return None
        
def getFilePath(filePath):
    if isinDev():
        return str(Path.cwd()) + filePath
    if not isinDev():
        package_path, file_name = os.path.split(filePath)
        # Directly replace '/' with '.'
        package_name = package_path.lstrip('/').replace('/', '.')
        with importlib.resources.path(package_name, file_name) as res_path:
            return str(res_path)

def getMultipleFileContent(globExpression):
    globExpression = globExpression.lstrip('/')
    fileContents = []
    correspondingFilePaths = []  

    if isinDev():
        file_paths = glob.glob(globExpression, recursive=True)
        for file_path in file_paths:
            with open(file_path, "r", encoding="utf-8") as file:
                fileContents.append(file.read())
            correspondingFilePaths.append(file_path.replace('\\', '/'))
    else:
        package_path, file_pattern = os.path.split(globExpression)
        package_name = package_path.replace('/', '.')
        try:
            all_files = importlib.resources.contents(package_name)
        except ModuleNotFoundError:
            print(f"Module '{package_name}' not found")
            return (fileContents, correspondingFilePaths)
        for file_name in all_files:
            if fnmatch.fnmatch(file_name, file_pattern):
                try:
                    with importlib.resources.path(package_name, file_name) as res_path:
                        with open(str(res_path), "r", encoding="utf-8") as file:
                            content = file.read()
                        fileContents.append(content)
                        path = package_name.replace('.', '/') + '/' + file_name
                        correspondingFilePaths.append(path)
                except (FileNotFoundError, UnicodeDecodeError):
                    print(f"File '{file_name}' not found or not a text file")
    return (fileContents, correspondingFilePaths)
    

