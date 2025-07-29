"""
# Projection des masques sur la route

Transforme les masques binaires en représentation polygonale sur la route dans un système de coordonnées UTM.

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

from typing import List, Optional, Tuple, Union

import numpy as np
import utm
from shapely.geometry import MultiPoint, Point, Polygon, LineString, MultiPolygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union, polygonize

from lcvtoolbox.core.schemas import (
    GPSCoordinates,
    MaskProjectionParams,
    UTMPolygonResult,
    UTMReference,
)


class ProjectMask:
    """
    ProjectMask handles the projection of a binary mask as polygons onto a road points in 3D space.

    This class provides functionality to:
    - Project 2D binary masks onto 3D road points
    - Convert projected points to polygon representations
    - Transform polygons to UTM (Universal Transverse Mercator) coordinates

    Attributes:
        points3d (np.ndarray): 3D coordinates array with shape (H, W, 3) where each pixel 
                              contains (X, Y, Z) coordinates in the vehicle frame.
        gps_coordinates (Dict): GPS reference containing 'latitude', 'longitude', and 
                               optionally 'heading' (in degrees).

    Coordinate Systems:
        1. Image Frame: 2D pixel coordinates (u, v) with origin at top-left
        2. Vehicle Frame: 3D coordinates (X, Y, Z) with X forward, Y left, Z up
        3. UTM Frame: Projected geographic coordinates (easting, northing)

    Example:
        >>> # Create a ProjectMask instance
        >>> points3d = np.random.randn(480, 640, 3)  # Example 3D points
        >>> gps_coords = {'latitude': 48.8566, 'longitude': 2.3522, 'heading': 45.0}
        >>> projector = ProjectMask(points3d, gps_coords)
        
        >>> # Project a binary mask to UTM polygon
        >>> mask = np.zeros((480, 640), dtype=np.uint8)
        >>> mask[100:200, 150:250] = 1  # Example rectangular mask
        >>> utm_polygon = projector.mask_to_polygon_in_utm(mask)
    """

    def __init__(self, points3d: np.ndarray, gps_coordinates: Union[GPSCoordinates, dict]):
        """
        Initialize the ProjectMask instance.

        Args:
            points3d (np.ndarray): Array of shape (H, W, 3) containing 3D coordinates
                                  for each pixel in the vehicle frame.
            gps_coordinates (Union[GPSCoordinates, dict]): GPS reference as a Pydantic model
                                                          or dict with 'latitude', 'longitude', 
                                                          and optional 'heading'.

        Raises:
            ValueError: If points3d doesn't have shape (H, W, 3).
        """
        if points3d.ndim != 3 or points3d.shape[2] != 3:
            raise ValueError(f"points3d must have shape (H, W, 3), got {points3d.shape}")
        
        # Convert dict to GPSCoordinates if needed
        if isinstance(gps_coordinates, dict):
            self.gps_coordinates = GPSCoordinates(**gps_coordinates)
        else:
            self.gps_coordinates = gps_coordinates
        
        self.points3d = points3d
        
        # Pre-compute UTM reference for efficiency
        utm_x, utm_y, zone_number, zone_letter = utm.from_latlon(
            self.gps_coordinates.latitude, 
            self.gps_coordinates.longitude
        )
        self.utm_reference = UTMReference(
            easting=utm_x,
            northing=utm_y,
            zone_number=zone_number,
            zone_letter=str(zone_letter) if zone_letter is not None else 'N'
        )

    def mask_to_polygon_in_utm(self, mask: np.ndarray, 
                              params: Optional[MaskProjectionParams] = None) -> Optional[UTMPolygonResult]:
        """
        Transforms a binary mask to a polygon representation in UTM coordinates.

        This is the main method that orchestrates the full pipeline:
        1. Projects mask pixels to 3D vehicle frame coordinates
        2. Removes height information (projects to ground plane)
        3. Converts projected points to polygon
        4. Transforms polygon to UTM coordinates

        Args:
            mask (np.ndarray): Binary mask of shape (H, W) with values 0 or 1.
                              Must have the same spatial dimensions as points3d.
            params (Optional[MaskProjectionParams]): Projection parameters. If None,
                                                   default parameters are used.

        Returns:
            Optional[UTMPolygonResult]: Result containing polygon and UTM zone info,
                                      or None if no valid polygon could be created.

        Raises:
            ValueError: If mask shape doesn't match points3d spatial dimensions.

        Example:
            >>> mask = np.zeros((480, 640), dtype=np.uint8)
            >>> mask[200:300, 250:350] = 1  # 100x100 pixel region
            >>> result = projector.mask_to_polygon_in_utm(mask)
            >>> if result:
            ...     print(f"Polygon area: {result.polygon.area:.2f} m²")
            ...     print(f"UTM Zone: {result.zone_number}{result.zone_letter}")
        """
        # Use default params if not provided
        if params is None:
            params = MaskProjectionParams()
        
        # Validate mask dimensions
        if mask.shape[:2] != self.points3d.shape[:2]:
            raise ValueError(f"Mask shape {mask.shape} doesn't match points3d shape {self.points3d.shape[:2]}")
        
        # Step 1: Project mask to vehicle frame
        projected_points = self.project_mask_to_moving_frame(mask, self.points3d)
        
        if len(projected_points) == 0:
            return None
        
        # Step 2: Remove height (project to ground plane)
        ground_points = self.remove_height_from_projected_mask(projected_points)
        
        # Step 3: Convert to polygon
        polygon = self.transform_projected_mask_to_polygon(
            ground_points, 
            simplify_tolerance=params.simplify_tolerance,
            min_area=params.min_area,
            alpha=params.alpha,
            use_convex_hull=params.use_convex_hull
        )
        
        if polygon is None:
            return None
        
        # Step 4: Transform to UTM coordinates
        utm_polygon, zone_number, zone_letter = self.project_polygon_to_utm_coordinates(
            self.gps_coordinates, 
            polygon,
            self.utm_reference
        )
        
        return UTMPolygonResult(
            polygon=utm_polygon,
            zone_number=zone_number,
            zone_letter=zone_letter
        )

    @staticmethod
    def project_mask_to_moving_frame(mask: np.ndarray, points3d: np.ndarray) -> np.ndarray:
        """
        Projects binary mask pixels onto 3D road points in the vehicle frame.

        This method extracts the 3D coordinates corresponding to pixels where the mask
        value is non-zero (typically 1 for binary masks).

        Args:
            mask (np.ndarray): Binary mask of shape (H, W) with non-zero values
                              indicating regions of interest.
            points3d (np.ndarray): 3D coordinates array of shape (H, W, 3) containing
                                  (X, Y, Z) coordinates for each pixel.

        Returns:
            np.ndarray: Array of shape (N, 3) containing 3D coordinates of masked pixels,
                       where N is the number of non-zero pixels in the mask.

        Example:
            >>> mask = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
            >>> points3d = np.random.randn(3, 3, 3)
            >>> projected = ProjectMask.project_mask_to_moving_frame(mask, points3d)
            >>> print(f"Projected {len(projected)} points")
        """
        # Get indices where mask is non-zero
        mask_indices = np.where(mask > 0)
        
        # Extract 3D points at these indices
        projected_points = points3d[mask_indices]
        
        return projected_points

    @staticmethod
    def remove_height_from_projected_mask(points: np.ndarray) -> np.ndarray:
        """
        Projects 3D points onto the ground plane by setting Z coordinate to zero.

        This is necessary for creating 2D polygons on the road surface.

        Args:
            points (np.ndarray): Array of shape (N, 3) containing 3D points.

        Returns:
            np.ndarray: Array of shape (N, 2) containing 2D points on the ground plane.

        Example:
            >>> points_3d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            >>> points_2d = ProjectMask.remove_height_from_projected_mask(points_3d)
            >>> print(points_2d)  # [[1, 2], [4, 5], [7, 8]]
        """
        # Keep only X and Y coordinates (drop Z)
        return points[:, :2]

    @staticmethod
    def transform_projected_mask_to_polygon(projected_points: np.ndarray,
                                          simplify_tolerance: float = 0.5,
                                          min_area: float = 1.0,
                                          alpha: float = 2.0,
                                          use_convex_hull: bool = False) -> Optional[Polygon]:
        """
        Transforms a set of 2D points into a polygon representation.

        This method creates a polygon that can handle complex shapes including:
        - L-shaped regions
        - U-shaped regions
        - Both convex and concave forms

        It uses an alpha shape algorithm by default for concave hulls, but can fall
        back to convex hull when needed.

        Args:
            projected_points (np.ndarray): Array of shape (N, 2) containing 2D points
                                         in the vehicle frame (X, Y coordinates).
            simplify_tolerance (float): Tolerance for polygon simplification in meters.
                                      Default: 0.5m.
            min_area (float): Minimum polygon area in square meters. Default: 1.0 m².
            alpha (float): Alpha parameter for concave hull. Smaller values create
                          tighter fits around points. Default: 2.0.
            use_convex_hull (bool): If True, uses convex hull instead of alpha shape.
                                   Default: False.

        Returns:
            Optional[Polygon]: Shapely Polygon object or None if no valid polygon
                              could be created. Supports both convex and concave shapes.

        Example:
            >>> # L-shaped points
            >>> points = np.array([[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2]])
            >>> polygon = ProjectMask.transform_projected_mask_to_polygon(points)
            >>> if polygon:
            ...     print(f"Created L-shaped polygon with area: {polygon.area:.2f}")
        """
        if len(projected_points) < 3:
            # Need at least 3 points to form a polygon
            return None
        
        try:
            # Create MultiPoint object from points
            multi_point = MultiPoint(projected_points)
            
            if use_convex_hull:
                # Use convex hull for simple cases
                polygon = multi_point.convex_hull
            else:
                # Create alpha shape (concave hull) for complex shapes
                polygon = ProjectMask._create_alpha_shape(projected_points, alpha)
                
                # If alpha shape fails, fall back to convex hull
                if polygon is None or not isinstance(polygon, Polygon):
                    polygon = multi_point.convex_hull
            
            # Ensure we have a polygon (not a point or line)
            if not isinstance(polygon, Polygon):
                return None
            
            # Simplify polygon to reduce vertices
            if simplify_tolerance > 0:
                simplified = polygon.simplify(simplify_tolerance, preserve_topology=True)
                # Ensure the simplified result is still a polygon
                if isinstance(simplified, Polygon):
                    polygon = simplified
            
            # Filter by minimum area
            if polygon.area < min_area:
                return None
            
            return polygon
            
        except Exception:
            # If any error occurs, try to return at least a convex hull
            try:
                hull = MultiPoint(projected_points).convex_hull
                if isinstance(hull, Polygon) and hull.area >= min_area:
                    return hull
            except:
                pass
            return None
    
    @staticmethod
    def _create_alpha_shape(points: np.ndarray, alpha: float) -> Optional[Polygon]:
        """
        Creates an alpha shape (concave hull) from a set of points.
        
        This method creates a concave hull that can wrap tightly around complex
        shapes like L-shapes, U-shapes, etc.
        
        Args:
            points (np.ndarray): Array of shape (N, 2) containing 2D points.
            alpha (float): Alpha parameter. Smaller values create tighter fits.
        
        Returns:
            Optional[Polygon]: The alpha shape polygon or None if creation failed.
        """
        try:
            # Create a buffer around each point and union them
            point_buffers = []
            buffer_radius = alpha
            
            for point in points:
                p = Point(point)
                point_buffers.append(p.buffer(buffer_radius))
            
            # Union all buffers
            union = unary_union(point_buffers)
            
            # Erode back to get the alpha shape
            if hasattr(union, 'buffer'):
                alpha_shape = union.buffer(-buffer_radius * 0.95)
                
                # Extract the largest polygon if multiple polygons exist
                if isinstance(alpha_shape, MultiPolygon):
                    # MultiPolygon case - get the largest one
                    largest = max(alpha_shape.geoms, key=lambda p: p.area)
                    return largest if isinstance(largest, Polygon) else None
                elif isinstance(alpha_shape, Polygon):
                    return alpha_shape
            
            return None
            
        except Exception:
            return None

    @staticmethod
    def project_polygon_to_utm_coordinates(gps_coordinates: GPSCoordinates, 
                                         polygon: Polygon,
                                         utm_reference: Optional[UTMReference] = None) -> Tuple[Polygon, int, str]:
        """
        Projects a polygon from vehicle frame to UTM coordinates.

        This method transforms a polygon defined in the vehicle's local coordinate
        system to the global UTM coordinate system using GPS reference.

        Args:
            gps_coordinates (GPSCoordinates): GPS reference with latitude, longitude,
                                             and optional heading.
            polygon (Polygon): Shapely Polygon in vehicle frame coordinates (meters).
            utm_reference (Optional[UTMReference]): Pre-computed UTM reference for efficiency.

        Returns:
            Tuple[Polygon, int, str]: A tuple containing:
                - Transformed polygon in UTM coordinates
                - Zone number (int)
                - Zone letter (str)

        Example:
            >>> gps = GPSCoordinates(latitude=48.8566, longitude=2.3522, heading=90.0)
            >>> vehicle_polygon = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
            >>> utm_polygon, zone_num, zone_letter = ProjectMask.project_polygon_to_utm_coordinates(gps, vehicle_polygon)
            >>> print(f"UTM bounds: {utm_polygon.bounds}")
            >>> print(f"UTM Zone: {zone_num}{zone_letter}")
        """
        # Get UTM reference point
        if utm_reference is None:
            utm_x, utm_y, zone_number, zone_letter = utm.from_latlon(
                gps_coordinates.latitude,
                gps_coordinates.longitude
            )
        else:
            utm_x = utm_reference.easting
            utm_y = utm_reference.northing
            zone_number = utm_reference.zone_number
            zone_letter = utm_reference.zone_letter
        
        # Get vehicle heading (default to 0° North if not provided)
        heading = gps_coordinates.heading if gps_coordinates.heading is not None else 0.0
        heading_rad = np.radians(heading)
        
        # Create rotation matrix for heading
        cos_h = np.cos(heading_rad)
        sin_h = np.sin(heading_rad)
        
        # Transform polygon coordinates
        coords = np.array(polygon.exterior.coords)
        transformed_coords = []
        
        for x_vehicle, y_vehicle in coords:
            # Apply rotation based on heading
            # In vehicle frame: X=forward, Y=left
            # In UTM/geographic: North=0°, East=90°
            x_rotated = x_vehicle * cos_h - y_vehicle * sin_h
            y_rotated = x_vehicle * sin_h + y_vehicle * cos_h
            
            # Translate to UTM coordinates
            utm_x_point = utm_x + x_rotated
            utm_y_point = utm_y + y_rotated
            
            transformed_coords.append((utm_x_point, utm_y_point))
        
        # Create new polygon in UTM coordinates
        utm_polygon = Polygon(transformed_coords)
        
        # Ensure zone_letter is a string (handle edge cases where it might be None)
        zone_letter_str = str(zone_letter) if zone_letter is not None else ''
        
        return utm_polygon, int(zone_number), zone_letter_str
