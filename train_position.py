from ultralytics import YOLO
if __name__ == '__main__':
    model = YOLO('yolov8s.pt')

    result = model.train(
        data='data/dataset/data.yaml',
        epochs=100,
        imgsz=640,
        batch=8,
        device=0
    )