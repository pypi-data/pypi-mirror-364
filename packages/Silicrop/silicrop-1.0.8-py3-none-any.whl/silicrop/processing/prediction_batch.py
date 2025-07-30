import os
import cv2
import time
import torch
import numpy as np
from PIL import Image, ImageOps
from torchvision import transforms
import segmentation_models_pytorch as smp
from silicrop.processing.meplat import extract_meplat_parts


class EllipsePredictorBatch:
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = smp.Unet(
            encoder_name="resnet18",
            encoder_weights="imagenet",
            in_channels=3,
            classes=1
        ).to(self.device)

        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

    def predict_mask(self, img_pil):
        img_pil = ImageOps.exif_transpose(img_pil)
        img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.model(img_tensor)
            mask = torch.sigmoid(output).squeeze().cpu().numpy()
        return mask

    def run_inference(self, img_path, dataset_type='200'):
        t_start = time.time()
        orig_img = cv2.imread(img_path)
        if orig_img is None:
            print(f"❌ Erreur de lecture : {img_path}")
            return None, None, None

        h, w = orig_img.shape[:2]
        img_rgb = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        mask = self.predict_mask(img_pil)
        mask_bin = (mask > 0.5).astype(np.uint8) * 255
        mask_resized = cv2.resize(mask_bin, (w, h), interpolation=cv2.INTER_NEAREST)

        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            print("❌ Aucun contour détecté.")
            return None, mask_resized, None

        contour = max(contours, key=cv2.contourArea)
        contour = contour[:, 0, :]

        if dataset_type == '150':
            mask_flat, flat_part, curved_part = extract_meplat_parts(
                contour, window_size=20, error_thresh=1.5, min_length=30,
                gap_tolerance=5, top_n=20
            )
            if len(curved_part) < 5:
                print("❌ Pas assez de points pour l'ellipse.")
                return None, mask_resized, None
            ellipse = cv2.fitEllipse(curved_part.reshape(-1, 1, 2))
            points = [flat_part[0], flat_part[1], flat_part[2], flat_part[3], flat_part[-1]]
        else:
            if len(contour) < 5:
                print("❌ Contour trop court pour ellipse.")
                return None, mask_resized, None
            ellipse = cv2.fitEllipse(contour.reshape(-1, 1, 2))
            points = contour

        # Apply warp manually
        result = self.warp_image(orig_img, ellipse, points)
        return result, mask_resized, ellipse

    def warp_image(self, image, ellipse, points):
        (cx, cy), (MA, ma), angle = ellipse
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.ellipse(mask, (int(cx), int(cy)), (int(MA / 2), int(ma / 2)), angle, 0, 360, 255, -1)

        diameter = int(max(MA, ma))
        pts1 = cv2.boxPoints(ellipse).astype(np.float32)
        pts2 = np.array([
            [0, 0],
            [diameter - 1, 0],
            [diameter - 1, diameter - 1],
            [0, diameter - 1]
        ], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(image, matrix, (diameter, diameter))
        warped_mask = cv2.warpPerspective(mask, matrix, (diameter, diameter))

        result = np.ones_like(warped, dtype=np.uint8) * 255
        for c in range(3):
            result[:, :, c] = np.where(warped_mask == 255, warped[:, :, c], 255)

        return result


if __name__ == "__main__":
    model_path = r"C:\Users\TM273821\Desktop\Silicrop - model\unet_200300_notch_0.001_250_4__weights.pth"
    image_dir = r"C:\Users\TM273821\Desktop\Test_Batch\file"
    output_dir = r"C:\Users\TM273821\Desktop\Test_Batch\processed"

    os.makedirs(output_dir, exist_ok=True)
    predictor = EllipsePredictorBatch(model_path)

    for i, filename in enumerate(os.listdir(image_dir), 1):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            img_path = os.path.join(image_dir, filename)
            print(f"[{i}] ▶ Traitement : {filename}")

            result_img, mask, ellipse = predictor.run_inference(img_path, dataset_type='200')

            if result_img is not None:
                out_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_processed.png")
                cv2.imwrite(out_path, result_img)
                print(f"   💾 Sauvé : {out_path}\n")
            else:
                print("   ❌ Erreur\n")