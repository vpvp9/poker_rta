from ultralytics import YOLO
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_YAML_PATH = PROJECT_ROOT / "data" / "dataset" / "data.yaml"
if __name__ == '__main__':
    model = YOLO('yolov8s.pt')

    result = model.train(
        data=str(DATA_YAML_PATH),
        epochs=100,
        imgsz=640,
        batch=4,
        device=0
    )
