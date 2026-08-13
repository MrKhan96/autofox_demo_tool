"""
Reflection Removal Model
========================

This module holds the single integration point for the reflection-removal
model. The web app calls `remove_reflection()` and nothing else, so plugging
in the real model later means editing ONLY the body of that function.

Current state: PLACEHOLDER. It just copies the input image to the output path
so the full web flow (upload -> process -> before/after -> download) works
end-to-end during the demo build. Swap the body when the model is ready.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def remove_reflection(input_path: str | Path, output_path: str | Path) -> str:
    """Remove reflections from a car image.

    Args:
        input_path:  Path to the uploaded car image (jpg/png/webp).
        output_path: Path where the reflection-removed image should be written.

    Returns:
        The output_path as a string.

    ------------------------------------------------------------------
    PLUG THE REAL MODEL IN HERE.
    ------------------------------------------------------------------
    Replace the placeholder copy below with your inference code, e.g.:

        from PIL import Image
        img = Image.open(input_path).convert("RGB")
        result = your_model.predict(img)          # -> PIL.Image / np.ndarray
        result.save(output_path)

    Keep the same signature (input_path, output_path) -> output_path and the
    web app will keep working without any other changes.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # --- PLACEHOLDER: pass the image through unchanged ---
    shutil.copyfile(input_path, output_path)

    return str(output_path)
