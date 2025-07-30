from io import BytesIO

from .data_structures.stack import Stack
from .path import *


def readfile(file, mode='r'):
    """
    从文件读取数据，允许自定义模式
    """
    with open(file, mode) as f:
        return f.read()


def writefile(data, file, mode='w'):
    """
    向文件写入数据，允许自定义模式
    """
    with open(file, mode) as f:
        f.write(data)


def isfileempty(file):
    """
    判断文件内容是否为空
    """
    with open(file) as f:
        d = f.read(1)
        if d == '':
            return True
        return None


def isfilespace(file):
    """
    判断文件内容是否完全为空白
    """
    d = readfile(file)
    return d.isspace()


def copyfile(src, dst):
    """
    复制文件
    """
    with open(src, 'rb') as f:
        data = f.read()
    with open(dst, 'wb') as f:
        f.write(data)


def copyfile_stream(src, dst, chunk_size=1024):
    """
    流式复制文件
    """
    with open(src, 'rb') as src_f:
        with open(dst, 'wb') as dst_f:
            while True:
                data = src_f.read(chunk_size)
                if data == b'':
                    break
                dst_f.write(data)


fileDataType = Union[str, bytes, bytearray]


class NeoIO:
    """
    新文件读写

    特点:
        1. 可复用
        2. 灵活,完全支持内置的IO-API
        3. 快速获取文件信息
        4. 堆栈管理文件

    适用于普通文件操作，在常见桌面和服务器操作系统上表现良好。
    """

    class FileState:
        def __init__(self, fstat: os.stat_result):
            self.fstat = fstat

        @property
        def birthday(self):
            """
            创建时间
            """
            # 注意：st_birthtime在某些平台上可能不可用
            try:
                return self.fstat.st_birthtime
            except AttributeError:
                return None

        @property
        def last_access(self):
            """
            最后访问时间
            """
            return self.fstat.st_atime

        @property
        def last_modified(self):
            """
            最后修改时间
            """
            return self.fstat.st_mtime

        @property
        def size(self):
            """
            文件大小
            """
            return self.fstat.st_size

        @property
        def mode(self):
            """
            文件权限
            """
            return self.fstat.st_mode

        @property
        def inode(self):
            """
            文件ID
            """
            return self.fstat.st_ino

        @property
        def device(self):
            """
            文件设备
            """
            return self.fstat.st_dev

        @property
        def nlink(self):
            """
            链接数
            """
            return self.fstat.st_nlink

        @property
        def uid(self):
            """
            用户ID
            """
            return self.fstat.st_uid

        @property
        def gid(self):
            """
            组ID
            """
            return self.fstat.st_gid

    def __init__(self):
        self._file_stack = Stack()
        self.create = False

    def __push_file(self, fd):
        self._file_stack.push(fd)

    @property
    def __topfile(self):
        """
        获取当前栈顶的文件
        """
        return self._file_stack.top

    @classmethod
    def from_fd(cls, fd):
        """
        从文件描述符创建实例
        """
        ins = cls()
        ins.push_fd(fd)
        return ins

    @classmethod
    def fopen(cls, file, mode='r', encoding=None, *args, **kwargs):
        """
        打开文件并返回实例
        """
        fd = open(file, mode, encoding=encoding, *args, **kwargs)
        ins = cls.from_fd(fd)
        return ins

    def open(self, file, mode='r', encoding=None, create=None, *args, **kwargs):
        """
        打开一个新的文件,并压入栈中
        """
        if create is None:
            create = self.create

        if not path_exists(file) and not create:
            mkfile(file)

        self.__push_file(
            open(file, mode, encoding=encoding, *args, **kwargs))

        return self

    def push_fd(self, fd):
        """
        压入一个新的文件描述符
        """
        self.__push_file(fd)

    @property
    def opened(self):
        """
        是否存在打开的文件
        """
        return self._file_stack.size() and not self.__topfile.closed

    @property
    def can_write(self):
        """
        是否可写
        """
        return self.__topfile.writable()

    @property
    def can_read(self):
        """
        是否可读
        """
        return self.__topfile.readable()

    @property
    def can_seek(self):
        """
        是否可定位
        """
        return self.__topfile.seekable()

    @property
    def is_bytes_io(self):
        """
        是否为BytesIO
        """
        return isinstance(self.__topfile, BytesIO)

    @property
    def pos(self):
        """
        当前位置
        """
        return self.__topfile.tell()

    @property
    def fileno(self):
        """
        文件描述符
        """
        return self.__topfile.fileno()

    @property
    def osfstat(self):
        """
        文件状态
        """
        try:
            return os.fstat(self.fileno)
        except OSError:
            return None

    @property
    def neofstat(self):
        """
        文件状态
        """
        return NeoIO.FileState(self.osfstat)

    @property
    def size(self):
        """
        文件大小
        """
        return self.osfstat.st_size

    def write(self, data: Union[bytes, str]):
        """
        写入数据
        """
        if self.can_write:
            self.__topfile.write(data)
        else:
            raise IOError("文件无法写入")

    def seek(self, offset, whence=0):
        """
        定位文件
        """
        self.__topfile.seek(offset, whence)

    def read(self, size=-1):
        """
        读取数据
        """
        if self.can_read:
            return self.__topfile.read(size)
        else:
            raise IOError("文件无法读取")

    def readline(self, size=-1):
        """
        读取一行
        """
        if self.can_read:
            return self.__topfile.readline(size)
        else:
            raise IOError("文件无法读取")

    def readlines(self, hint=-1):
        """
        读取所有行
        """
        if self.can_read:
            return self.__topfile.readlines(hint)
        else:
            raise IOError("文件无法读取")

    def clear(self):
        """
        清除文件内容
        """
        self.__topfile.truncate(0)

    def flush(self):
        """
        刷新文件
        """
        self.__topfile.flush()

    def close(self):
        """
        关闭位于栈顶的文件
        """
        if self.__topfile:
            self.__topfile.close()
            self._file_stack.pop()
        else:
            raise IOError('未打开任何文件')

    def close_all(self):
        """
        关闭所有文件
        """
        while self._file_stack:
            self._file_stack.pop().close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
