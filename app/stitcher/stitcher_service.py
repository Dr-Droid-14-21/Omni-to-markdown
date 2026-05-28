from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.core.models import ConversionWarning, StitchManifest, StitchResult
from app.stitcher.separator import build_separator


class StitcherValidationError(ValueError):
    """Raised when stitch inputs fail validation."""


class StitchCancelledError(RuntimeError):
    """Raised when stitching is cancelled before completion."""


class StitcherService:
    def stitch(
        self,
        manifest: StitchManifest,
        should_cancel: Callable[[], bool] | None = None,
    ) -> StitchResult:
        self._validate_manifest(manifest)

        output_path = manifest.output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        warnings = self._build_warnings(manifest.input_files)

        temp_path = self._write_temp_output(
            manifest.input_files,
            output_path,
            should_cancel=should_cancel,
        )
        Path(temp_path).replace(output_path)

        return StitchResult(
            output_path=output_path,
            file_count=len(manifest.input_files),
            warnings=warnings,
        )

    def _validate_manifest(self, manifest: StitchManifest) -> None:
        output_resolved = manifest.output_path.resolve()

        for path in manifest.input_files:
            if not path.exists():
                msg = f"input file does not exist: {path}"
                raise StitcherValidationError(msg)
            if path.resolve() == output_resolved:
                msg = "output path cannot be the same as an input file path"
                raise StitcherValidationError(msg)
            if path.suffix.lower() not in {".md", ".markdown"}:
                msg = f"unsupported stitch input extension: {path.suffix}"
                raise StitcherValidationError(msg)

    def _build_warnings(self, paths: list[Path]) -> list[ConversionWarning]:
        basenames = [path.name.lower() for path in paths]
        duplicates = sorted({name for name in basenames if basenames.count(name) > 1})
        warnings: list[ConversionWarning] = []
        for name in duplicates:
            warnings.append(
                ConversionWarning(
                    code="DUPLICATE_BASENAME",
                    message=f"duplicate basename in stitch list: {name}",
                )
            )
        return warnings

    def _write_temp_output(
        self,
        input_files: list[Path],
        output_path: Path,
        should_cancel: Callable[[], bool] | None = None,
    ) -> str:
        temp_path = ""
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                delete=False,
                dir=output_path.parent,
                suffix=".tmp.md",
            ) as temp:
                temp_path = temp.name
                for index, file_path in enumerate(input_files):
                    if should_cancel is not None and should_cancel():
                        msg = "stitch cancelled by user request"
                        raise StitchCancelledError(msg)

                    content = self._read_markdown(file_path)
                    temp.write(content.rstrip("\n"))

                    if index < len(input_files) - 1:
                        separator = build_separator(file_path.name)
                        temp.write("\n\n")
                        temp.write(separator)
                        temp.write("\n\n")
                    else:
                        temp.write("\n")
            return temp_path
        except Exception:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
            raise

    @staticmethod
    def _read_markdown(path: Path) -> str:
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            msg = f"unable to decode file as utf-8: {path}"
            raise StitcherValidationError(msg) from exc
        return raw.replace("\r\n", "\n").replace("\r", "\n")
