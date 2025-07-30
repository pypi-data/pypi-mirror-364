import torch
import numpy as np
import cv2
import time
from torchvision import transforms
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse as MplEllipse
import segmentation_models_pytorch as smp
import psutil
from silicrop.processing.crop import FitAndCrop
from silicrop.processing.rotate import Rotate
from silicrop.processing.meplat import extract_meplat_parts


class EllipsePredictor:
    def __init__(self, model_path, fit_crop_widget=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.fit_crop_widget = fit_crop_widget

        # Load the U-Net model with ResNet-18 as the encoder
        self.model = smp.Unet(
            encoder_name="resnet18",  # Use ResNet-18 as the backbone
            encoder_weights="imagenet",  # Pre-trained weights on ImageNet
            in_channels=3,  # Input channels (e.g., RGB)
            classes=1  # Output channels (binary segmentation)
        ).to(self.device)

        # Load the model weights
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

        self.process = psutil.Process()

    def predict_mask(self, img_pil):
        """
        Predict the segmentation mask for the given image.
        """
        img_pil = ImageOps.exif_transpose(img_pil)
        img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)

        # Perform inference
        with torch.no_grad():
            output = self.model(img_tensor)
            mask = torch.sigmoid(output).squeeze().cpu().numpy()

        return mask

    def run_inference(self, img_path, dataset_type='200', plot=False, apply_projection=True):
        """
        Optimized version of the inference pipeline, suitable for batch usage.
        - No matplotlib.
        - Minimal memory & time overhead.
        """
        import time
        import os

        t_total = time.time()

        # 🧠 Charge image avec OpenCV (rapide)
        orig_img = cv2.imread(img_path)
        if orig_img is None:
            print(f"❌ Impossible de lire : {img_path}")
            return None, None, None

        h, w = orig_img.shape[:2]

        # 🔁 Conversion vers PIL uniquement pour le modèle
        img_rgb = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        # 🤖 Prédiction (modèle)
        t0 = time.time()
        mask = self.predict_mask(img_pil)  # doit retourner image [0-1]
        print(f"  ⏱️ Modèle : {time.time() - t0:.3f}s")

        # 📉 Binarisation rapide
        mask_bin = (mask > 0.5).astype(np.uint8) * 255
        mask_resized = cv2.resize(mask_bin, (w, h), interpolation=cv2.INTER_NEAREST)

        # # 🧽 Nettoyage léger
        # kernel = np.ones((3, 3), np.uint8)
        # mask_clean = cv2.morphologyEx(mask_resized, cv2.MORPH_CLOSE, kernel)

        # 🔎 Contours
        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            print("❌ Aucun contour trouvé.")
            return None, None, None

        contour = max(contours, key=cv2.contourArea)
        contour = contour[:, 0, :]  # (N, 1, 2) → (N, 2)

        # 🔺 Fit ellipse selon dataset
        if dataset_type == '150':
            from silicrop.processing.meplat import extract_meplat_parts
            mask_flat, flat_part, curved_part = extract_meplat_parts(
                contour, window_size=20, error_thresh=1.5, min_length=30,
                gap_tolerance=5, top_n=20
            )
            if len(curved_part) < 5:
                print("❌ Pas assez de points (150).")
                return None, mask_resized, None

            ellipse = cv2.fitEllipse(curved_part.reshape(-1, 1, 2))
            points = [flat_part[0], flat_part[1], flat_part[2], flat_part[3], flat_part[-1]]
        else:
            if len(contour) < 5:
                print("❌ Pas assez de points (200).")
                return None, mask_resized, None

            ellipse = cv2.fitEllipse(contour.reshape(-1, 1, 2))
            points = contour


        if apply_projection :
            self.fit_crop_widget.image = orig_img
            self.fit_crop_widget.ellipse_params = ellipse
            self.fit_crop_widget.process_and_display_corrected_image(points=points)
            result_img = self.fit_crop_widget.processed_ellipse
        else:
            result_img = orig_img.copy()

        print(f"  ✅ Total inference : {time.time() - t_total:.3f}s")
        return result_img, mask_resized, ellipse


# ==== Debugging Entry Point ====
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    model_path = r"C:\Users\TM273821\Desktop\Silicrop - model\unet_200300_notch_0.001_250_4__weights.pth"
    img_path = r"C:\Users\TM273821\Desktop\Database\200\Image\105.jpg"

    rotate_widget = Rotate()
    fit_crop = FitAndCrop(processed_label=rotate_widget, filter_150_button=True, header=False)

    predictor = EllipsePredictor(model_path, fit_crop)
    result_img, mask, ellipse = predictor.run_inference(img_path, dataset_type='200', plot=True)
