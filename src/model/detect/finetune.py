import torch
from pathlib import Path
from ultralytics import YOLO


class YOLOTrainer:
    def __init__(
            self, 
            dataset_yaml: Path,
            model_size: str = "yolov8m",
            epochs: int = 50,
            patience: int = 10,
            lr: float = 0.005,
            imgz: int = 640,
            batch_size: int = 16,
            device: str = "cuda"
        ):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.dataset_yaml = dataset_yaml
        self.epochs = epochs
        self.batch_size = batch_size
        self.imgz = imgz
        self.lr = lr
        self.patience = patience
        self.model_size = model_size
        self.model_path = Path(f"yolov8_finetuned.pt")

        self.model = YOLO(f"{model_size}.pt").to(self.device)
        print(f"Loaded YOLO model: {model_size}")

    def train(self):
        """Fine-tunes YOLOv8 on the dataset."""
        print(f"Starting training on {self.dataset_yaml} for {self.epochs} epochs...")

        resume_checkpoint = Path("yolo_training/football_yolov8/weights/last.pt")

        if resume_checkpoint.exists():
            self.model = YOLO(resume_checkpoint).to(self.device)  # Resume from last checkpoint
            self.resume=True
            print(f"Resuming training from {resume_checkpoint}")

        else:
            self.model = YOLO(f"{self.model_size}.pt").to(self.device)  # Start fresh
            self.resume=False
            print(f"Starting new training from {self.model_size}.pt")


        self.model.train(
            data=self.dataset_yaml,
            epochs=self.epochs,
            batch=self.batch_size,
            device=self.device,
            resume=self.resume,
            imgsz=self.imgz,
            patience=self.patience,
            lr0=self.lr,
            save=True,
            save_period=5,
            project="yolo_training",
            name="football_yolov8",
            exist_ok=True
        )
        
        print("Training complete!")

    def save_model(self, save_path: str = "yolov8_finetuned.pt"):
        """Saves the best-trained model weights."""
        best_model_path = Path("yolo_training/football_yolov8/weights/best.pt")
        if best_model_path.exists():
            best_model_path.rename(save_path)
            print(f"Model saved to {save_path}")
        else:
            print("No trained model found. Check training output.")

    def evaluate(self):
        """Runs validation on the trained model."""
        print("Evaluating model...")
        metrics = self.model.val()
        print(metrics)
        return metrics
    
    def predict(self, image_path: str):
        """Runs inference on a sample image."""
        print(f"Running inference on {image_path}")
        results = self.model(image_path)
        results.show()

if __name__ == "__main__":
    data_path = Path(__file__).resolve().parents[3] / "data"
    dataset_yaml = data_path / "00--raw" / "football-players-detection.v12i.yolov8" / "data.yaml"
    trainer = YOLOTrainer(dataset_yaml, model_size="yolov8m", epochs=200, batch_size=2)

    save_path = data_path / "10--models" / "yolo_finetune2.pt"
    trainer.train()
    trainer.evaluate()
    trainer.save_model(save_path=save_path)
