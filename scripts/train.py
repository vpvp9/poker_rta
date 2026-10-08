from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('yolov8n-seg.pt')

    model.train(
        data='dataset/data.yaml',  # путь к data.yaml
        epochs=50,
        imgsz=640,
        device='cpu'  # Указываем CPU
    )