"""
# Compute Points 3D Module - Simulation de Route pour Caméras Embarquées

## Vue d'ensemble

Ce module simule la géométrie 3D d'une route plane vue par une caméra embarquée sur véhicule.
Il est particulièrement adapté aux caméras GoPro Hero 13 en mode Linear, mais peut être configuré
pour d'autres caméras moyennant ajustement des paramètres de calibration.

## Principe de fonctionnement

### Modèle géométrique simplifié
Le module repose sur plusieurs hypothèses simplifiées mais réalistes :
- **Route plane** : La chaussée est modélisée comme un plan horizontal parfait (Z=0)
- **Caméra fixe** : Position et orientation constantes par rapport au véhicule
- **Pas d'obstacles** : Seul le plan route est considéré, pas de véhicules ou piétons

### Processus de projection inverse
1. **Étalonnage caméra** : Utilise les paramètres intrinsèques (focale, centre optique)
2. **Génération de rayons** : Chaque pixel génère un rayon 3D depuis la caméra
3. **Intersection** : Calcul du point d'intersection entre chaque rayon et le plan route
4. **Cartes 3D** : Production de cartes X, Y, Z associant chaque pixel à sa position 3D

## Applications pratiques

- **Tests et validation** : Génération de données 3D de référence pour valider des algorithmes
- **Inspection routière** : Analyse de la géométrie de chaussée pour détection de défauts
- **Navigation** : Cartographie locale pour systèmes d'aide à la conduite

## Système de coordonnées détaillé

### Repère Image (pixels // caméra)

Le repère image standard utilisé en vision par ordinateur.

**Unité :** pixels

**Axes :**
- **X** : vers la droite de l'image (axe horizontal)
- **Y** : vers le bas de l'image (axe vertical)

**Origine (0,0) :**
- Coin supérieur gauche de l'image
- Première ligne, première colonne du tableau de pixels

**Notes importantes :**
- Les coordonnées sont toujours positives dans l'image
- La depth map associée utilise les mêmes coordonnées mais en mètres

### Repère Véhicule GoPro 13 (points 3D // monde réel)

Système de coordonnées 3D aligné sur l'orientation naturelle du véhicule.
Compatible avec les standards automotive et robotique.

**Unité :** mètres

**Axes (convention main droite) :**
- **X** : vers l'avant du véhicule (direction de marche)
- **Y** : vers la gauche du véhicule (côté conducteur en conduite à droite)
- **Z** : vers le haut (perpendiculaire au sol)

**Origine (0,0,0) :**
- **X = 0** : directement sous la caméra (projection verticale)
- **Y = 0** : dans l'axe longitudinal du véhicule
- **Z = 0** : au niveau de la chaussée

### Correspondance pixel ↔ monde réel

Chaque pixel (u,v) de l'image correspond à un point 3D (X,Y,Z) sur la route :
- **Pixel proche du bas** → Point proche du véhicule (X faible)
- **Pixel au centre horizontalement** → Point dans l'axe du véhicule (Y≈0)
- **Pixel vers le haut** → Point lointain devant le véhicule (X élevé)

"""

from dataclasses import dataclass

import cv2
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Calibration:
    """
    Stocke les paramètres intrinsèques d'une caméra après étalonnage.

    Params:
    - camera_matrix : Matrice 3x3 des paramètres intrinsèques (focale, centre optique)
    - dist_coeffs : Vecteur des 5 coefficients de distorsion (optionnels, par défaut None)

    En vision par ordinateur, chaque caméra a des caractéristiques physiques uniques
    qui influencent la façon dont elle projette le monde 3D sur le capteur 2D.

    Paramètres intrinsèques principaux :
    - **Focale** : Distance entre l'objectif et le capteur (détermine le zoom)
    - **Centre optique** : Point où l'axe optique rencontre le capteur
    - **Distorsion** : Déformations géométriques de l'objectif (barillet, coussinet)

    Ces paramètres sont obtenus par étalonnage avec une mire (damier, cercles).
    """

    camera_matrix: np.ndarray  # Matrice 3x3 des paramètres intrinsèques
    dist_coeffs: np.ndarray | None = None  # Coefficients de distorsion (optionnel)


def get_calibration_from_focal(
    image_width: int = 1920,
    image_height: int = 1080,
    focal_px: float = 1200.0,
) -> Calibration:
    """
    Génère les paramètres de calibration d'une caméra GoPro Hero 13 en mode Linear.

    La calibration définit comment les points 3D du monde sont projetés sur l'image 2D.

    **Matrice caméra (camera_matrix) :**
    ```
    [fx  0  cx]
    [ 0 fy  cy]
    [ 0  0   1]
    ```
    Où :
    - fx, fy : focales en pixels (généralement égales pour capteurs carrés)
    - cx, cy : centre optique en pixels (idéalement au centre de l'image)

    **Distorsions :**
    Les GoPro utilisent des objectifs ultra grand-angle qui créent des distorsions.
    Le mode Linear applique une correction automatique, d'où coefficients à zéro.

    **Paramètres typiques GoPro Hero 13 :**
    - Résolution : 1920x1080 pixels
    - Focale : ~1000-1200 pixels (équivaut à ~24mm en 35mm)
    - Champ de vision : ~90° en diagonal après correction Linear

    Args:
        image_width: Largeur image en pixels
        image_height: Hauteur image en pixels
        focal_px: Focale en pixels (ajustable selon conditions)

    Returns:
        Calibration: Objet contenant matrice caméra et coefficients distorsion
    """

    # Focales horizontale et verticale (généralement identiques)
    fx = fy = focal_px

    # Centre optique : théoriquement au centre, mais peut être décalé
    # par stabilisation électronique ou défauts de fabrication
    cx = image_width / 2.0
    cy = image_height / 2.0

    # Construction de la matrice intrinsèque 3x3
    camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)

    # Coefficients de distorsion : [k1, k2, p1, p2, k3]
    # Mode Linear GoPro = distorsion déjà corrigée → coefficients nuls
    dist_coeffs = np.array([0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    return Calibration(camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)


class PlaneRoadModel:
    """
    Modèle pour projeter une image sur un plan de route (z=0)

    Système de coordonnées GoPro 13:
    - X: avant (forward)
    - Y: gauche (left)
    - Z: haut (up)

    La route est située sur le plan z=0
    """

    def __init__(
        self,
        camera_calibration: Calibration,
        camera_pitch: float = 30.0,  # en degrés
        camera_yaw: float = 0.0,  # en degrés
        camera_roll: float = 0.0,  # en degrés
        camera_height: float = 1.1,  # en mètres
    ):  # hauteur de la caméra au-dessus du sol
        self.camera_calibration = camera_calibration
        self.camera_pitch = np.radians(camera_pitch)  # Convertir en radians
        self.camera_yaw = np.radians(camera_yaw)
        self.camera_roll = np.radians(camera_roll)
        self.camera_position = np.array([0.0, 0.0, camera_height])  # Caméra à hauteur h (GoPro 13: Z=up)
        self.points3d = None

        # Matrice de rotation de la caméra
        self.rotation_matrix = self._compute_rotation_matrix()

    def _compute_rotation_matrix(self) -> np.ndarray:
        """
        Calcule la matrice de rotation 3D pour orienter la caméra dans l'espace.

        **Principe des rotations 3D :**
        Une caméra peut être orientée selon 3 axes de rotation (angles d'Euler) :
        - **Pitch** : basculement avant/arrière (regarder vers le haut/bas)
        - **Yaw** : rotation gauche/droite (regarder à gauche/droite)
        - **Roll** : inclinaison latérale (pencher la tête)

        **Système de coordonnées GoPro 13 :**
        - X = avant du véhicule
        - Y = gauche du véhicule
        - Z = haut (vers le ciel)

        **Ordre des rotations :** Rz @ Ry @ Rx (standard en robotique)
        L'ordre est important car les rotations ne commutent pas !

        **Cas typique inspection route :**
        - Pitch : -30° (caméra inclinée vers le bas pour voir la chaussée)
        - Yaw : 0° (caméra alignée avec la direction de marche)
        - Roll : 0° (caméra horizontale, pas penchée)

        Returns:
            np.ndarray: Matrice de rotation 3x3 transformant les coordonnées caméra
                       vers les coordonnées monde (véhicule)
        """

        # Rotation autour de Y (pitch - inclinaison avant/arrière)
        # Angle positif = regarder vers le haut, négatif = vers le bas
        Ry = np.array(
            [
                [np.cos(self.camera_pitch), 0, np.sin(self.camera_pitch)],
                [0, 1, 0],
                [-np.sin(self.camera_pitch), 0, np.cos(self.camera_pitch)],
            ]
        )

        # Rotation autour de Z (yaw - rotation gauche/droite)
        # Angle positif = rotation vers la gauche
        Rz = np.array(
            [
                [np.cos(self.camera_yaw), -np.sin(self.camera_yaw), 0],
                [np.sin(self.camera_yaw), np.cos(self.camera_yaw), 0],
                [0, 0, 1],
            ]
        )

        # Rotation autour de X (roll - inclinaison latérale)
        # Angle positif = rotation horaire vue depuis l'avant
        Rx = np.array(
            [
                [1, 0, 0],
                [0, np.cos(self.camera_roll), -np.sin(self.camera_roll)],
                [0, np.sin(self.camera_roll), np.cos(self.camera_roll)],
            ]
        )

        # Composition des rotations : ordre Rz @ Ry @ Rx
        # Applique d'abord roll, puis pitch, puis yaw
        return Rz @ Ry @ Rx

    def get_points3D(self, image: cv2.typing.MatLike | None = None, image_size: tuple[int, int] | None = None) -> np.ndarray:
        """
        Calcule les coordonnées 3D de chaque pixel par projection inverse géométrique.

        **Principe de la projection inverse :**
        1. **Pixel → Rayon 3D** : Chaque pixel (u,v) génère un rayon depuis la caméra
        2. **Transformation** : Le rayon est orienté selon la pose de la caméra
        3. **Intersection** : Calcul où le rayon rencontre le plan route (Z=0)
        4. **Point 3D** : Coordonnées (X,Y,Z) du point d'intersection

        **Modèle pinhole :**
        Les rayons partent du centre optique et passent par chaque pixel.
        La direction du rayon dépend de la position du pixel et de la focale.

        **Système GoPro 13 :**
        - Rayons normalisés puis transformés par matrice de rotation
        - Intersection avec plan horizontal Z=0 (route)
        - Points invalides (rayons vers le haut) mis à (0,0,0)

        Args:
            image: Image source (utilisée uniquement pour les dimensions). Optionnel si image_size est fourni.
            image_size: Tuple (width, height) des dimensions de l'image. Optionnel si image est fourni.

        Returns:
            np.ndarray: Tableau 3D (H,W,3) des coordonnées (X,Y,Z) en mètres
                       Forme (height, width, 3) où [:,:,0]=X, [:,:,1]=Y, [:,:,2]=Z
        
        Raises:
            ValueError: Si ni image ni image_size ne sont fournis.
        """
        if image is not None:
            h, w = image.shape[:2]
        elif image_size is not None:
            w, h = image_size
        else:
            raise ValueError("Either image or image_size must be provided")
        fx = self.camera_calibration.camera_matrix[0, 0]
        fy = self.camera_calibration.camera_matrix[1, 1]
        cx = self.camera_calibration.camera_matrix[0, 2]
        cy = self.camera_calibration.camera_matrix[1, 2]

        # Créer une grille de coordonnées pixel (u, v) pour tous les pixels
        x_coords, y_coords = np.meshgrid(np.arange(w), np.arange(h))

        # === ÉTAPE 1: Conversion pixel → rayon caméra ===
        # Modèle pinhole : (u-cx)/fx et (v-cy)/fy donnent les directions angulaires
        # Pour GoPro 13: X=avant, Y=gauche, Z=haut

        x_norm = np.ones_like(x_coords)  # Direction avant unitaire (profondeur)
        y_norm = -(x_coords - cx) / fx  # Vers la gauche (signe - pour convention GoPro)
        z_norm = -(y_coords - cy) / fy  # Vers le haut (signe - car pixels Y vers le bas)

        # Construire les vecteurs directeurs des rayons (non normalisés)
        rays_cam = np.stack([x_norm, y_norm, z_norm], axis=-1)

        # === ÉTAPE 2: Normalisation des rayons ===
        # Chaque rayon doit être unitaire pour les calculs d'intersection
        norms = np.linalg.norm(rays_cam, axis=2, keepdims=True)
        rays_cam_normalized = rays_cam / norms

        # === ÉTAPE 3: Transformation caméra → monde ===
        # Appliquer la rotation de la caméra pour orienter les rayons
        rays_world = np.einsum("ij,hwj->hwi", self.rotation_matrix, rays_cam_normalized)

        # === ÉTAPE 4: Intersection rayon-plan ===
        # Plan route: Z = 0. Équation paramétrique: P = camera_pos + t * ray_direction
        # À l'intersection: camera_pos[2] + t * ray_z = 0 → t = -camera_pos[2] / ray_z

        ray_z = rays_world[:, :, 2]  # Composante Z des rayons (vers le haut/bas)
        valid_mask = ray_z < 0  # Rayons pointant vers le bas (vers la route)

        # Calcul du paramètre t (distance le long du rayon)
        t = np.zeros_like(ray_z)
        t[valid_mask] = -self.camera_position[2] / ray_z[valid_mask]

        # === ÉTAPE 5: Calcul des points 3D finaux ===
        # Point d'intersection = position_caméra + t * direction_rayon
        points3D = self.camera_position[np.newaxis, np.newaxis, :] + t[:, :, np.newaxis] * rays_world

        # Correction numérique : forcer Z=0 pour les points très proches
        tolerance = 1e-10
        near_zero_mask = valid_mask & (np.abs(points3D[:, :, 2]) < tolerance)
        points3D[near_zero_mask, 2] = 0.0

        # Points invalides (rayons vers le haut) → coordonnées nulles
        points3D[~valid_mask] = [0.0, 0.0, 0.0]

        self.points3d = points3D.astype(np.float32)
        return self.points3d

    def get_points3D_from_img_path(self, image_path: str) -> np.ndarray:
        """
        Charge une image depuis un fichier et calcule les points 3D correspondants.

        Pratique pour traiter des images stockées sur disque sans les charger manuellement.

        Args:
            image_path: Chemin vers le fichier image (formats supportés par OpenCV)
                       Ex: 'route.jpg', 'dashcam_frame.png'

        Returns:
            np.ndarray: Points 3D calculés, même format que get_points3D()

        Raises:
            ValueError: Si l'image ne peut pas être chargée (fichier inexistant, format non supporté)
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
        return self.get_points3D(image)

    def save_points3D_as_npz(self, path: str) -> None:
        """Sauvegarde les points 3D au format NPZ"""
        if self.points3d is None:
            raise ValueError("Points 3D non calculés. Appelez d'abord get_points3D().")
        np.savez_compressed(path, points3D=self.points3d)
        print(f"Points 3D sauvegardés dans: {path}")

    def load_points3D_from_npz(self, depth_map_path: str) -> np.ndarray:
        """Charge les points 3D depuis un fichier NPZ"""
        data = np.load(depth_map_path)
        self.points3d = data["points3D"]
        return self.points3d

    def get_scene_statistics(self) -> dict:
        """Calcule et affiche les statistiques de la scène 3D dans le système GoPro 13"""
        if self.points3d is None:
            raise ValueError("Points 3D non calculés. Appelez d'abord get_points3D().")

        # Masquer les points invalides (0,0,0)
        valid_mask = ~((self.points3d[:, :, 0] == 0) & (self.points3d[:, :, 1] == 0) & (self.points3d[:, :, 2] == 0))

        if not np.any(valid_mask):
            return {"error": "Aucun point 3D valide trouvé"}

        valid_points = self.points3d[valid_mask]

        # Coordonnées GoPro 13: X=avant, Y=gauche, Z=haut
        # Coordonnées X (distance avant)
        x_coords = valid_points[:, 0]
        distance_min = np.min(x_coords)
        distance_max = np.max(x_coords)

        # Coordonnées Y (largeur latérale)
        y_coords = valid_points[:, 1]
        width_min = np.min(y_coords)
        width_max = np.max(y_coords)
        total_width = width_max - width_min

        # Coordonnées Z (hauteur - devrait être proche de 0 pour la route)
        z_coords = valid_points[:, 2]
        height_min = np.min(z_coords)
        height_max = np.max(z_coords)

        stats = {
            "largeur_totale_m": total_width,
            "largeur_min_m": width_min,
            "largeur_max_m": width_max,
            "distance_min_m": distance_min,
            "distance_max_m": distance_max,
            "hauteur_min_m": height_min,
            "hauteur_max_m": height_max,
            "nb_points_valides": np.sum(valid_mask),
            "nb_points_total": self.points3d.shape[0] * self.points3d.shape[1],
        }

        return stats

    def verify_z_zero_constraint(self, tolerance: float = 1e-6) -> dict:
        """Vérifie si tous les points valides ont z=0 (ou très proche de 0) dans le système GoPro 13"""
        if self.points3d is None:
            raise ValueError("Points 3D non calculés. Appelez d'abord get_points3D().")

        # Masquer les points invalides (0,0,0)
        valid_mask = ~((self.points3d[:, :, 0] == 0) & (self.points3d[:, :, 1] == 0) & (self.points3d[:, :, 2] == 0))

        if not np.any(valid_mask):
            return {"error": "Aucun point 3D valide trouvé"}

        valid_points = self.points3d[valid_mask]
        z_coords = valid_points[:, 2]  # Z=hauteur dans GoPro 13

        # Vérifier que tous les z sont proche de 0 (route)
        points_near_zero = np.abs(z_coords) <= tolerance
        all_z_zero = np.all(points_near_zero)

        # Statistiques détaillées
        max_z_deviation = np.max(np.abs(z_coords))
        mean_z_deviation = np.mean(np.abs(z_coords))
        points_within_tolerance = np.sum(points_near_zero)
        total_valid_points = len(z_coords)

        return {
            "all_z_zero": all_z_zero,
            "tolerance": tolerance,
            "max_z_deviation": max_z_deviation,
            "mean_z_deviation": mean_z_deviation,
            "points_within_tolerance": points_within_tolerance,
            "total_valid_points": total_valid_points,
            "percentage_within_tolerance": (points_within_tolerance / total_valid_points) * 100,
        }

    def print_scene_statistics(self) -> None:
        """Affiche les statistiques de la scène de manière formatée"""
        stats = self.get_scene_statistics()

        if "error" in stats:
            print(f"Erreur: {stats['error']}")
            return

        print("\n" + "=" * 50)
        print("STATISTIQUES DE LA SCÈNE 3D - GoPro Hero 13 Linear 90°")
        print("=" * 50)
        print(f"📏 Largeur totale visible    : {stats['largeur_totale_m']:.2f} m")
        print(f"   ├─ Largeur min (gauche)  : {stats['largeur_min_m']:.2f} m")
        print(f"   └─ Largeur max (droite)  : {stats['largeur_max_m']:.2f} m")
        print()
        print("📐 Distance de vue")
        print(f"   ├─ Distance minimale     : {stats['distance_min_m']:.2f} m")
        print(f"   └─ Distance maximale     : {stats['distance_max_m']:.2f} m")
        print()
        print("📊 Hauteurs (route = 0m)")
        print(f"   ├─ Hauteur minimale      : {stats['hauteur_min_m']:.3f} m")
        print(f"   └─ Hauteur maximale      : {stats['hauteur_max_m']:.3f} m")
        print()
        print("🔢 Points calculés")
        print(f"   ├─ Points valides        : {stats['nb_points_valides']:,}")
        print(f"   ├─ Points totaux         : {stats['nb_points_total']:,}")
        print(f"   └─ Pourcentage valide    : {(stats['nb_points_valides'] / stats['nb_points_total'] * 100):.1f}%")
        print()

        # Vérification z=0 (route dans GoPro 13)
        z_check = self.verify_z_zero_constraint()
        if "error" not in z_check:
            status_icon = "✅" if z_check["all_z_zero"] else "⚠️"
            print(f"🎯 Vérification contrainte z=0 (route) {status_icon}")
            print(f"   ├─ Tous les points z≈0   : {'Oui' if z_check['all_z_zero'] else 'Non'}")
            print(f"   ├─ Tolérance             : {z_check['tolerance']:.2e}")
            print(f"   ├─ Déviation max         : {z_check['max_z_deviation']:.6f} m")
            print(f"   ├─ Déviation moyenne     : {z_check['mean_z_deviation']:.6f} m")
            print(f"   └─ Points dans tolérance : {z_check['percentage_within_tolerance']:.1f}%")
        print("=" * 50)

    def visualize_depth_map(self, max_distance: float = 50.0) -> np.ndarray:
        """Crée une visualisation de la carte de profondeur"""
        if self.points3d is None:
            raise ValueError("Points 3D non calculés.")

        # Calculer les distances depuis la caméra
        distances = np.linalg.norm(self.points3d - self.camera_position, axis=2)

        # Normaliser pour la visualisation
        distances_normalized = np.clip(distances / max_distance, 0, 1)
        depth_vis = (255 * (1 - distances_normalized)).astype(np.uint8)

        return depth_vis

    def create_coordinate_maps(self, save_path: str | None = None) -> dict:
        """Crée les cartes de coordonnées X, Y, Z et les sauvegarde pour le système GoPro 13"""
        if self.points3d is None:
            raise ValueError("Points 3D non calculés.")

        # Extraire les coordonnées GoPro 13: X=avant, Y=gauche, Z=haut
        x_map = self.points3d[:, :, 0]  # Coordonnées X (distance avant)
        y_map = self.points3d[:, :, 1]  # Coordonnées Y (largeur latérale)
        z_map = self.points3d[:, :, 2]  # Coordonnées Z (hauteur)

        # Calculer les distances depuis la caméra pour la depth map
        distances = np.linalg.norm(self.points3d - self.camera_position, axis=2)

        # Créer les visualisations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Cartes de Coordonnées 3D - GoPro Hero 13", fontsize=16)

        # Depth Map
        im1 = axes[0, 0].imshow(distances, cmap="plasma", origin="upper")
        axes[0, 0].set_title("Depth Map (Distance depuis caméra)")
        axes[0, 0].set_xlabel("Pixels X")
        axes[0, 0].set_ylabel("Pixels Y")
        plt.colorbar(im1, ax=axes[0, 0], label="Distance (m)")

        # X Map (distance avant dans GoPro 13)
        im2 = axes[0, 1].imshow(x_map, cmap="magma", origin="upper")
        axes[0, 1].set_title("X Map (Distance avant)")
        axes[0, 1].set_xlabel("Pixels X")
        axes[0, 1].set_ylabel("Pixels Y")
        plt.colorbar(im2, ax=axes[0, 1], label="X (m)")

        # Y Map (largeur latérale dans GoPro 13)
        im3 = axes[1, 0].imshow(y_map, cmap="RdBu_r", origin="upper")
        axes[1, 0].set_title("Y Map (Largeur latérale)")
        axes[1, 0].set_xlabel("Pixels X")
        axes[1, 0].set_ylabel("Pixels Y")
        plt.colorbar(im3, ax=axes[1, 0], label="Y (m)")

        # Z Map (hauteur dans GoPro 13)
        im4 = axes[1, 1].imshow(z_map, cmap="viridis", origin="upper")
        axes[1, 1].set_title("Z Map (Hauteur depuis sol)")
        axes[1, 1].set_xlabel("Pixels X")
        axes[1, 1].set_ylabel("Pixels Y")
        plt.colorbar(im4, ax=axes[1, 1], label="Z (m)")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Cartes de coordonnées sauvegardées: {save_path}")

        plt.show()

        return {"depth_map": distances, "x_map": x_map, "y_map": y_map, "z_map": z_map}

    def create_3d_surface_plot(self, subsample: int = 10, save_path: str | None = None):
        """Crée un graphique 3D de la surface Z = f(X, Y) pour le système GoPro 13"""
        if self.points3d is None:
            raise ValueError("Points 3D non calculés.")

        # Sous-échantillonner pour la performance
        x_coords = self.points3d[::subsample, ::subsample, 0]  # Distance avant
        y_coords = self.points3d[::subsample, ::subsample, 1]  # Largeur latérale
        z_coords = self.points3d[::subsample, ::subsample, 2]  # Hauteur

        # Masquer les points invalides
        valid_mask = ~((x_coords == 0) & (y_coords == 0) & (z_coords == 0))

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Surface plot
        x_valid = x_coords[valid_mask]
        y_valid = y_coords[valid_mask]
        z_valid = z_coords[valid_mask]

        # Créer un scatter plot coloré par hauteur Z (GoPro 13)
        scatter = ax.scatter(x_valid, y_valid, z_valid, c=z_valid, cmap="terrain", alpha=0.6)

        ax.set_xlabel("X (distance avant, m)")
        ax.set_ylabel("Y (largeur latérale, m)")
        ax.set_zlabel("Z (hauteur, m)")
        ax.set_title("Surface 3D: Z = f(X, Y) - Vue de la route (GoPro 13)")

        # Colorbar
        plt.colorbar(scatter, ax=ax, label="Hauteur Z (m)", shrink=0.5)

        # Vue optimale pour inspection de route
        ax.view_init(elev=20, azim=45)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Graphique 3D sauvegardé: {save_path}")

        plt.show()

    def create_cross_sections(self, save_path: str | None = None):
        """Crée des coupes transversales et longitudinales pour le système GoPro 13"""
        if self.points3d is None:
            raise ValueError("Points 3D non calculés.")

        h, w = self.points3d.shape[:2]

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Coupes Transversales et Longitudinales - GoPro 13", fontsize=16)

        # Coupe transversale au centre (ligne horizontale)
        center_row = h // 2
        x_center = self.points3d[center_row, :, 0]  # Distance avant
        y_center = self.points3d[center_row, :, 1]  # Largeur latérale
        z_center = self.points3d[center_row, :, 2]  # Hauteur

        axes[0, 0].plot(y_center, z_center, "b-", linewidth=2)
        axes[0, 0].set_xlabel("Y (largeur latérale, m)")
        axes[0, 0].set_ylabel("Z (hauteur, m)")
        axes[0, 0].set_title("Profil transversal (centre image)")
        axes[0, 0].grid(True)

        axes[0, 1].plot(y_center, x_center, "r-", linewidth=2)
        axes[0, 1].set_xlabel("Y (largeur latérale, m)")
        axes[0, 1].set_ylabel("X (distance avant, m)")
        axes[0, 1].set_title("Vue de dessus - transversale")
        axes[0, 1].grid(True)

        # Coupe longitudinale au centre (ligne verticale)
        center_col = w // 2
        x_long = self.points3d[:, center_col, 0]  # Distance avant
        z_long = self.points3d[:, center_col, 2]  # Hauteur

        axes[1, 0].plot(x_long, z_long, "g-", linewidth=2)
        axes[1, 0].set_xlabel("X (distance avant, m)")
        axes[1, 0].set_ylabel("Z (hauteur, m)")
        axes[1, 0].set_title("Profil longitudinal (centre image)")
        axes[1, 0].grid(True)

        # Histogramme des distances
        distances = np.linalg.norm(self.points3d - self.camera_position, axis=2)
        valid_distances = distances[distances > 0]

        axes[1, 1].hist(valid_distances.flatten(), bins=50, alpha=0.7, color="purple")
        axes[1, 1].set_xlabel("Distance (m)")
        axes[1, 1].set_ylabel("Nombre de pixels")
        axes[1, 1].set_title("Distribution des distances")
        axes[1, 1].grid(True)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Coupes transversales sauvegardées: {save_path}")

        plt.show()

    def calculate_field_of_view(self) -> dict:
        """Calcule les angles de champ de vision de la caméra pour debug"""
        fx = self.camera_calibration.camera_matrix[0, 0]
        fy = self.camera_calibration.camera_matrix[1, 1]
        cx = self.camera_calibration.camera_matrix[0, 2]
        cy = self.camera_calibration.camera_matrix[1, 2]

        # Dimensions de l'image (déduite des paramètres de calibration)
        image_width = 2 * cx  # cx devrait être au centre
        image_height = 2 * cy  # cy devrait être au centre

        # Calcul des angles de champ de vision en degrés
        fov_horizontal_deg = 2 * np.arctan(image_width / (2 * fx)) * 180 / np.pi
        fov_vertical_deg = 2 * np.arctan(image_height / (2 * fy)) * 180 / np.pi
        fov_diagonal_deg = 2 * np.arctan(np.sqrt(image_width**2 + image_height**2) / (2 * np.sqrt(fx**2 + fy**2))) * 180 / np.pi

        # Angles de vue effectifs après rotation de la caméra
        # Pour une caméra inclinée vers le bas (pitch négatif), l'angle de vue vers le haut est réduit
        pitch_deg = np.degrees(self.camera_pitch)
        yaw_deg = np.degrees(self.camera_yaw)
        roll_deg = np.degrees(self.camera_roll)

        return {
            "focal_length_px": fx,
            "image_dimensions": (int(image_width), int(image_height)),
            "fov_horizontal_deg": fov_horizontal_deg,
            "fov_vertical_deg": fov_vertical_deg,
            "fov_diagonal_deg": fov_diagonal_deg,
            "camera_orientation": {"pitch_deg": pitch_deg, "yaw_deg": yaw_deg, "roll_deg": roll_deg},
            "camera_height_m": self.camera_position[2],
        }

    def print_field_of_view_debug(self) -> None:
        """Affiche les informations de debug sur l'angle de vue de la caméra"""
        fov_info = self.calculate_field_of_view()

        print("\n" + "=" * 60)
        print("🎥 DEBUG - ANGLE DE VUE DE LA CAMÉRA")
        print("=" * 60)
        print(f"📐 Focale                    : {fov_info['focal_length_px']:.1f} pixels")
        print(f"📏 Dimensions image          : {fov_info['image_dimensions'][0]} x {fov_info['image_dimensions'][1]} pixels")
        print()
        print("🔍 Angles de champ de vision (théoriques) :")
        print(f"   ├─ Horizontal             : {fov_info['fov_horizontal_deg']:.1f}°")
        print(f"   ├─ Vertical               : {fov_info['fov_vertical_deg']:.1f}°")
        print(f"   └─ Diagonal               : {fov_info['fov_diagonal_deg']:.1f}°")
        print()
        print("🎯 Orientation de la caméra :")
        print(f"   ├─ Pitch (inclinaison)    : {fov_info['camera_orientation']['pitch_deg']:.1f}° ({'vers le bas' if fov_info['camera_orientation']['pitch_deg'] > 0 else 'vers le haut'})")
        print(f"   ├─ Yaw (rotation H)       : {fov_info['camera_orientation']['yaw_deg']:.1f}°")
        print(f"   ├─ Roll (inclinaison lat) : {fov_info['camera_orientation']['roll_deg']:.1f}°")
        print(f"   └─ Hauteur                : {fov_info['camera_height_m']:.2f} m")
        print()

        # Calculer la portée théorique
        if fov_info["camera_orientation"]["pitch_deg"] > 0:  # Caméra inclinée vers le bas
            # Distance maximale visible au sol
            half_fov_v = np.radians(fov_info["fov_vertical_deg"] / 2)
            pitch_rad = np.radians(fov_info["camera_orientation"]["pitch_deg"])

            # Angle du rayon le plus bas par rapport à l'horizontale
            angle_bottom_ray = pitch_rad + half_fov_v

            # Distance maximale visible (géométrie simple)
            if angle_bottom_ray < np.pi / 2:  # Si le rayon pointe vers le bas
                max_distance = fov_info["camera_height_m"] / np.tan(angle_bottom_ray)
                print(f"📏 Portée théorique au sol   : {max_distance:.1f} m")

            # Largeur visible à différentes distances
            half_fov_h = np.radians(fov_info["fov_horizontal_deg"] / 2)
            for dist in [5, 10, 20, 30]:
                width_at_distance = 2 * dist * np.tan(half_fov_h)
                print(f"   ├─ Largeur à {dist:2d}m        : {width_at_distance:.1f} m")

        print("=" * 60)

    def generate_all_visualizations(self, base_name: str = "gopro_3d_analysis"):
        """Génère toutes les visualisations et les sauvegarde"""
        print("🎨 Génération de toutes les visualisations...")

        # 1. Cartes de coordonnées
        print("📊 Création des cartes de coordonnées...")
        coord_maps = self.create_coordinate_maps(f"{base_name}_coordinate_maps.png")

        # 2. Graphique 3D
        print("🌍 Création du graphique 3D...")
        self.create_3d_surface_plot(subsample=5, save_path=f"{base_name}_3d_surface.png")

        # 3. Coupes transversales
        print("📏 Création des coupes transversales...")
        self.create_cross_sections(f"{base_name}_cross_sections.png")

        # 4. Visualisation depth classique
        print("🗺️ Création de la depth map...")
        depth_vis = self.visualize_depth_map(max_distance=20.0)
        cv2.imwrite(f"{base_name}_depth_map.png", depth_vis)

        print(f"✅ Toutes les visualisations sauvegardées avec le préfixe '{base_name}'")

        return coord_maps


# Exemple d'utilisation avec les paramètres corrigés
def example_usage():
    """Exemple d'utilisation avec les paramètres GoPro Hero 13 Linear 90°"""

    print("=== Calibration GoPro Hero 13 Linear 90° ===")

    # Crée une calibration pour la caméra
    calibration: Calibration = get_calibration_from_focal(1920, 1080, 1000.0)

    # Prépare le modèle de route plane
    road_model = PlaneRoadModel(
        camera_calibration=calibration,
        camera_pitch=33.0,  # looking downwards for road crack inspection
        camera_yaw=0.0,  # Pas de rotation horizontale
        camera_roll=0.0,  # Pas de rotation de roulis
        camera_height=1.1,  # 1 mètre au-dessus du sol
    )

    # Exemple avec une image factice pour les tests
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)

    # Calculer les points 3D
    points3d: np.ndarray = road_model.get_points3D(test_image)

    print(f"\nShape des points 3D: {points3d.shape}")

    # Afficher les informations de debug sur l'angle de vue
    road_model.print_field_of_view_debug()

    # Afficher les statistiques détaillées de la scène
    road_model.print_scene_statistics()

    # Sauvegarder les points 3D
    road_model.save_points3D_as_npz("src/annot/structures/endpoints/dummy_points3d.npz")

    # Générer toutes les visualisations
    print("\n" + "=" * 60)
    print("GÉNÉRATION DES VISUALISATIONS")
    print("=" * 60)
    coord_maps = road_model.generate_all_visualizations("hero13_linear_analysis")

    return points3d


# Use in production
def compute_points3d(
    image: cv2.typing.MatLike,
    camera_matrix: np.ndarray,
    dist_coeffs: np.ndarray,
    camera_pitch: float,
    camera_yaw: float,
    camera_roll: float,
    camera_height: float,
):
    """
    Fonction de calcul des points 3D à partir d'une matrice de caméra.

    Args:
        image (cv2.typing.MatLike): Image source pour laquelle les points 3D sont calculés. Formats supportés par OpenCV.
        camera_matrix (np.ndarray): Matrice de caméra 3x3.
        dist_coeffs (np.ndarray): Coefficients de distorsion de la caméra.
        camera_pitch (float): Angle de pitch de la caméra en degrés.
        camera_yaw (float): Angle de yaw de la caméra en degrés.
        camera_roll (float): Angle de roll de la caméra en degrés.
        camera_height (float): Hauteur de la caméra au-dessus du sol en mètres.

    Returns:
        np.ndarray: les points 3D de l'image.
    """
    # Créer une calibration à partir de la matrice de caméra
    calibration = Calibration(camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)

    # Retourner le modèle de route plane
    model = PlaneRoadModel(
        camera_calibration=calibration,
        camera_pitch=camera_pitch,
        camera_yaw=camera_yaw,
        camera_roll=camera_roll,
        camera_height=camera_height,
    )
    # Create the points 3D from the model
    points3d = model.get_points3D(image)

    return points3d


if __name__ == "__main__":
    points = example_usage()
