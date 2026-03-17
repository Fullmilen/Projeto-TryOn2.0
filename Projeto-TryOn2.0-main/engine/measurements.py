import math


# ==========================================================
# DISTÂNCIA ENTRE DOIS PONTOS
# ==========================================================
def distance(p1, p2):
    """
    Calcula a distância entre dois pontos 2D.
    Cada ponto é uma tupla no formato (x, y).
    """
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


# ==========================================================
# MEDIDAS CORPORAIS BASEADAS NA ALTURA REAL INFORMADA
# ==========================================================
def calculate_measurements(landmarks, width, height, real_height_cm):
    """
    Calcula medidas aproximadas do corpo usando a altura real informada.

    Retorna:
    - ombro em cm
    - largura frontal do quadril em cm
    - quadril estimado em cm
    - cintura estimada em cm
    - altura em cm
    """

    # ------------------------------------------------------
    # OMBROS
    # ------------------------------------------------------
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    left_shoulder_px = (
        int(left_shoulder.x * width),
        int(left_shoulder.y * height)
    )

    right_shoulder_px = (
        int(right_shoulder.x * width),
        int(right_shoulder.y * height)
    )

    shoulder_center_px = (
        int((left_shoulder_px[0] + right_shoulder_px[0]) / 2),
        int((left_shoulder_px[1] + right_shoulder_px[1]) / 2)
    )

    shoulder_width_px = distance(left_shoulder_px, right_shoulder_px)

    # ------------------------------------------------------
    # QUADRIL
    # ------------------------------------------------------
    left_hip = landmarks[23]
    right_hip = landmarks[24]

    left_hip_px = (
        int(left_hip.x * width),
        int(left_hip.y * height)
    )

    right_hip_px = (
        int(right_hip.x * width),
        int(right_hip.y * height)
    )

    hip_width_px = distance(left_hip_px, right_hip_px)

    # ------------------------------------------------------
    # TORNOZELOS
    # ------------------------------------------------------
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]

    left_ankle_px = (
        int(left_ankle.x * width),
        int(left_ankle.y * height)
    )

    right_ankle_px = (
        int(right_ankle.x * width),
        int(right_ankle.y * height)
    )

    # escolhe o tornozelo mais baixo da imagem
    lowest_ankle_px = left_ankle_px if left_ankle_px[1] > right_ankle_px[1] else right_ankle_px

    # ------------------------------------------------------
    # ESCALA BASEADA NA ALTURA REAL
    # ------------------------------------------------------
    # Medimos do centro dos ombros até o tornozelo e compensamos
    # um pouco para cabeça/pescoço.
    body_height_px = distance(shoulder_center_px, lowest_ankle_px)

    estimated_full_body_px = body_height_px * 1.02

    if estimated_full_body_px <= 0:
        scale = 1.0
    else:
        scale = real_height_cm / estimated_full_body_px

    # ------------------------------------------------------
    # CONVERSÕES PARA CENTÍMETROS
    # ------------------------------------------------------
    shoulder_cm = shoulder_width_px * scale
    hip_width_cm = hip_width_px * scale
    height_cm = estimated_full_body_px * scale

    # ------------------------------------------------------
    # ESTIMATIVAS DE CIRCUNFERÊNCIA
    # ------------------------------------------------------
    # Antes o fator estava muito baixo e derrubava o tamanho.
    # Agora aumentamos para ficar mais compatível com bermuda masculina.
    hip_circumference_cm = hip_width_cm * 3.7

    # estimativa simples da cintura com base no quadril
    waist_circumference_cm = hip_circumference_cm * 0.92

    return {
        "shoulder_cm": shoulder_cm,
        "hip_width_cm": hip_width_cm,
        "hip_circumference_cm": hip_circumference_cm,
        "waist_circumference_cm": waist_circumference_cm,
        "height_cm": height_cm
    }