### it can use one topic for record and not complete the function for multi topic

import os
import cv2
import copy
import rosbag
import numpy as np
from calibration.calib import Calibration
from cv_bridge import CvBridge

def params(flag):
        bag_path = '/workspace/media/cvlab-swlee/23a423e0-9c48-443e-b8c4-876e0c652b7e/0622_avande/xingyou_work/'
        save_path = '/workspace/home/cvlab-swlee/Desktop/tool/Image_avande/'
        bag_list = sorted(get_bag_list(bag_path, '.bag'))
        image_topic = '/camera/image_color'

        param_dict = {
            'bag_path': bag_path,
            'bag_list': bag_list,
            'image_topic': image_topic,
            'save_path': save_path
        }

        #### undistort image option
        if flag:
            camera_path = 'calibration/f_camera_video1.txt'
            img_size = (1920, 1080)
            param_dict.update({
                'camera_path': camera_path,
                'img_size': img_size
            })

        return param_dict 

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_bag_list(path,file_type):
    image_names = []
    for maindir, subdir, file_name_list in os.walk(path):
        print(maindir)
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            ext = os.path.splitext(apath)[1]
            if ext in file_type:
                image_names.append(apath)
    return image_names

class BAG2IMG:
    def __init__(self, iscalibration_flag):
        self.bag_list = parameters['bag_list']
        self.save_path = parameters['save_path']
        self.iscalibration_flag = iscalibration_flag
        self.bridge = CvBridge()
        
        if iscalibration_flag:
            self.calib =  Calibration(camera_path)
            camera_path = parameters['camera_path']
            self.width,self.height = parameters['img_size']


    def image_read(self,msg, save_fname):
        np_arr = np.frombuffer(msg.data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        if self.iscalibration_flag:
            img = cv2.resize(img, (self.width,self.height))
            img = self.calib.undistort(img)
            
        cur_img = copy.copy(img)
        cv2.imwrite(save_fname, cur_img)

    def run(self,save_topic):
        for bag_p in self.bag_list:
            bag = rosbag.Bag(bag_p)
            tag_bag = bag_p.split('_')[-1].split('.bag')[0]
            save_dir = f'{self.save_path+tag_bag}'
            mkdir(save_dir)
            for i, (topic, msg, t) in enumerate(bag.read_messages(topics=[save_topic])):
                save_fname = f'{save_dir}/{str(i).zfill(6)}.png'
                self.image_read(msg, save_fname)
            bag.close()

if __name__ == "__main__":

    iscalibration_flag = False  # or False, depending on your requirement
    parameters = params(iscalibration_flag)

    image_topic = parameters['image_topic'] ### its for single

    record = BAG2IMG(iscalibration_flag)
    record.run(image_topic)
