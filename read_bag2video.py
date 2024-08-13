### it can use one topic for record and not complete the function for multi topic

import os
import cv2
import copy
import rosbag
import numpy as np
from calibration.calib import Calibration


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
    def __init__(self, camera_path, bag_path, img_size, save_path):
        self.calib =  Calibration(camera_path)
        self.width,self.height = img_size
        self.video = None
        self.bag_path = bag_path
        self.save_path = save_path

    def recorder(self,width, height, filename='video'):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        result_video_path = self.output_path(filename)
        return cv2.VideoWriter(result_video_path, fourcc, 30.0, (int(width), int(height)))

    def output_path(self,filename):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        file_ext = '.mp4'
        save_file = f'{dir_path}/{self.save_path}'
        if not os.path.exists(save_file):
           os.mkdir(save_file)
        output_path=f'{dir_path}/{self.save_path}/{filename}_{file_ext}'
        uniq=1
        while os.path.exists(output_path):
            output_path = f'{dir_path}/{self.save_path}/{filename}_{uniq}{file_ext}' 
            uniq+=1
        return output_path

    def image_read(self,msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        # img = cv2.resize(img, (self.width,self.height))
        img = self.calib.undistort(img)
        cur_img = copy.copy(img)
        self.video.write(cur_img)

    def main(self,save_topic):
        bag_path = self.bag_path
        bag = rosbag.Bag(bag_path)
        self.video = self.recorder(self.width, self.height)
        count =0
        for topic, msg, t in bag.read_messages(topics=[save_topic]):
            count +=1
            if 100 <= count <500:
                self.image_read(msg)
                print(count)
            elif count < 100:
                pass
            else:
                break
        bag.close()
        self.video.release()

if __name__ == "__main__":
    bag_path = '/home/cvlab-swlee/Desktop/bag/q/20240206'
    bag_list = sorted(get_bag_list(bag_path, '.bag'))

    save_topic = '/gmsl_camera/dev/video1/compressed'
    camera_path = 'calibration/f_camera_video1.txt'
    save_path = 'results'
    img_size = (1920,1080)
    for bag_file in bag_list:
        record = BAG2IMG(camera_path, bag_file, img_size, save_path)
        record.main(save_topic)
