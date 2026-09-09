#!/usr/bin/env python3

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py <image>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Erreur : fichier introuvable : {input_path}")
        sys.exit(1)

    output_path = input_path.with_name("source-prepped.png")

    print(f"→ Lecture de {input_path}")

    # 1. Remove background
    print("→ Suppression de l'arrière-plan...")
    source = Image.open(input_path).convert("RGBA")
    foreground = remove(source)

    # 2. White background
    print("→ Composition sur fond blanc...")
    background = Image.new("RGBA", foreground.size, "white")
    composited = Image.alpha_composite(background, foreground)

    # 3. Convert to grayscale
    print("→ Conversion en niveaux de gris...")
    gray = np.array(composited.convert("L"))

    # 4. Local contrast enhancement with CLAHE
    print("→ Amélioration du contraste...")
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    # 5. Save
    Image.fromarray(enhanced).save(output_path)

    print(f"✓ Image préparée : {output_path}")


if __name__ == "__main__":
    main()