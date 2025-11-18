import time
import cv2
import mediapipe as mp

class EyeCapture:
    def __init__(self, ear_threshold=0.20, closed_frames=6, cooldown=10.0, blackout_time=2.0):
        self.ear_threshold = ear_threshold
        self.closed_frames = closed_frames
        self.cooldown = cooldown
        self.blackout_time = blackout_time

        self.closed_eye_count = 0
        self.last_enemy_time = 0.0
        self.blackout_until = 0.0
        self.enemy_near = False

        mp_face = mp.solutions.face_mesh
        self.face_mesh = mp_face.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

    def compute_ear(self, landmarks):
        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE = [263, 387, 385, 362, 380, 373]
        def ear(eye_idxs):
            p = [landmarks[i] for i in eye_idxs]
            A = ((p[1].x - p[5].x)**2 + (p[1].y - p[5].y)**2)**0.5
            B = ((p[2].x - p[4].x)**2 + (p[2].y - p[4].y)**2)**0.5
            C = ((p[0].x - p[3].x)**2 + (p[0].y - p[3].y)**2)**0.5
            if C == 0: return None
            return (A + B) / (2.0 * C)
        left = ear(LEFT_EYE); right = ear(RIGHT_EYE)
        return None if left is None or right is None else (left+right)/2.0

    def update(self, frame):
        """处理一帧，返回状态字典：{'blackout':bool, 'enemy':bool, 'ear':float}"""
        now = time.time()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        ear_val = None
        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            ear_val = self.compute_ear(lm)
            if ear_val is not None and ear_val < self.ear_threshold:
                self.closed_eye_count += 1
            else:
                self.closed_eye_count = 0
        else:
            self.closed_eye_count = 0

        # 事件触发
        if self.closed_eye_count >= self.closed_frames and (now - self.last_enemy_time) > self.cooldown:
            self.enemy_near = True
            self.last_enemy_time = now
            self.blackout_until = now + self.blackout_time
            self.closed_eye_count = 0

        # 自动重置敌人状态
        if self.enemy_near and (now - self.last_enemy_time) > 2.0:
            self.enemy_near = False

        blackout = now < self.blackout_until
        return {"blackout": blackout, "enemy": self.enemy_near, "ear": ear_val}