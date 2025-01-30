import cv2
import numpy as np
from skimage import measure
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter

class FiberImageProcessor:
    def __init__(self, image):
        self.original = image
        self.processed = None
        self._init_processing()
        
    def _init_processing(self):
        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        self.processed = cv2.medianBlur(gray, 11)
        
    def detect_core_cladding(self):
        # aadaptive thresholding
        thresh = cv2.adaptiveThreshold(
            self.processed, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # region analysis
        labels = measure.label(cleaned)
        regions = measure.regionprops(labels)
        
        # select relevant regions
        valid_regions = sorted(
            [r for r in regions if r.area > 100],
            key=lambda x: x.area, 
            reverse=True
        )[:2]
        
        return {
            'core': self._region_stats(valid_regions[0]),
            'cladding': self._region_stats(valid_regions[1])
        }
    
    def _region_stats(self, region):
        return {
            'diameter': 2 * region.equivalent_diameter,
            'centroid': region.centroid,
            'orientation': region.orientation
        }
    
    def refractive_index_profile(self):
        line_scan = self.processed[self.processed.shape[0]//2, :]
        x = np.arange(len(line_scan))
        
        def n_profile(r, n_core, n_clad, r_core, alpha):
            return n_clad + (n_core - n_clad) * np.exp(-(r/r_core)**alpha)
            
        params, _ = curve_fit(
            n_profile, x, line_scan/np.max(line_scan),
            p0=[1.46, 1.44, 50, 2]
        )
        return params