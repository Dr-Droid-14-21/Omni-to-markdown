from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

from app.windows_integration import (
    explorer_integration_status,
    inspect_context_menu_script_coverage,
    packaged_executable_path,
)


@dataclass(slots=True)
class ReleaseReadiness:
    packaged_app_exists: bool
    explorer_menu_installed: bool
    sendto_shortcut_installed: bool
    context_menu_coverage_ok: bool
    supported_extensions: tuple[str, ...]
    signing_required: bool
    signature_status: str
    signature_detail: str
    summary: str
    next_actions: list[str]


@dataclass(slots=True)
class CodeSignatureInspection:
    status: str
    detail: str

    @property
    def valid(self) -> bool:
        return self.status.lower() in {"valid", "signed"}


def inspect_release_readiness() -> ReleaseReadiness:
    packaged_app = packaged_executable_path()
    integration = explorer_integration_status()
    coverage = inspect_context_menu_script_coverage()
    packaged_app_exists = packaged_app.exists()
    signature = inspect_code_signature(packaged_app) if packaged_app_exists else None
    next_actions: list[str] = []

    if not packaged_app_exists:
        next_actions.append("Build the Windows app with scripts/build_windows.ps1.")
    if not integration.installed:
        next_actions.append("Install the Explorer right-click menu from Tools or Settings.")
    if not integration.sendto_installed:
        next_actions.append("Install the Explorer SendTo shortcut from Tools or Settings.")
    if not coverage.ok:
        next_actions.append(
            "Update Explorer scripts so every supported format has right-click coverage."
        )

    signature_valid = bool(signature and signature.valid)

    explorer_complete = integration.installed and integration.sendto_installed
    if packaged_app_exists and explorer_complete and signature_valid:
        summary = "Windows package, Explorer integration, and code signing are ready."
    elif packaged_app_exists and explorer_complete:
        summary = (
            "Local Windows workflow is ready. "
            "Code signing is optional and currently not used."
        )
    elif packaged_app_exists:
        summary = "Packaged app exists. Explorer integration is not installed yet."
    else:
        summary = "Windows package is not built yet."

    return ReleaseReadiness(
        packaged_app_exists=packaged_app_exists,
        explorer_menu_installed=integration.installed,
        sendto_shortcut_installed=integration.sendto_installed,
        context_menu_coverage_ok=coverage.ok,
        supported_extensions=coverage.supported_extensions,
        signing_required=False,
        signature_status=signature.status if signature else "missing",
        signature_detail=signature.detail if signature else "Package has not been built.",
        summary=summary,
        next_actions=next_actions,
    )


def inspect_code_signature(executable_path: Path) -> CodeSignatureInspection:
    try:
        with executable_path.open("rb") as file:
            header = file.read(1024)
            if len(header) < 0x40 or header[:2] != b"MZ":
                return CodeSignatureInspection(
                    status="unknown",
                    detail="File is not a readable Windows PE executable.",
                )

            pe_offset = struct.unpack_from("<I", header, 0x3C)[0]
            file.seek(pe_offset)
            pe_header = file.read(24)
            if len(pe_header) < 24 or pe_header[:4] != b"PE\0\0":
                return CodeSignatureInspection(
                    status="unknown",
                    detail="File does not contain a valid PE header.",
                )

            optional_header_size = struct.unpack_from("<H", pe_header, 20)[0]
            optional_header = file.read(optional_header_size)
            if len(optional_header) < optional_header_size:
                return CodeSignatureInspection(
                    status="unknown",
                    detail="PE optional header is truncated.",
                )

            magic = struct.unpack_from("<H", optional_header, 0)[0]
            if magic == 0x10B:
                data_directory_offset = 96
            elif magic == 0x20B:
                data_directory_offset = 112
            else:
                return CodeSignatureInspection(
                    status="unknown",
                    detail=f"Unsupported PE optional-header magic: 0x{magic:x}.",
                )

            security_directory_offset = data_directory_offset + (4 * 8)
            if len(optional_header) < security_directory_offset + 8:
                return CodeSignatureInspection(
                    status="unknown",
                    detail="PE security directory is missing from optional header.",
                )

            certificate_offset, certificate_size = struct.unpack_from(
                "<II",
                optional_header,
                security_directory_offset,
            )
    except OSError as exc:
        return CodeSignatureInspection(
            status="unknown",
            detail=f"Unable to inspect executable signature: {exc}",
        )

    if certificate_offset > 0 and certificate_size > 0:
        return CodeSignatureInspection(
            status="Signed",
            detail=(
                "Authenticode certificate table is present. "
                "Full certificate-chain trust validation is not required for this build."
            ),
        )

    return CodeSignatureInspection(
        status="NotSigned",
        detail=(
            "No Authenticode certificate table is present. "
            "This is acceptable for the current local build policy."
        ),
    )
