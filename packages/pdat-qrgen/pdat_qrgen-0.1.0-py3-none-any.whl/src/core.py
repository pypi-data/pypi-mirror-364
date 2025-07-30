from pathlib import Path
from typing import Optional

import qrcode  # type: ignore[import-untyped]
from PIL import Image

from .exceptions import InvalidInputError, LogoNotFoundError


class QRGenerator:
    """Advanced QR code generator with logo embedding support."""

    ERROR_CORRECTION_MAP = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    def __init__(
        self,
        content: str,
        output_path: str,
        fill_color: str = "black",
        back_color: str = "white",
        logo_path: Optional[str] = None,
        version: int = 1,
        error_correction: str = "H",
        box_size: int = 10,
        border: int = 4,
    ):
        self.content = content
        self.output_path = output_path
        self.fill_color = fill_color
        self.back_color = back_color
        self.logo_path = logo_path
        self.version = version
        self.error_correction = error_correction.upper()
        self.box_size = box_size
        self.border = border

    def generate(self) -> None:
        """Generate and save QR code with optional logo."""
        self._validate_inputs()

        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self._get_error_correction(),
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(self.content)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color).convert("RGB")

        if self.logo_path is not None:
            self._embed_logo(qr_img)

        Path(self.output_path).parent.mkdir(exist_ok=True, parents=True)
        qr_img.save(self.output_path)

    def _validate_inputs(self) -> None:
        """Validate all input parameters."""
        if not self.content:
            raise InvalidInputError("Content cannot be empty")
        if not self.output_path:
            raise InvalidInputError("Output path cannot be empty")
        if self.logo_path and not Path(self.logo_path).exists():
            raise LogoNotFoundError(f"Logo file not found: {self.logo_path}")
        if self.error_correction not in self.ERROR_CORRECTION_MAP:
            raise InvalidInputError(
                f"Invalid error correction level: {self.error_correction}. "
                f"Must be one of: {list(self.ERROR_CORRECTION_MAP.keys())}"
            )

    def _get_error_correction(self) -> int:
        """Get error correction level constant."""
        return self.ERROR_CORRECTION_MAP[self.error_correction]

    def _embed_logo(self, qr_img: Image.Image) -> None:
        """Embed logo in the center of QR code."""
        logo = Image.open(self.logo_path).convert("RGBA")  # type: ignore[arg-type]
        max_size = min(qr_img.size) // 5
        logo.thumbnail((max_size, max_size))

        pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

        mask = logo.split()[3] if logo.mode == "RGBA" else None
        qr_img.paste(logo, pos, mask)
