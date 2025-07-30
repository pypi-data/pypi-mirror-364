import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_and_visualize_mask(mask_path, target_size=(1024, 1024)):
    """
    Charge un masque de segmentation à classes discrètes, le redimensionne,
    et l'affiche avec une colormap adaptée.

    Args:
        mask_path (str): chemin vers l'image PNG du masque
        target_size (tuple): taille de sortie (H, W), ex: (256, 256)
    """
    # Lire l'image en niveaux de gris
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        print(f"⛔ Impossible de lire : {mask_path}")
        return

    # Resize sans interpolation (important pour garder les valeurs 0,1,2,...)
    resized_mask = cv2.resize(mask, target_size[::-1], interpolation=cv2.INTER_NEAREST)

    # Vérifications
    uniques = np.unique(resized_mask)
    print("Valeurs présentes dans le masque :", uniques)
    print("🧮 Nombre de pixels à 254 :", np.sum(resized_mask == 254))

    # Affichage
    plt.figure(figsize=(5, 5))
    plt.imshow(resized_mask, cmap='nipy_spectral', vmin=0, vmax=255)
    plt.title(f"Masque {target_size} - classes: {uniques}")
    plt.colorbar()
    plt.axis('off')
    plt.show()

    return resized_mask

resized = load_and_visualize_mask(r"C:\Users\TM273821\Desktop\test.png", target_size=(2024, 2024))