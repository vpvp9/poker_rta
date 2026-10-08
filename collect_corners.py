from pathlib import Path
import cv2
from src.vision.vision_parser import VisionParser

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw_screenshots"
OUTPUT_DIR = PROJECT_ROOT / "data" / "dataset_corners" / "train"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    parser = VisionParser()

    image_files = list(RAW_DIR.glob("*.jpg")) + list(RAW_DIR.glob("*.png"))
    print(f"Найдено скриншотов: {len(image_files)}")

    saved_count = 0
    for idx, img_path in enumerate(image_files):
        left, right = parser.parse_frame(img_path)

        if left is not None:
            cv2.imwrite(str(OUTPUT_DIR / f"crop_{idx}_left.png"), left)
            saved_count += 1

        if right is not None:
            cv2.imwrite(str(OUTPUT_DIR / f"crop_{idx}_right.png"), right)
            saved_count += 1

    print(f"Готово! Сохранено {saved_count} углов карт в {OUTPUT_DIR}")


if __name__ == "__main__":
    main()