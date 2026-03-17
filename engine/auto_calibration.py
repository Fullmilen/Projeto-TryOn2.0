import math

# ==========================================================
# CALIBRAÇÃO AUTOMÁTICA
# ==========================================================
# Ajustei a largura de ombros de referência para um valor
# mais compatível com o teste atual, o que ajuda a
# aproximar melhor a altura estimada.
# O PROBLEMA É QUE A LARGURA DE OMBROS NÃO ESTÁ VARIANDO DE PESSOA PARA PESSOA, 
# ENTÃO A ALTURA ESTIMADA FICA SEM VARIAÇÃO TAMBÉM. PRECISAMOS DE OUTRO REFERENCIAL PARA CALIBRAR MELHOR A ALTURA.
# ==========================================================

REFERENCE_SHOULDER_WIDTH_CM = 33.5


def calibrate_scale(landmarks, width, height):
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    x1 = int(left_shoulder.x * width)
    y1 = int(left_shoulder.y * height)

    x2 = int(right_shoulder.x * width)
    y2 = int(right_shoulder.y * height)

    shoulder_distance_px = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    if shoulder_distance_px <= 0:
        return 1.0

    scale = REFERENCE_SHOULDER_WIDTH_CM / shoulder_distance_px
    return scale