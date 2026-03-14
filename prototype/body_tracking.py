# ==========================================
# IMPORTAÇÃO DAS BIBLIOTECAS
# ==========================================

import cv2                  # Biblioteca para capturar a câmera
import mediapipe as mp      # Biblioteca para rastrear o corpo


# ==========================================
# CONFIGURAÇÃO DO MEDIAPIPE
# ==========================================

mp_pose = mp.solutions.pose              # Acessa módulo de pose
pose = mp_pose.Pose()                    # Inicializa detector de pose
mp_drawing = mp.solutions.drawing_utils  # Ferramenta para desenhar esqueleto


# ==========================================
# ABRE A CÂMERA
# ==========================================

cap = cv2.VideoCapture(0)  # 0 = câmera padrão


# ==========================================
# LOOP PRINCIPAL
# ==========================================

while True:

    ret, frame = cap.read()  # Captura um frame da câmera
    
    if not ret:
        print("Erro ao acessar a câmera")
        break

    # Converte BGR (OpenCV) para RGB (MediaPipe trabalha em RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processa a imagem para detectar pose
    results = pose.process(rgb_frame)

    # Se o corpo for detectado
    if results.pose_landmarks:

        # Desenha o esqueleto na tela
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        # ==========================================
        # COLETA DAS COORDENADAS
        # ==========================================

        landmarks = results.pose_landmarks.landmark

        # Exemplo: pegar ombro esquerdo (índice 11)
        left_shoulder = landmarks[11]

        # As coordenadas vêm normalizadas (entre 0 e 1)
        # Precisamos converter para pixels reais

        height, width, _ = frame.shape

        x_pixel = int(left_shoulder.x * width)
        y_pixel = int(left_shoulder.y * height)

        # Desenha um círculo no ombro esquerdo
        cv2.circle(frame, (x_pixel, y_pixel), 10, (0, 255, 0), -1)

        # Mostra coordenadas na tela
        cv2.putText(frame,
                    f"Ombro Esq: ({x_pixel}, {y_pixel})",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2)

        # Imprime coordenadas no terminal
        print(f"Ombro esquerdo -> X: {x_pixel} | Y: {y_pixel}")

    # Mostra o vídeo
    cv2.imshow("Rastreamento Corporal", frame)

    # Fecha ao apertar Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# ==========================================
# ENCERRAMENTO
# ==========================================

cap.release()
cv2.destroyAllWindows()
