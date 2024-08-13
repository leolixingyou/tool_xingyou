import cv2
import numpy as np

class Calibration:
    def __init__(self, camera_path):
        # camera parameters
        cam_param = []

        with open(camera_path, 'r') as f:
            for i in f.readlines():
                for val in i.split(','):
                    cam_param.append(float(val))

        '''Main(Front) Camera Calibration'''
        self.camera_matrix = np.array([[cam_param[0], cam_param[1], cam_param[2]], 
                                    [cam_param[3], cam_param[4], cam_param[5]], 
                                    [cam_param[6], cam_param[7], cam_param[8]]])
        self.dist_coeffs = np.array([[cam_param[9]], [cam_param[10]], [cam_param[11]], [cam_param[12]], [cam_param[13]]])
        
    def undistort(self, img):
        w,h = (img.shape[1], img.shape[0])

        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.dist_coeffs, (w,h), 0)
        result_img = cv2.undistort(img, self.camera_matrix, self.dist_coeffs, None, newcameramtx)

        return result_img
