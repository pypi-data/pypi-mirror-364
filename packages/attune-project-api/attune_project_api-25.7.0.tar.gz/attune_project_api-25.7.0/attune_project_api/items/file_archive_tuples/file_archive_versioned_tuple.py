"""
*
 *  Copyright AttuneOps HQ Pty Ltd 2021
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  AttuneOps HQ Pty Ltd
 *
"""
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED
from zipfile import ZIP_STORED

import pytz
from pytmpdir.spooled_named_temporary_file import SpooledNamedTemporaryFile

from attune_project_api import ObjectStorageContext
from attune_project_api.ObjectStorageContext import VersionedFileContent
from attune_project_api.ObjectStorageContext import VersionedFileInfo
from attune_project_api.items.file_archive_tuples.file_archive_tuple import (
    FileArchiveTuple,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_TAR,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_ZIP,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    FileArchiveTupleTypeEnum,
)
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import noMainThread
from vortex.Tuple import addTupleType

logger = logging.getLogger(__name__)


@ObjectStorageContext.registerItemClass
@addTupleType
class FileArchiveVersionedTuple(FileArchiveTuple):
    """Archive Versioned Tuple

    This archive tuple stores small version controlled archives.
    They are never archived, they live extracted in the git object repository
    """

    # We need to enforce this because this data is loaded entirely in memory
    MAX_VERSIONED_FILE_SIZE = 10 * 1024 * 1024
    MAX_ARCHIVE_VERSION_REPLACE_SIZE = 10 * 1024 * 1024

    __tupleType__ = FileArchiveTupleTypeEnum.VERSIONED.value

    @classmethod
    @property
    def niceName(cls) -> str:
        # This is meant to be an abstract method
        return "Version Controlled Files"

    def __checkSize(self, data):
        if len(data) > self.MAX_VERSIONED_FILE_SIZE:
            raise Exception(
                "Only files up to 1mb can be version controlled,"
                "use the Large files type instead"
            )

    def writeFile(self, path: Path, data: bytes) -> None:
        self.__checkSize(data)
        self.storageContext.writeItemVersionedFile(
            self.storageGroup, self.key, path, data
        )

    def readFile(self, path: Path) -> bytes:
        data = self.storageContext.readItemVersionedFile(
            self.storageGroup, self.key, path
        )
        self.__checkSize(data)
        return data

    @property
    def listFiles(self) -> list[VersionedFileInfo]:
        return self.storageContext.listItemVersionedFiles(
            self.storageGroup, self.key
        )

    @property
    def hasFiles(self) -> bool:
        return self.storageContext.hasItemVersionedFiles(
            self.storageGroup, self.key
        )

    def getFileContent(self, path: Path) -> VersionedFileContent:
        return self.storageContext.getItemVersionedFileContent(
            self.storageGroup, self.key, path
        )

    def setFileContent(self, path: Path, data: bytes, executable: bool) -> None:
        self.storageContext.setItemVersionedFileContent(
            self.storageGroup, self.key, path, data, executable
        )

    def moveFile(self, fromPath: Path, toPath: Path) -> None:
        self.storageContext.moveItemVersionedFile(
            self.storageGroup, self.key, fromPath, toPath
        )

    def moveDirectory(self, fromPath: Path, toPath: Path) -> None:
        self.storageContext.moveItemVersionedDirectory(
            self.storageGroup, self.key, fromPath, toPath
        )

    def deleteFile(self, path: Path) -> None:
        self.storageContext.deleteItemVersionedFile(
            self.storageGroup, self.key, path
        )

    def deleteDirectory(self, path: Path = Path()) -> None:
        self.storageContext.deleteItemVersionedDirectory(
            self.storageGroup, self.key, path
        )

    def makeFileName(self, formatKey: str = ARCHIVE_FORMAT_KEY_TAR) -> str:
        assert formatKey in (
            ARCHIVE_FORMAT_KEY_ZIP,
            ARCHIVE_FORMAT_KEY_TAR,
        ), "formatKey should must be tar or zip"

        return self._makeFileName(formatKey)

    @deferToThreadWrapWithLogger(logger)
    def makeZipAsync(self, deflate: bool = False) -> SpooledNamedTemporaryFile:
        return self.makeZip(deflate=deflate)

    def makeZip(self, deflate: bool = False) -> SpooledNamedTemporaryFile:
        noMainThread()
        now = datetime.now(pytz.utc)

        tmpFile = SpooledNamedTemporaryFile()
        # Create the zip file
        from zipfile import ZipFile, ZipInfo

        with ZipFile(
            tmpFile, "w", compression=(ZIP_DEFLATED if deflate else ZIP_STORED)
        ) as zip:
            for fileInfo in self.listFiles:
                content = self.getFileContent(fileInfo.path)
                zip.writestr(
                    ZipInfo(str(fileInfo.path), date_time=now.timetuple()),
                    content.data,
                )

        tmpFile.seek(0)
        return tmpFile

    @deferToThreadWrapWithLogger(logger)
    def makeTarAsync(self) -> SpooledNamedTemporaryFile:
        return self.makeTar()

    def makeTar(self) -> SpooledNamedTemporaryFile:
        noMainThread()
        now = datetime.now(pytz.utc)

        tmpFile = SpooledNamedTemporaryFile()

        # Create the zip file
        from tarfile import TarFile, TarInfo

        with TarFile.open(
            fileobj=tmpFile, mode="w", bufsize=1024 * 1024
        ) as tar:
            for fileInfo in self.listFiles:
                content = self.getFileContent(fileInfo.path)

                fileObj = BytesIO(content.data)
                fileObj.seek(0)

                tarInfo = TarInfo(str(fileInfo.path))
                tarInfo.size = len(content.data)
                tarInfo.mtime = now.timestamp()

                tar.addfile(tarInfo, fileObj)

        tmpFile.seek(0)
        return tmpFile
