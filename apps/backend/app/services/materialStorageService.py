import hashlib
import os
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile


class MaterialStorageService:
    MAX_FILE_SIZE = 50 * 1024 * 1024

    def __init__(self):
        self.root = Path(
            os.getenv(
                "LIA2_MATERIAL_STORAGE_PATH",
                "/var/lib/lia2-materials",
            )
        )
        self.root.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        studentId: UUID,
        materialId: UUID,
        materialFileId: UUID,
        upload: UploadFile,
    ) -> tuple[str, int, str]:
        extension = Path(upload.filename or "").suffix.lower()
        relative = Path(str(studentId)) / str(materialId) / (
            f"{materialFileId}{extension}"
        )
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)

        digest = hashlib.sha256()
        size = 0

        try:
            with destination.open("wb") as output:
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break

                    size += len(chunk)

                    if size > self.MAX_FILE_SIZE:
                        raise ValueError("FILE_TOO_LARGE")

                    digest.update(chunk)
                    output.write(chunk)

        except Exception:
            destination.unlink(missing_ok=True)
            raise

        finally:
            await upload.close()

        return str(relative), size, digest.hexdigest()

    def saveDerivedBytes(
        self,
        studentId: UUID,
        materialId: UUID,
        relativeName: str,
        content: bytes,
    ) -> str:
        safeName = relativeName.replace("..", "_").lstrip("/\\")
        relative = (
            Path(str(studentId))
            / str(materialId)
            / "derived"
            / safeName
        )

        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

        return str(relative)

    def saveDerivedFile(
        self,
        studentId: UUID,
        materialId: UUID,
        relativeName: str,
        sourcePath: Path,
    ) -> str:
        return self.saveDerivedBytes(
            studentId,
            materialId,
            relativeName,
            sourcePath.read_bytes(),
        )

    def absolutePath(self, storageKey: str) -> Path:
        return self.root / storageKey

    def remove(self, storageKey: str) -> None:
        self.absolutePath(storageKey).unlink(missing_ok=True)

    def removeDerivedTree(
        self,
        studentId: UUID,
        materialId: UUID,
    ) -> None:
        derivedRoot = (
            self.root
            / str(studentId)
            / str(materialId)
            / "derived"
        )

        if not derivedRoot.exists():
            return

        for path in sorted(
            derivedRoot.rglob("*"),
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            if path.is_file() or path.is_symlink():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass

        try:
            derivedRoot.rmdir()
        except OSError:
            pass

    def removeMaterialTree(
        self,
        studentId: UUID,
        materialId: UUID,
    ) -> None:
        materialRoot = self.root / str(studentId) / str(materialId)

        if not materialRoot.exists():
            return

        for path in sorted(
            materialRoot.rglob("*"),
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            if path.is_file() or path.is_symlink():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass

        try:
            materialRoot.rmdir()
        except OSError:
            pass
