from pathlib import Path




def create_folder(folder_path: str) -> None:
    """
    Create a folder if it does not exist.

    :param folder_path: Path to the folder to be created.
    """
    path = Path(folder_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Folder created: {path}")
    else:
        print(f"Folder already exists: {path}")


def create_folders(folders: list) -> None:
    """
    Create multiple folders if they do not exist.

    :param folders: List of folder paths to be created.
    """
    for folder in folders:
        create_folder(folder)


def remove_folder(folder_path: str) -> None:
    """
    Remove a folder recursively if it exists, even if it is not empty.

    :param folder_path: Path to the folder to be removed.
    """
    path = Path(folder_path)
    
    if not path.exists() or not path.is_dir():
        print(f"Folder does not exist or is not a directory: {path}")
        return

    file_count = sum(1 for _ in path.glob('**/*') if _.is_file())
    folder_count = sum(1 for _ in path.glob('**/*') if _.is_dir())

    print(f"[delete_folder] The folder '{path.name}' has {file_count} files and {folder_count} folders. Continue y/n:")
    choice = input().strip().lower()

    if choice != 'y':
        print("Operation cancelled.")
        return

    for item in path.iterdir():
        if item.is_dir():
            remove_folder(item)
        else:
            item.unlink()

    path.rmdir()
    print(f"Folder removed: {path}")

def remove_folders(folders: list) -> None:
    """
    Remove multiple folders if they exist.

    :param folders: List of folder paths to be removed.
    """
    for folder in folders:
        remove_folder(folder)



def list_folders(folder_path: str) -> list:
    """
    List all folders in a given path.

    :param folder_path: Path to the directory to list folders from.
    :return: List of folder names in the specified path.
    """
    path = Path(folder_path)
    if path.exists() and path.is_dir():
        return [f.name for f in path.iterdir() if f.is_dir()]
    else:
        print(f"Path does not exist or is not a directory: {path}")
        return []
    


def folder_exists(folder_path: str) -> bool:
    """
    Check if a folder exists.

    :param folder_path: Path to the folder to check.
    :return: True if the folder exists, False otherwise.
    """
    path = Path(folder_path)
    exists = path.exists() and path.is_dir()
    print(f"Folder exists: {exists} for path: {path}")
    return exists


def get_folder_size(folder_path: str) -> int:
    """
    Get the size of a folder in bytes.

    :param folder_path: Path to the folder.
    :return: Size of the folder in bytes.
    """
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        print(f"Path does not exist or is not a directory: {path}")
        return 0
    
    total_size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
    print(f"Total size of folder '{path}': {total_size} bytes")
    return total_size


def copy_folder(src: str, dst: str) -> None:
    """
    Copy a folder from source to destination.

    :param src: Path to the source folder.
    :param dst: Path to the destination folder.
    """
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists() or not src_path.is_dir():
        print(f"Source folder does not exist or is not a directory: {src_path}")
        return
    
    if dst_path.exists():
        print(f"Destination folder already exists: {dst_path}")
        return
    
    dst_path.mkdir(parents=True, exist_ok=True)
    
    for item in src_path.iterdir():
        if item.is_dir():
            copy_folder(item, dst_path / item.name)
        else:
            (dst_path / item.name).write_bytes(item.read_bytes())
    
    print(f"Folder copied from {src_path} to {dst_path}")



def move_folder(src: str, dst: str) -> None:
    """
    Move a folder from source to destination.

    :param src: Path to the source folder.
    :param dst: Path to the destination folder.
    """
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists() or not src_path.is_dir():
        print(f"Source folder does not exist or is not a directory: {src_path}")
        return
    
    if dst_path.exists():
        print(f"Destination folder already exists: {dst_path}")
        return
    
    src_path.rename(dst_path)
    
    print(f"Folder moved from {src_path} to {dst_path}")



def rename_folder(old_name: str, new_name: str) -> None:
    """
    Rename a folder.

    :param old_name: Current name of the folder.
    :param new_name: New name for the folder.
    """
    old_path = Path(old_name)
    new_path = Path(new_name)
    
    if not old_path.exists() or not old_path.is_dir():
        print(f"Folder to rename does not exist or is not a directory: {old_path}")
        return
    
    if new_path.exists():
        print(f"New folder name already exists: {new_path}")
        return
    
    old_path.rename(new_path)
    
    print(f"Folder renamed from {old_path} to {new_path}")



def get_folder_info(folder_path: str) -> dict:
    """
    Get information about a folder.

    :param folder_path: Path to the folder.
    :return: Dictionary containing folder information.
    """
    path = Path(folder_path)
    
    if not path.exists() or not path.is_dir():
        print(f"Path does not exist or is not a directory: {path}")
        return {}
    
    info = {
        'name': path.name,
        'size': get_folder_size(folder_path),
        'exists': folder_exists(folder_path),
        'folders': list_folders(folder_path)
    }
    
    print(f"Folder info: {info}")
    return info


def touch_file(file_path: str) -> None:
    """
    Create a file if it does not exist, or update its last modified time.

    :param file_path: Path to the file to be touched.
    """
    path = Path(file_path)
    path.touch(exist_ok=True)
    print(f"File touched: {path}")




def remove_file(file_path: str) -> None:
    """
    Remove a file if it exists.

    :param file_path: Path to the file to be removed.
    """
    path = Path(file_path)
    if path.exists() and path.is_file():
        path.unlink()
        print(f"File removed: {path}")
    else:
        print(f"File does not exist or is not a file: {path}")


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    :param file_path: Path to the file to check.
    :return: True if the file exists, False otherwise.
    """
    path = Path(file_path)
    exists = path.exists() and path.is_file()
    print(f"File exists: {exists} for path: {path}")
    return exists



def rename_file(old_name: str, new_name: str) -> None:
    """
    Rename a file.

    :param old_name: Current name of the file.
    :param new_name: New name for the file.
    """
    old_path = Path(old_name)
    new_path = Path(new_name)
    
    if not old_path.exists() or not old_path.is_file():
        print(f"File to rename does not exist or is not a file: {old_path}")
        return
    
    if new_path.exists():
        print(f"New file name already exists: {new_path}")
        return
    
    old_path.rename(new_path)
    
    print(f"File renamed from {old_path} to {new_path}")


def move_file(src: str, dst: str) -> None:
    """
    Move a file from source to destination.

    :param src: Path to the source file.
    :param dst: Path to the destination file.
    """
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists() or not src_path.is_file():
        print(f"Source file does not exist or is not a file: {src_path}")
        return
    
    if dst_path.exists():
        print(f"Destination file already exists: {dst_path}")
        return
    
    src_path.rename(dst_path)
    
    print(f"File moved from {src_path} to {dst_path}")



def getfilesize(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    :param file_path: Path to the file.
    :return: Size of the file in bytes.
    """
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        print(f"Path does not exist or is not a file: {path}")
        return 0
    
    size = path.stat().st_size
    print(f"Size of file '{path}': {size} bytes")
    return size




def get_file_info(file_path: str) -> dict:
    """
    Get information about a file.

    :param file_path: Path to the file.
    :return: Dictionary containing file information.
    """
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        print(f"Path does not exist or is not a file: {path}")
        return {}
    
    info = {
        'name': path.name,
        'size': getfilesize(file_path),
        'exists': file_exists(file_path)
    }
    
    print(f"File info: {info}")
    return info

def list_files(folder_path: str) -> list:
    """
    List all files in a given folder.

    :param folder_path: Path to the directory to list files from.
    :return: List of file names in the specified path.
    """
    path = Path(folder_path)
    
    if not path.exists() or not path.is_dir():
        print(f"Path does not exist or is not a directory: {path}")
        return []
    
    files = [f.name for f in path.iterdir() if f.is_file()]
    print(f"Files in '{path}': {files}")
    return files


def copy_file(src: str, dst: str) -> None:
    """
    Copy a file from source to destination.

    :param src: Path to the source file.
    :param dst: Path to the destination file.
    """
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists() or not src_path.is_file():
        print(f"Source file does not exist or is not a file: {src_path}")
        return
    
    if dst_path.exists():
        print(f"Destination file already exists: {dst_path}")
        return
    
    dst_path.write_bytes(src_path.read_bytes())
    
    print(f"File copied from {src_path} to {dst_path}")


def currentdir() -> str:
    """
    Get the current working directory.

    :return: Path to the current working directory.
    """
    current_dir = Path.cwd()
    print(f"Current working directory: {current_dir}")
    return str(current_dir)


def get_perms() -> dict:
    """
    Get the permissions of the current user.

    :return: Dictionary containing the permissions of the current user.
    """
    import os
    import stat

    perms = {
        'read': os.access(os.getcwd(), os.R_OK),
        'write': os.access(os.getcwd(), os.W_OK),
        'execute': os.access(os.getcwd(), os.X_OK)
    }
    
    print(f"Current user permissions: {perms}")
    return perms



import os
import platform
import subprocess
import stat
from pathlib import Path

def set_perms(path: str, read=True, write=True, execute=False):
    path = Path(path)

    if not path.exists():
        print(f"Path does not exist: {path}")
        return

    system = platform.system()

    try:
        if system == "Windows":
            
            if not read and not write and not execute:
                cmd = ["icacls", str(path), "/deny", "everyone:(F)"]
            else:
                
                if read and write and execute:
                    perm = "F"
                elif read and write:
                    perm = "M"
                elif read:
                    perm = "R"
                elif write:
                    perm = "W"
                else:
                    perm = "R"
                subprocess.run(["icacls", str(path), "/remove:d", "everyone"], stdout=subprocess.DEVNULL)
                cmd = ["icacls", str(path), "/grant:r", f"everyone:({perm})"]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise PermissionError(result.stderr.strip())
            print(f"[Windows] Permissions set for {path}")

        else:
            
            mode = 0
            if read: mode |= stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            if write: mode |= stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
            if execute: mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            os.chmod(path, mode)
            print(f"[POSIX] Permissions set for {path}: {oct(mode)}")

    except PermissionError as e:
        print(f"Permission denied while setting permissions for {path}.\n   Error: {e}")
        print("Please run as Administrator (Windows) or with sudo (Linux/macOS).")


def list_all() -> dict:
    """
    List all files and folders in the current directory.

    :return: Dictionary containing lists of files and folders.
    """
    current_path = Path.cwd()
    
    files = [f.name for f in current_path.iterdir() if f.is_file()]
    folders = [f.name for f in current_path.iterdir() if f.is_dir()]
    
    result = {
        'files': files,
        'folders': folders
    }
    
    print(f"Files: {files}, Folders: {folders}")
    return result



