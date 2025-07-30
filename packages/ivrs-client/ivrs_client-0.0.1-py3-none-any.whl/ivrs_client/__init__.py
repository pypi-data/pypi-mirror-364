import os
import platform
import zipfile
import shutil
import urllib.request
import tempfile
import subprocess
from tqdm import tqdm


def download_with_progress(url, output_path):
    """带进度条的下载函数"""
    with urllib.request.urlopen(url) as response:
        total_size = int(response.getheader('Content-Length').strip())
        with open(output_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc='下载 ffmpeg', ncols=80
        ) as pbar:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                pbar.update(len(chunk))


def get_ffmpeg_exe_names():
    system = platform.system()
    if system == "Windows":
        return ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]
    else:
        return ["ffmpeg", "ffplay", "ffprobe"]


def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None


def install_ffmpeg_unix():
    system = platform.system()
    try:
        if system == "Linux":
            print("[INFO] 正在尝试通过 apt 安装 ffmpeg...")
            subprocess.check_call(["sudo", "apt", "update"])
            subprocess.check_call(["sudo", "apt", "install", "-y", "ffmpeg"])
        elif system == "Darwin":
            print("[INFO] 正在尝试通过 Homebrew 安装 ffmpeg...")
            subprocess.check_call(["brew", "install", "ffmpeg"])
    except Exception as e:
        raise RuntimeError(f"[ERROR] 安装 ffmpeg 失败：{e}")


def ensure_ffmpeg_windows():
    exe_files = get_ffmpeg_exe_names()
    cwd = os.getcwd()

    if all(os.path.exists(os.path.join(cwd, exe)) for exe in exe_files):
        print("[INFO] 已存在 ffmpeg 可执行文件")
        return

    print("[INFO] 正在下载 ffmpeg 可执行文件...")

    download_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "ffmpeg.zip")
        download_with_progress(download_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        bin_dir = None
        for root, dirs, files in os.walk(tmpdir):
            if all(name in files for name in exe_files):
                bin_dir = root
                break

        if bin_dir is None:
            raise RuntimeError("找不到 ffmpeg 可执行文件")

        for exe in exe_files:
            shutil.copy(os.path.join(bin_dir, exe), os.path.join(cwd, exe))
            print(f"[INFO] 已保存 {exe}")

        print("[INFO] ffmpeg 可执行文件准备完成")


def ensure_ffmpeg():
    system = platform.system()
    if system == "Windows":
        ensure_ffmpeg_windows()
    else:
        if is_ffmpeg_installed():
            print("[INFO] 系统中已安装 ffmpeg")
        else:
            install_ffmpeg_unix()


# 自动执行
ensure_ffmpeg()