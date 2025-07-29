import io
import tarfile
import zipfile
from typing import IO


class Format:
    def __init__(self, file: IO[bytes]):
        self.file = file

    def write(self, filename: str, data: IO[bytes]):
        ...

    def read(self, filename: str) -> IO[bytes]:
        ...

    def exists(self, path: str) -> bool:
        ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


class ZipFormat(Format):
    def __init__(self, file: IO[bytes]):
        super().__init__(file)
        self.zip = zipfile.ZipFile(file, 'a')

    def write(self, filename: str, data: IO[bytes]):
        with self.zip.open(filename, 'w') as f, data:
            for chunk in iter(lambda: data.read(1024 * 1024 * 10), b""):
                f.write(chunk)

    def read(self, filename: str) -> IO[bytes]:
        return self.zip.open(filename, 'r')

    def exists(self, path: str) -> bool:
        return path in self.zip.namelist()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.zip.close()
        super().__exit__(exc_type, exc_val, exc_tb)


class TarFormat(Format):
    def __init__(self, file: IO[bytes], mode: str = 'w', compression: str = ''):
        super().__init__(file)
        self.mode = mode + compression
        self.tar = tarfile.open(fileobj=file, mode=self.mode)

    def write(self, filename: str, data: IO[bytes]):
        info = tarfile.TarInfo(name=filename)

        # 将数据读入内存（可能不适合超大文件）
        data_bytes = data.read()
        info.size = len(data_bytes)
        self.tar.addfile(tarinfo=info, fileobj=io.BytesIO(data_bytes))

    def read(self, filename: str) -> IO[bytes]:
        member = self.tar.getmember(filename)
        return self.tar.extractfile(member)

    def exists(self, path: str) -> bool:
        try:
            self.tar.getmember(path)
            return True
        except KeyError:
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tar.close()
        super().__exit__(exc_type, exc_val, exc_tb)


class TarGzFormat(TarFormat):
    def __init__(self, file: IO[bytes]):
        super().__init__(file, compression=':gz')


class TarBz2Format(TarFormat):
    def __init__(self, file: IO[bytes]):
        super().__init__(file, compression=':bz2')


class TarXzFormat(TarFormat):
    def __init__(self, file: IO[bytes]):
        super().__init__(file, compression=':xz')


def get_format(format_: str, stream: IO) -> Format:
    format_lower = format_.lower()  # 不区分大小写匹配

    if format_lower.endswith('.zip'):
        return ZipFormat(stream)
    elif format_lower.endswith('.tar'):
        return TarFormat(stream)
    elif format_lower.endswith(('.tar.gz', '.tgz')):
        return TarGzFormat(stream)
    elif format_lower.endswith(('.tar.bz2', '.tbz2')):
        return TarBz2Format(stream)
    elif format_lower.endswith(('.tar.xz', '.txz')):
        return TarXzFormat(stream)
    else:
        supported_formats = [
            '.zip',
            '.tar',
            '.tar.gz (.tgz)',
            '.tar.bz2 (.tbz2)',
            '.tar.xz (.txz)'
        ]
        raise ValueError(
            f"Unsupported format: '{format_}'. "
            f"Supported formats are: {', '.join(supported_formats)}"
        )
