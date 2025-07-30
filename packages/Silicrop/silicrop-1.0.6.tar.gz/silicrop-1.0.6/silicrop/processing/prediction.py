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
    def __init__(self, model_path, fit_crop_widget):
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

    def run_inference(self, img_path, dataset_type='200', plot=True):
        """
        Run the inference pipeline on the given image.
        """
        mem_before = self.process.memory_info().rss / 1024 ** 2

        # Load and preprocess the image
        img_pil = Image.open(img_path).convert('RGB')
        img_pil = ImageOps.exif_transpose(img_pil)
        orig_img = np.array(img_pil)
        orig_img = cv2.cvtColor(orig_img, cv2.COLOR_RGB2BGR)

        # Predict the mask
        start_time = time.time()
        mask = self.predict_mask(img_pil)
        elapsed = time.time() - start_time
        mem_after = self.process.memory_info().rss / 1024 ** 2

        # Post-process the mask
        h, w = orig_img.shape[:2]
        mask_bin = (mask > 0.5).astype(np.uint8) * 255
        mask_resized = cv2.resize(mask_bin, (w, h), interpolation=cv2.INTER_NEAREST)
        _, mask_thresh = cv2.threshold(mask_resized, 127, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        mask_clean = cv2.morphologyEx(mask_thresh, cv2.MORPH_CLOSE, kernel)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            print("❌ No contours detected.")
            return None, None, None

        contour = max(contours, key=cv2.contourArea)
        contour = contour[:, 0, :]  # (N, 1, 2) → (N, 2)

        # Process based on dataset type
        show_flat = False
        if dataset_type == '150':
            mask_flat, flat_part, curved_part = extract_meplat_parts(
                contour,
                window_size=20,
                error_thresh=1.5,
                min_length=30,
                gap_tolerance=5,
                top_n=20
            )
            show_flat = True

            if len(curved_part) < 5:
                print("❌ Not enough points for ellipse (150).")
                return None, mask, None

            ellipse = cv2.fitEllipse(curved_part.reshape(-1, 1, 2))
            points = [flat_part[0], flat_part[1], flat_part[2], flat_part[3], flat_part[-1]]
        else:
            if len(contour) < 5:
                print("❌ Not enough points for ellipse (200).")
                return None, mask, None
            ellipse = cv2.fitEllipse(contour.reshape(-1, 1, 2))
            points = contour

        # ---- Projection with FitAndCrop
        self.fit_crop_widget.image = orig_img
        self.fit_crop_widget.ellipse_params = ellipse
        self.fit_crop_widget.process_and_display_corrected_image(points=points)

        result_img = self.fit_crop_widget.processed_ellipse
        if result_img is None:
            print("❌ Transformation failed.")
            return None, mask, ellipse

        # Plot results if requested
        if plot:
            plt.figure(figsize=(16, 5))

            plt.subplot(1, 4, 1)
            plt.title("Original Image")
            plt.imshow(cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB))
            plt.axis('off')

            plt.subplot(1, 4, 2)
            plt.title("Mask + Ellipse")
            plt.imshow(mask_resized, cmap='gray')
            ax = plt.gca()
            (cx, cy), (MA, ma), angle = ellipse
            ell_patch = MplEllipse((cx, cy), MA, ma, angle=angle, edgecolor='red', facecolor='none', linewidth=2)
            ax.add_patch(ell_patch)

            if show_flat and flat_part is not None and len(flat_part) > 0:
                plt.scatter(flat_part[:, 0], flat_part[:, 1], s=5, c='cyan', label='Flat Part')
                plt.legend()

            plt.axis('off')

            plt.subplot(1, 4, 3)
            plt.title("Transformed Image")
            plt.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
            plt.axis('off')

            # ➕ New subplot 4: After rotation (if available)
            rotated_img = getattr(self.fit_crop_widget.processed_widget, "image", None)
            if rotated_img is not None:
                plt.subplot(1, 4, 4)
                plt.title("After Rotation")
                plt.imshow(cv2.cvtColor(rotated_img, cv2.COLOR_BGR2RGB))
                plt.axis('off')
            else:
                print("⚠️ No 'image' visual in processed_widget")

            plt.tight_layout()
            plt.show()

        print(f"✅ Inference: {elapsed:.3f}s | RAM: {mem_after - mem_before:.2f}MB")

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
    result_img, mask, ellipse = predictor.run_inference(img_path, dataset_type='150', plot=True)
