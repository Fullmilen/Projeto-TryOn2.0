import cv2
import numpy as np

# ==========================================================
# VARIÁVEIS GLOBAIS PARA SUAVIZAÇÃO
# ==========================================================

prev_x = None
prev_y = None
prev_w = None
prev_h = None


# ==========================================================
# ROTACIONAR ROUPA
# ==========================================================

def rotate_image(image, angle):
    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    rotated = cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )

    return rotated


# ==========================================================
# OVERLAY COM TRANSPARÊNCIA E SUAVIZAÇÃO
# ==========================================================

def overlay_clothing(frame, clothing_img, x, y, w, h):
    global prev_x, prev_y, prev_w, prev_h

    frame_h, frame_w, _ = frame.shape

    # ------------------------------
    # Suavização para reduzir tremedeira
    # ------------------------------
    alpha = 0.78

    if prev_x is None:
        prev_x = x
        prev_y = y
        prev_w = w
        prev_h = h
    else:
        x = int(alpha * prev_x + (1 - alpha) * x)
        y = int(alpha * prev_y + (1 - alpha) * y)
        w = int(alpha * prev_w + (1 - alpha) * w)
        h = int(alpha * prev_h + (1 - alpha) * h)

    prev_x = x
    prev_y = y
    prev_w = w
    prev_h = h

    # ------------------------------
    # Limites da tela
    # ------------------------------
    if x < 0:
        x = 0
    if y < 0:
        y = 0

    if x + w > frame_w:
        w = frame_w - x

    if y + h > frame_h:
        h = frame_h - y

    if w <= 0 or h <= 0:
        return frame

    # ------------------------------
    # Redimensionar roupa
    # ------------------------------
    clothing_resized = cv2.resize(
        clothing_img,
        (w, h),
        interpolation=cv2.INTER_LINEAR
    )

    if clothing_resized is None:
        return frame

    if len(clothing_resized.shape) < 3 or clothing_resized.shape[2] < 4:
        return frame

    overlay_rgb = clothing_resized[:, :, :3].astype(float)
    alpha_mask = clothing_resized[:, :, 3].astype(float) / 255.0
    alpha_mask_3 = np.dstack([alpha_mask, alpha_mask, alpha_mask])

    roi = frame[y:y + h, x:x + w].astype(float)

    if roi.shape[:2] != overlay_rgb.shape[:2]:
        return frame

    blended = (overlay_rgb * alpha_mask_3) + (roi * (1 - alpha_mask_3))

    frame[y:y + h, x:x + w] = blended.astype(np.uint8)

    return frame