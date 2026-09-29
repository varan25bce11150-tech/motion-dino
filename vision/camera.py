
import cv2

class Camera:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def is_available(self):
        return self.cap is not None and self.cap.isOpened()

    def get_frame(self):
        if not self.is_available():
            return None
        
        success, frame = self.cap.read()
        if not success:
            return None
            
        
        return cv2.flip(frame, 1)

    def release(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()