import datetime
import fnmatch
import io
import json
import os
import time
import shutil
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .fileformat import get_format, Format


class ArgException(Exception):
    pass


@dataclass
class ManifestInfo:
    filename: str
    size: int
    mtime: float

    @classmethod
    def from_str(cls, text: str):
        file, size, mtime = text.split(':')
        return cls(file, int(size), float(mtime))

    def __str__(self):
        return f'{self.filename}:{self.size}:{self.mtime}'


def get_manifest(fm: Format) -> dict[str, ManifestInfo]:
    text = fm.read('.backup_manifest').read().decode('utf-8')
    data = {}
    for line in text.splitlines():
        manifest = ManifestInfo.from_str(line)
        data[manifest.filename] = manifest
    return data


def write_manifest(fm: Format, manifest: dict[str, ManifestInfo]):
    text = '\n'.join(str(item) for item in manifest.values())
    fm.write('.backup_manifest', io.BytesIO(text.encode('utf-8')))


def openf(path, mode="rb") -> Format:
    return get_format(path, open(path, mode))


def get_backup_info(config: Config) -> dict:
    try:
        with open(f"{config.target}/backup.json", encoding="utf8") as f:
            data = json.load(f)
            backup_files: list = data['backup_files']
            backup_files.sort(key=lambda x: x["time"], reverse=True)  # 从最新的开始
            return data
    except FileNotFoundError:
        return {"backup_files": []}


def save_backup_info(config: Config, backup_info: dict):
    with open(f"{config.target}/backup.json", 'w', encoding="utf8") as f:
        json.dump(backup_info, f, indent=4, ensure_ascii=False)


def show_file(name: str, config: Config):
    info = get_backup_info(config)
    files = info["backup_files"]
    for file in files:
        if file["name"] == name:
            with openf(f"{config.target}/{file['filename']}") as fm:
                print('Files(* represents exists in backup file):')
                manifest = get_manifest(fm)
                for path in manifest.keys():
                    line = f"{path}(size={manifest[path].size}, mtime={datetime.datetime.fromtimestamp(file['time'])})"
                    if fm.exists(path):
                        print(" *" + line)
                    else:
                        print(" ?" + line)
            return
    else:
        raise ArgException(f"Backup name {name} not found")


def backup_file(config: Config, name=None):
    """
    执行增量备份操作
    """

    # 创建目录，避免错误
    os.makedirs(config.target, exist_ok=True)
    backup_info = get_backup_info(config)
    # 2. 在目标目录查找最新的备份文件
    old_manifest = {}
    if not config.full_backup and backup_info["backup_files"]:
        latest_file = backup_info["backup_files"][0]  # 取最新备份
        # 3. 读取最新备份文件中的文件清单
        with openf(f"{config.target}/{latest_file['filename']}") as fm:
            old_manifest = get_manifest(fm)  # 获取旧清单

    total_files = 0
    backed_files = 0
    # 准备新备份清单
    new_manifest = {}

    filename = datetime.datetime.now().strftime(config.format)
    name = name or datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    backup_path = str(Path(config.target, filename))
    source_path = Path(config.source)

    with openf(backup_path, 'wb') as fm:
        # 4. 递归遍历源文件夹
        for root, dirs, files in os.walk(config.source):
            for file in files:
                # 5. 排除文件，计算文件哈希和大小并与备份清单比较
                f_path = Path(root, file)
                rel_path = str(f_path.relative_to(source_path)).replace('\\', '/')
                if any(fnmatch.fnmatch(rel_path, exclude) for exclude in config.exclude):
                    continue
                total_files += 1
                # 计算文件大小和mtime
                meta = os.stat(f_path)
                f_size = meta.st_size
                f_mtime = meta.st_mtime

                # 7. 更新新清单（无论是否备份都记录）
                new_manifest[rel_path] = ManifestInfo(rel_path, f_size, f_mtime)

                if rel_path in old_manifest:  # 在清单里，比对大小和mtime
                    mt = old_manifest[rel_path]
                    if mt.size == f_size and mt.mtime == f_mtime:
                        continue

                # 6. 备份有变化的文件
                with open(str(f_path), 'rb') as fb:
                    fm.write(rel_path, fb)  # 写入备份
                backed_files += 1
        # 写入新备份清单
        write_manifest(fm, new_manifest)

    backup_info["backup_files"].insert(0, {"name": name, "filename": filename, "time": time.time(), "backed": backed_files, "total": total_files})
    save_backup_info(config, backup_info)
    print(f"Backup {filename} done, name: {name}, {backed_files}/{total_files} files backed")

    if config.max_backups is not None:
        # 8. 如果超出最大备份数量，合并最旧的文件
        # 删除旧文件需要合并最后两个文件
        if len(backup_info["backup_files"]) > config.max_backups >= 2:
            print(f"Max backup number {config.max_backups} reached, merging")
            old = backup_info["backup_files"][-1]
            merge_file(config.target, old["filename"], backup_info["backup_files"][-2]["filename"])
            backup_info["backup_files"].pop(-1)
            print(f"Merge {old['filename']} done")


def merge_file(fdir, file1, file2):
    """
    合并两个文件，f1是旧的

    步骤：
    1. 新建临时文件f3 (因为有些压缩格式不支持追加)
    2. 打开f123
    2. 读取f2的清单
    3. 将f2的所有文件复制到f3中
    4. f2清单上有但是f2里不存在的文件从f1中读取
    5. 删除f1,f2，将f3重命名为f2
    """
    with (openf(f"{fdir}/{file1}") as f1,
          openf(f"{fdir}/{file2}") as f2,
          openf(f"{fdir}/{file2}.tmp") as f3):
        manifest2 = get_manifest(f2)
        for file, item in manifest2.items():
            if f2.exists(file):
                f3.write(file, f2.read(file))
            else:
                f3.write(file, f1.read(file))
        write_manifest(f3, manifest2)
    os.unlink(f"{fdir}/{file1}")
    os.unlink(f"{fdir}/{file2}")
    os.rename(f"{fdir}/{file2}.tmp", f"{fdir}/{file2}")


def delete_file(name, config: Config):
    """
    删除文件，需要合并此文件和更新的文件
    """
    info = get_backup_info(config)
    for file in info["backup_files"].copy():
        if file["name"] == name:
            if not os.path.exists(f"{config.target}/{file['filename']}"):
                raise ArgException(f'{file["filename"]} not found')

            next_file_ind = info["backup_files"].index(file) - 1  # 更新的备份
            if next_file_ind >= 0:
                merge_file(config.target, file["filename"], info["backup_files"][next_file_ind])
            else:
                os.unlink(f"{config.target}/{file['filename']}")  # 如果自己就是最新的，则直接删除
            info["backup_files"].remove(file)
            save_backup_info(config, info)
            break
    else:
        raise ArgException(f'{name} not found')


def restore_file(name, config: Config):
    os.makedirs(config.source, exist_ok=True)
    info = get_backup_info(config)
    backup_info = [file for file in info["backup_files"] if file["name"] == name]
    if backup_info:
        file = backup_info[0]
    else:
        raise ArgException(f'{name} not found')
    if not os.path.exists(f"{config.target}/{file['filename']}"):
        raise ArgException(f'{file["filename"]} not found')

    with openf(f"{config.target}/{file['filename']}") as f:
        manifest = get_manifest(f)
    total_files = len(manifest)
    source_path = Path(config.source)
    for path in source_path.rglob("*"):
        if str(path.relative_to(source_path)).replace('\\', '/') not in manifest:
            os.unlink(path)

    for bi in info["backup_files"][info["backup_files"].index(file):]:  # 遍历旧文件
        # 寻找匹配的文件
        with openf(f"{config.target}/{bi['filename']}") as fm:
            for file, item in manifest.copy().items():
                if fm.exists(file):
                    with open(f"{config.source}/{file}", "wb") as fb:
                        shutil.copyfileobj(fm.read(file), fb)
                    manifest.pop(file)
    print(f"Restore {name} done, {total_files - len(manifest)}/{total_files} files restored")


def list_file(config: Config):
    info = get_backup_info(config)
    print("Backup info:")
    for file in info["backup_files"]:
        print(f"  {file['name']}(backed {file['backed']}/{file['total']} files)")
