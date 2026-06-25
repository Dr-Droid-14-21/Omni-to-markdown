from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QTextEdit, QVBoxLayout

from app.release_readiness import inspect_release_readiness
from app.ui.button_metrics import apply_button_metrics_to
from app.ui.neon_effects import NeonUiEffects


class ReleaseReadinessDialog(QDialog):
    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("releaseReadinessDialog")
        self.setWindowTitle("Release Readiness")
        self.resize(680, 420)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(14)

        self.title_label = QLabel("WINDOWS RELEASE READINESS")
        self.title_label.setObjectName("tabTitle")
        root.addWidget(self.title_label)

        self.summary_label = QLabel("")
        self.summary_label.setObjectName("tabSubtitle")
        self.summary_label.setWordWrap(True)
        root.addWidget(self.summary_label)

        self.details_edit = QTextEdit()
        self.details_edit.setReadOnly(True)
        self.details_edit.setAccessibleName("Release readiness details")
        root.addWidget(self.details_edit)

        self.close_button = QPushButton("Close")
        self.close_button.setProperty("uiRole", "primary")
        self.close_button.setAccessibleName("Close release readiness")
        self.close_button.setToolTip("Close the release readiness report.")
        self.close_button.clicked.connect(self.accept)
        root.addWidget(self.close_button)

        apply_button_metrics_to(self)
        self._ui_fx = NeonUiEffects(self)
        self._ui_fx.install()

    def refresh(self) -> None:
        readiness = inspect_release_readiness()
        self.summary_label.setText(readiness.summary)
        build_text = "present" if readiness.packaged_app_exists else "missing"
        explorer_text = "installed" if readiness.explorer_menu_installed else "not installed"
        sendto_text = "installed" if readiness.sendto_shortcut_installed else "not installed"
        coverage_text = "complete" if readiness.context_menu_coverage_ok else "needs update"
        if readiness.signing_required:
            signing_text = f"{readiness.signature_status} - signing required"
        elif readiness.signature_status.lower() == "valid":
            signing_text = f"{readiness.signature_status} - ready"
        else:
            signing_text = f"{readiness.signature_status} - optional"
        supported_text = ", ".join(readiness.supported_extensions)
        action_lines = "\n".join(f"- {item}" for item in readiness.next_actions)
        self.details_edit.setPlainText(
            "Status\n"
            f"- Windows package: {build_text}\n"
            f"- Explorer menu: {explorer_text}\n"
            f"- SendTo shortcut: {sendto_text}\n"
            f"- Explorer format coverage: {coverage_text}\n"
            f"- Supported input formats: {supported_text}\n"
            f"- Code signing: {signing_text}\n\n"
            "Signature detail\n"
            f"{readiness.signature_detail}\n\n"
            "Next actions\n"
            f"{action_lines}"
        )
