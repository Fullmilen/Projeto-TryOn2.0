import cv2
import os

from engine.body_tracking import detect_pose, draw_pose
from engine.measurements import calculate_measurements
from engine.size_recommendation import recommend_size
from engine.clothing_overlay import overlay_clothing, rotate_image

# ==========================================================
# ENTRADA DA ALTURA REAL
# ==========================================================

# Pedimos a altura real da pessoa para calcular a escala corretamente.
altura_real_cm = float(input("Digite a altura da pessoa em cm (ex: 180): "))

# ==========================================================
# CARREGAR IMAGEM DA ROUPA
# ==========================================================

base_path = os.path.dirname(__file__)
image_path = os.path.join(base_path, "assets", "bermuda.png")

clothing = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

if clothing is None:
    print("ERRO: imagem da bermuda não foi carregada")
else:
    print("Imagem carregada com sucesso")

# ==========================================================
# ABRIR CÂMERA
# ==========================================================

cap = cv2.VideoCapture(0)

# ==========================================================
# VARIÁVEIS DE SUAVIZAÇÃO
# ==========================================================

prev_shoulder_cm = None
prev_hip_circumference_cm = None
prev_waist_circumference_cm = None
prev_height_cm = None

prev_clothing_width = None
prev_clothing_height = None
prev_x_pos = None
prev_y_pos = None

alpha = 0.80

# ==========================================================
# FUNÇÃO DE SUAVIZAÇÃO
# ==========================================================

def smooth_value(current, previous, alpha=0.85, limit=3):
    """
    Suaviza valores e limita a variação máxima por frame.
    Isso evita números "pulando" na tela.
    """
    if previous is None:
        return current

    smoothed = alpha * previous + (1 - alpha) * current

    if abs(smoothed - previous) > limit:
        smoothed = previous + limit if smoothed > previous else previous - limit

    return smoothed

# ==========================================================
# LOOP PRINCIPAL
# ==========================================================

while True:
    ret, frame = cap.read()

    if not ret:
        break

    height, width, _ = frame.shape

    # Detecta a pose
    results = detect_pose(frame)

    # Desenha o esqueleto
    frame = draw_pose(frame, results)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # --------------------------------------------------
        # MEDIDAS BASEADAS NA ALTURA REAL INFORMADA
        # --------------------------------------------------
        measures = calculate_measurements(
            landmarks,
            width,
            height,
            altura_real_cm
        )

        shoulder_cm = measures["shoulder_cm"]
        hip_width_cm = measures["hip_width_cm"]
        hip_circumference_cm = measures["hip_circumference_cm"]
        waist_circumference_cm = measures["waist_circumference_cm"]
        height_cm = measures["height_cm"]

        # --------------------------------------------------
        # SUAVIZAÇÃO DAS MEDIDAS
        # --------------------------------------------------
        if prev_shoulder_cm is None:
            prev_shoulder_cm = shoulder_cm
            prev_hip_circumference_cm = hip_circumference_cm
            prev_waist_circumference_cm = waist_circumference_cm
            prev_height_cm = height_cm
        else:
            shoulder_cm = smooth_value(shoulder_cm, prev_shoulder_cm, 0.88, 1.5)
            hip_circumference_cm = smooth_value(hip_circumference_cm, prev_hip_circumference_cm, 0.88, 2.0)
            waist_circumference_cm = smooth_value(waist_circumference_cm, prev_waist_circumference_cm, 0.88, 2.0)
            height_cm = smooth_value(height_cm, prev_height_cm, 0.92, 1.0)

            prev_shoulder_cm = shoulder_cm
            prev_hip_circumference_cm = hip_circumference_cm
            prev_waist_circumference_cm = waist_circumference_cm
            prev_height_cm = height_cm

        # --------------------------------------------------
        # TAMANHO RECOMENDADO
        # --------------------------------------------------
        recommended_size = recommend_size(
            waist_circumference_cm,
            hip_circumference_cm
        )

        # --------------------------------------------------
        # LANDMARKS IMPORTANTES
        # --------------------------------------------------
        hip_left = landmarks[23]
        hip_right = landmarks[24]
        knee_left = landmarks[25]
        knee_right = landmarks[26]

        if (
            hip_left.visibility > 0.5 and
            hip_right.visibility > 0.5 and
            knee_left.visibility > 0.5 and
            knee_right.visibility > 0.5
        ):
            hip_left_x = int(hip_left.x * width)
            hip_left_y = int(hip_left.y * height)

            hip_right_x = int(hip_right.x * width)
            hip_right_y = int(hip_right.y * height)

            knee_left_y = int(knee_left.y * height)
            knee_right_y = int(knee_right.y * height)

            # --------------------------------------------------
            # CENTRO DA CINTURA
            # --------------------------------------------------
            center_x = (hip_left_x + hip_right_x) // 2
            center_y = (hip_left_y + hip_right_y) // 2

            # --------------------------------------------------
            # TAMANHO DA ROUPA
            # --------------------------------------------------
            # Aumentamos a largura para cobrir mais o quadril.
            hip_width_px = abs(hip_right_x - hip_left_x)

            clothing_width = int(hip_width_px * 2.90)
            clothing_width = max(clothing_width, 130)

            knee_y = (knee_left_y + knee_right_y) // 2
            leg_length = knee_y - center_y

            clothing_height = int(leg_length * 0.95)
            clothing_height = max(clothing_height, 130)

            # --------------------------------------------------
            # POSIÇÃO DA ROUPA
            # --------------------------------------------------
            # Antes a bermuda subia demais.
            # Agora vamos descer um pouco para encaixar melhor.
            x_pos = int(center_x - clothing_width / 2)
            y_pos = int(center_y - clothing_height * 0.35)

            # --------------------------------------------------
            # SUAVIZAÇÃO DA ROUPA
            # --------------------------------------------------
            if prev_clothing_width is None:
                prev_clothing_width = clothing_width
                prev_clothing_height = clothing_height
                prev_x_pos = x_pos
                prev_y_pos = y_pos
            else:
                clothing_width = int(alpha * prev_clothing_width + (1 - alpha) * clothing_width)
                clothing_height = int(alpha * prev_clothing_height + (1 - alpha) * clothing_height)
                x_pos = int(alpha * prev_x_pos + (1 - alpha) * x_pos)
                y_pos = int(alpha * prev_y_pos + (1 - alpha) * y_pos)

                prev_clothing_width = clothing_width
                prev_clothing_height = clothing_height
                prev_x_pos = x_pos
                prev_y_pos = y_pos

            # --------------------------------------------------
            # ROTACIONAR E APLICAR ROUPA
            # --------------------------------------------------
            # Mantemos a bermuda reta para ficar mais estável.
            angle = 0

            rotated_clothing = rotate_image(clothing, angle)

            frame = overlay_clothing(
                frame,
                rotated_clothing,
                x_pos,
                y_pos,
                clothing_width,
                clothing_height
            )

        # --------------------------------------------------
        # TEXTO NA TELA
        # --------------------------------------------------
        cv2.putText(
            frame,
            f"Ombro: {shoulder_cm:.1f} cm",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Quadril est.: {hip_circumference_cm:.1f} cm",
            (30, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Cintura est.: {waist_circumference_cm:.1f} cm",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Altura aprox.: {height_cm:.1f} cm",
             (30, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
             0.7,
            (0, 255, 0),
             2
        )

        cv2.putText(
            frame,
            f"Tamanho recomendado: {recommended_size}",
            (30, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    cv2.imshow("Provador Virtual", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ==========================================================
# FINALIZAÇÃO
# ==========================================================

cap.release()
cv2.destroyAllWindows()