import time
import cv2
import mediapipe as mp
import pygame


# --------------------------
# 简要契约
# - 输入: 摄像头帧
# - 输出: Pygame 窗口显示摄像头 & 游戏提示
# - 事件: 闭眼 -> 敌人靠近, 惊讶 -> 剧情反转, 挥手 -> 门打开
# - 容错/防抖: 每个事件需要连续检测若干帧或有冷却时间
# --------------------------


# MediaPipe 配置
mp_face = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils

# face_mesh: 非静态图像模式，限制人脸数量，降低延迟
face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True,
                             min_detection_confidence=0.5, min_tracking_confidence=0.5)


# Pygame 初始化
pygame.init()
SCREEN_W, SCREEN_H = 960, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption('恐怖游戏 原型')
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()


# 摄像头
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# 检测与防抖参数
CLOSED_EYE_FRAMES = 6        # 连续帧数判定为闭眼

COOLDOWN_AFTER_EVENT = 2.0   # 触发后冷却（秒）以避免频繁触发
EAR_THRESHOLD = 0.20        # EAR 小于该值判定闭眼（可调）


# 游戏状态
enemy_near = False

# 计数器 / 时间戳
closed_eye_count = 0

# only need enemy timestamp + blackout
last_enemy_time = 0.0
blackout_until = 0.0  # timestamp until which the screen stays black after blink

# 单场景原型（门/剧情相关逻辑已移除）


def compute_ear(landmarks):
    """Compute average EAR (eye aspect ratio) from landmarks. Return float or None on error."""
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [263, 387, 385, 362, 380, 373]
    def ear(eye_idxs):
        try:
            p = [landmarks[i] for i in eye_idxs]
            A = ((p[1].x - p[5].x)**2 + (p[1].y - p[5].y)**2)**0.5
            B = ((p[2].x - p[4].x)**2 + (p[2].y - p[4].y)**2)**0.5
            C = ((p[0].x - p[3].x)**2 + (p[0].y - p[3].y)**2)**0.5
            if C == 0:
                return None
            return (A + B) / (2.0 * C)
        except Exception:
            return None

    left_ear = ear(LEFT_EYE)
    right_ear = ear(RIGHT_EYE)
    if left_ear is None or right_ear is None:
        return None
    return (left_ear + right_ear) / 2.0


def compute_mar_and_brow(landmarks):
    """Compute MAR and brow-raise boolean. Return (mar, brow_raise) or (None, False) on error."""
    try:
        top = landmarks[13]
        bottom = landmarks[14]
        left = landmarks[61]
        right = landmarks[291]
        vert = ((top.x - bottom.x)**2 + (top.y - bottom.y)**2)**0.5
        horiz = ((left.x - right.x)**2 + (left.y - right.y)**2)**0.5
        if horiz == 0:
            return None, False
        mar = vert / horiz
        brow_raise = (landmarks[105].y - landmarks[10].y) < -0.03
        return mar, brow_raise
    except Exception:
        return None, False




# hand/wave detection removed for now (kept out of prototype per request)


def frame_to_surface(frame, target_w, target_h):
    """Convert BGR OpenCV frame to Pygame surface and scale to target size."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.flip(frame_rgb, 1)  # 镜像
    surf = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.shape[1::-1], 'RGB')
    surf = pygame.transform.smoothscale(surf, (target_w, target_h))
    return surf


running = True
debug = True  # 开发时默认打开 debug，便于观察 EAR/MAR 与关键点（运行稳定后可改为 False）

while running:
    ret, frame = cap.read()
    if not ret:
        print('无法读取摄像头帧，退出')
        break

    h, w = frame.shape[:2]
    # 处理图像用于 mediapipe（RGB）
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_face = face_mesh.process(frame_rgb)

    now = time.time()

    # 默认每轮重置这些临时检测（若检测到则计数增加）
    face_detected = False

    # 人脸
    ear_val = None
    if results_face and results_face.multi_face_landmarks:
        face_detected = True
        for face_landmarks in results_face.multi_face_landmarks:
            lm = face_landmarks.landmark
            # compute metrics
            ear_val = compute_ear(lm)
            if ear_val is not None and ear_val < EAR_THRESHOLD:
                closed_eye_count += 1
            else:
                closed_eye_count = 0

            # 绘制人脸关键点（可选）
            if debug:
                # draw full mesh
                mp_draw.draw_landmarks(frame, face_landmarks, mp_face.FACEMESH_TESSELATION,
                                       mp_draw.DrawingSpec(color=(0,255,0), thickness=1, circle_radius=1),
                                       mp_draw.DrawingSpec(color=(255,0,0), thickness=1))
                try:
                    # draw key eye/mouth points used for EAR/MAR so we can visually verify
                    pts = {
                        'left_eye': [33,160,158,133,153,144],
                        'right_eye': [263,387,385,362,380,373],
                        'mouth': [13,14,61,291]
                    }
                    h, w = frame.shape[:2]
                    for name, idxs in pts.items():
                        for i in idxs:
                            p = face_landmarks.landmark[i]
                            cx, cy = int(p.x * w), int(p.y * h)
                            cv2.circle(frame, (cx, cy), 2, (0, 255, 255), -1)
                except Exception:
                    pass
                # print debug to console
                print(f"[DEBUG] face detected - EAR={ear_val} closed_count={closed_eye_count}")

    else:
        closed_eye_count = 0

    # 手势检测已移除（仅保留闭眼触发）

    # 事件触发判断（需要连续若干帧并且尊重冷却）
    if closed_eye_count >= CLOSED_EYE_FRAMES and (now - last_enemy_time) > COOLDOWN_AFTER_EVENT:
        enemy_near = True
        last_enemy_time = now
        # trigger 2-second blackout when player blinks
        blackout_until = now + 2.0
        # reset counts so we don't immediately retrigger
        closed_eye_count = 0
        print(f"[EVENT] enemy_near triggered at {now} -> blackout until {blackout_until}")

    # 把摄像头画面显示在 Pygame
    # If blackout is active, render a full black screen and skip camera drawing
    if now < blackout_until:
        screen.fill((0, 0, 0))
        # optional: show a subtle message or countdown
        remain = int(blackout_until - now + 0.5)
        small = pygame.font.SysFont(None, 28)
        msg = small.render(f'', True, (0,0,0))
        # explicitly keep screen black — no camera surface
    else:
        screen.fill((0, 0, 0))
        cam_surf = frame_to_surface(frame, SCREEN_W, SCREEN_H)
        screen.blit(cam_surf, (0, 0))

    # 根据状态显示 UI
    y = 20
    if enemy_near:
        text = font.render('👹 敌人靠近了！', True, (255, 0, 0))
        screen.blit(text, (20, y)); y += 40

    # 单场景原型（门/剧情提示已移除）

    # debug 信息
    if debug:
        dbg_text = f'closed:{closed_eye_count}'
        if ear_val is not None:
            dbg_text += f' | EAR:{ear_val:.3f}'
        dbg = font.render(dbg_text, True, (255,255,0))
        screen.blit(dbg, (20, SCREEN_H - 40))

    pygame.display.flip()

    # 事件和状态的自动重置（例如播放提示后可以自动消除状态）
    # 这里示例：2 秒后自动清除 enemy_near
    if enemy_near and (now - last_enemy_time) > 2.0:
        enemy_near = False

    # 事件循环（退出/按键）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                debug = not debug
            if event.key == pygame.K_ESCAPE:
                running = False

    clock.tick(30)

# 清理
cap.release()
pygame.quit()