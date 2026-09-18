import cv2
import numpy as np
import random
import math

def apply_dog_filter(frame, face_rect):
    x, y, w, h = face_rect
    # Dog Nose
    nose_x = x + w // 2
    nose_y = y + int(h * 0.6)
    cv2.ellipse(frame, (nose_x, nose_y), (int(w*0.1), int(h*0.07)), 0, 0, 360, (0, 0, 0), -1)
    
    # Dog Tongue
    tongue_x = nose_x
    tongue_y = nose_y + int(h * 0.15)
    cv2.ellipse(frame, (tongue_x, tongue_y), (int(w*0.12), int(h*0.18)), 0, 0, 180, (50, 50, 255), -1)
    cv2.line(frame, (tongue_x, nose_y + int(h * 0.15)), (tongue_x, tongue_y + int(h*0.15)), (0, 0, 150), 2)
    
    # Dog Ears
    ear_w = int(w * 0.3)
    ear_h = int(h * 0.4)
    # Left ear
    pts_left = np.array([[x - ear_w//2, y], [x + ear_w//2, y - ear_h], [x + ear_w, y + ear_h//3]], np.int32)
    cv2.fillPoly(frame, [pts_left], (100, 150, 200))
    # Right ear
    pts_right = np.array([[x + w + ear_w//2, y], [x + w - ear_w//2, y - ear_h], [x + w - ear_w, y + ear_h//3]], np.int32)
    cv2.fillPoly(frame, [pts_right], (100, 150, 200))
    
    # Whiskers
    whisker_len = int(w * 0.3)
    cv2.line(frame, (x + int(w*0.2), nose_y), (x - int(w*0.1), nose_y - int(h*0.05)), (0, 0, 0), 2)
    cv2.line(frame, (x + int(w*0.2), nose_y + int(h*0.05)), (x - int(w*0.1), nose_y + int(h*0.1)), (0, 0, 0), 2)
    cv2.line(frame, (x + int(w*0.8), nose_y), (x + w + int(w*0.1), nose_y - int(h*0.05)), (0, 0, 0), 2)
    cv2.line(frame, (x + int(w*0.8), nose_y + int(h*0.05)), (x + w + int(w*0.1), nose_y + int(h*0.1)), (0, 0, 0), 2)
    return frame

def apply_sunglasses_filter(frame, face_rect):
    x, y, w, h = face_rect
    eye_y = y + int(h * 0.35)
    glass_w = int(w * 0.4)
    glass_h = int(h * 0.25)
    
    # Left lens
    lx = x + int(w * 0.1)
    cv2.rectangle(frame, (lx, eye_y), (lx + glass_w, eye_y + glass_h), (20, 20, 20), -1)
    # Right lens
    rx = x + int(w * 0.5)
    cv2.rectangle(frame, (rx, eye_y), (rx + glass_w, eye_y + glass_h), (20, 20, 20), -1)
    # Bridge
    cv2.line(frame, (lx + glass_w, eye_y + glass_h//3), (rx, eye_y + glass_h//3), (20, 20, 20), 4)
    return frame

def apply_crown_filter(frame, face_rect):
    x, y, w, h = face_rect
    crown_w = int(w * 1.2)
    crown_h = int(h * 0.5)
    cx = x - int(w * 0.1)
    cy = y - int(h * 0.3)
    
    pts = np.array([
        [cx, cy], # Bottom left
        [cx + crown_w, cy], # Bottom right
        [cx + crown_w, cy - crown_h], # Top right point
        [cx + int(crown_w * 0.75), cy - int(crown_h * 0.4)], # Right valley
        [cx + int(crown_w * 0.5), cy - crown_h - int(h*0.1)], # Center point
        [cx + int(crown_w * 0.25), cy - int(crown_h * 0.4)], # Left valley
        [cx, cy - crown_h] # Top left point
    ], np.int32)
    
    # Draw gold crown
    cv2.fillPoly(frame, [pts], (0, 215, 255))
    # Add some jewels
    cv2.circle(frame, (cx + int(crown_w * 0.5), cy - crown_h - int(h*0.1)), int(w*0.05), (0, 0, 255), -1)
    cv2.circle(frame, (cx + crown_w, cy - crown_h), int(w*0.04), (255, 0, 0), -1)
    cv2.circle(frame, (cx, cy - crown_h), int(w*0.04), (255, 0, 0), -1)
    return frame

def apply_rainbow_filter(frame, face_rect):
    x, y, w, h = face_rect
    center = (x + w//2, y - int(h*0.1))
    colors = [(0, 0, 255), (0, 127, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0), (130, 0, 75), (211, 0, 148)]
    thickness = max(2, int(w * 0.05))
    
    for i, color in enumerate(colors):
        axes = (int(w*0.8) - i*thickness, int(h*0.5) - i*thickness)
        if axes[0] > 0 and axes[1] > 0:
            cv2.ellipse(frame, center, axes, 0, 180, 360, color, thickness)
    return frame

def apply_neon_filter(frame, face_rect):
    x, y, w, h = face_rect
    # Expand ROI slightly
    pad = int(w * 0.2)
    x1, y1 = max(0, x - pad), max(0, y - pad)
    x2, y2 = min(frame.shape[1], x + w + pad), min(frame.shape[0], y + h + pad)
    
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0: return frame
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    
    # Create colored neon glow (cyan)
    neon = np.zeros_like(roi)
    neon[edges > 0] = [255, 255, 0] # Cyan in BGR
    
    # Blend
    cv2.addWeighted(neon, 0.8, roi, 1.0, 0, roi)
    frame[y1:y2, x1:x2] = roi
    return frame

def apply_vintage_filter(frame, face_rect):
    # Apply to whole frame for better effect, but can be localized
    # Creating a sepia effect
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(frame, kernel)
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    
    # Add noise
    noise = np.random.normal(0, 15, sepia.shape).astype(np.uint8)
    sepia = cv2.add(sepia, noise)
    
    # Vignette
    rows, cols = frame.shape[:2]
    X_resultant_kernel = cv2.getGaussianKernel(cols, cols/2)
    Y_resultant_kernel = cv2.getGaussianKernel(rows, rows/2)
    kernel_v = Y_resultant_kernel * X_resultant_kernel.T
    mask = 255 * kernel_v / np.linalg.norm(kernel_v)
    
    vignette = np.copy(sepia)
    for i in range(3):
        vignette[:,:,i] = vignette[:,:,i] * mask
    
    return vignette

def apply_cyberpunk_filter(frame, face_rect):
    x, y, w, h = face_rect
    # Tint entire frame slightly cyan/magenta
    tint = np.full_like(frame, (255, 0, 255), dtype=np.uint8) # Magenta
    blended = cv2.addWeighted(frame, 0.7, tint, 0.3, 0)
    
    # Add scanlines
    for i in range(0, blended.shape[0], 4):
        blended[i, :] = blended[i, :] * 0.5
        
    # Add HUD around face
    pad = int(w * 0.1)
    x1, y1 = max(0, x - pad), max(0, y - pad)
    x2, y2 = min(blended.shape[1], x + w + pad), min(blended.shape[0], y + h + pad)
    
    color = (255, 255, 0) # Cyan
    t = 2 # thickness
    l = int(w * 0.2) # line length
    
    # Top-left
    cv2.line(blended, (x1, y1), (x1 + l, y1), color, t)
    cv2.line(blended, (x1, y1), (x1, y1 + l), color, t)
    # Top-right
    cv2.line(blended, (x2, y1), (x2 - l, y1), color, t)
    cv2.line(blended, (x2, y1), (x2, y1 + l), color, t)
    # Bottom-left
    cv2.line(blended, (x1, y2), (x1 + l, y2), color, t)
    cv2.line(blended, (x1, y2), (x1, y2 - l), color, t)
    # Bottom-right
    cv2.line(blended, (x2, y2), (x2 - l, y2), color, t)
    cv2.line(blended, (x2, y2), (x2, y2 - l), color, t)
    
    # Add some text
    cv2.putText(blended, "TARGET ACQUIRED", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return blended

def apply_sketch_filter(frame, face_rect):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

def apply_pixelate_filter(frame, face_rect):
    x, y, w, h = face_rect
    # Expand slightly
    pad = int(w * 0.1)
    x1, y1 = max(0, x - pad), max(0, y - pad)
    x2, y2 = min(frame.shape[1], x + w + pad), min(frame.shape[0], y + h + pad)
    
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0: return frame
    
    # Resize down
    small = cv2.resize(roi, (16, 16), interpolation=cv2.INTER_LINEAR)
    # Resize back up with nearest neighbor
    pixelated = cv2.resize(small, (x2 - x1, y2 - y1), interpolation=cv2.INTER_NEAREST)
    
    frame[y1:y2, x1:x2] = pixelated
    return frame

def apply_mirror_filter(frame, face_rect):
    h, w = frame.shape[:2]
    half_w = w // 2
    left_half = frame[:, :half_w].copy()
    right_half = cv2.flip(left_half, 1)
    
    mirror = np.zeros_like(frame)
    mirror[:, :half_w] = left_half
    mirror[:, half_w:] = right_half
    return mirror

FILTERS = {
    'dog': apply_dog_filter,
    'sunglasses': apply_sunglasses_filter,
    'crown': apply_crown_filter,
    'rainbow': apply_rainbow_filter,
    'neon': apply_neon_filter,
    'vintage': apply_vintage_filter,
    'cyberpunk': apply_cyberpunk_filter,
    'sketch': apply_sketch_filter,
    'pixelate': apply_pixelate_filter,
    'mirror': apply_mirror_filter
}
