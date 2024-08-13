import os
import numpy as np
import cv2
import glob
import time
import matplotlib.pyplot as plt


#### TODO: Changing Parameter for your task
def params():
    #### ***** IMPORTANT ***** ####
    #### Set mode for checking corner point or take output of calibration
    mode_list = ["filter_corner_detectable",'calibration']
    mode = mode_list[0]

    inter_corner_shape = (9, 6)
    size_per_grid = 0.0248 ## meter

    # file_path = 'path to your file'
    file_path = '/workspace/Image_avande/raw/'
    img_type = "png"
    # camera_name_list = ['front', 'left', 'right']
    camera_name_list = ['RightFront', 'RightRear']

    camera_name_dict = {name: name for name in camera_name_list}
    return {
        'img_type': img_type,
        'mode': mode,
        'file_path': file_path,
        ## expandable key and value and only use value as: 
        ## {'front': front, 'left': left, 'right': right, 'haha':hahah}
        'camera_name': camera_name_dict,
        'inter_corner_shape': inter_corner_shape,
        'size_per_grid': size_per_grid
    }

def save_calibration_data(data, img_dir, CAMERA_PARAMETERS_FILE):
    # Save calibration results to a text file
    ## change save format in here
    for index, msg in enumerate(data.items()):
        key, value = msg
        if index == 0:
            with open(img_dir + CAMERA_PARAMETERS_FILE + ".txt", 'w') as f:
                f.write(str(key) + ':' + '\n' + str(value) + '\n')
        else:
            with open(img_dir + CAMERA_PARAMETERS_FILE + ".txt", 'a') as f:
                f.write(str(key) + ':' + '\n' + str(value) + '\n')

def plot_reprojection_error(frame_error_list, Average_error):
    # Plot the reprojection error
    plt.figure()
    plt.plot(frame_error_list, label='Frame Error')
    plt.axhline(y=Average_error, color='r', linestyle='-', label='Average Error')
    plt.xlabel('Frame Index')
    plt.ylabel('Reprojection Error')
    plt.legend()
    plt.title('Reprojection Error per Frame')
    plt.show()

def poi_finding(inter_corner_shape, size_per_grid, img_dir, img_type, save_dir):
    
    w, h = inter_corner_shape
    cp_int = np.zeros((w * h, 3), np.float32)
    cp_int[:, :2] = np.mgrid[0:w, 0:h].T.reshape(-1, 2)
    cp_world = cp_int * size_per_grid
    obj_points = []  # Points in world coordinate system
    img_points = []  # Points in image coordinate system (corresponding to obj_points)
    images = glob.glob(img_dir + os.sep + '**.' + img_type)
    for fname in images:
        img_name = fname.split(os.sep)[-1]
        img = cv2.imread(fname)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, cp_img = cv2.findChessboardCorners(gray_img, (w, h), None)

        # If corners are found, save them
        if ret == True:
            obj_points.append(cp_world)
            img_points.append(cp_img)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (w, h), cp_img, ret)
            cv2.imwrite(save_dir + os.sep + img_name, img)
            print(fname)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        else:
            os.remove(fname)

def calib(inter_corner_shape, size_per_grid, img_dir, img_type, save_dir, CAMERA_PARAMETERS_FILE):
    
    w, h = inter_corner_shape
    cp_int = np.zeros((w * h, 3), np.float32)
    cp_int[:, :2] = np.mgrid[0:w, 0:h].T.reshape(-1, 2)
    cp_world = cp_int * size_per_grid
    obj_points = []  # Points in world coordinate system
    img_points = []  # Points in image coordinate system (corresponding to obj_points)
    images = glob.glob(img_dir + os.sep + '**.' + img_type)
    for fname in images:
        img_name = fname.split(os.sep)[-1]
        img = cv2.imread(fname)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, cp_img = cv2.findChessboardCorners(gray_img, (w, h), None)

        # If corners are found, save them
        if ret == True:
            obj_points.append(cp_world)
            img_points.append(cp_img)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (w, h), cp_img, ret)
            cv2.imwrite(save_dir + os.sep + img_name, img)
            print(fname)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # Calibrate the camera
    print("Calculating...")

    calib_ret, mat_inter, coff_dis, v_rot, v_trans = cv2.calibrateCamera(obj_points, img_points, gray_img.shape[::-1], None, None)
    frame_error_list, Average_error = post_process(obj_points, img_points, v_rot, v_trans, mat_inter, coff_dis)
    data = save_preprocess(calib_ret, mat_inter, coff_dis, v_rot, v_trans, Average_error)
    save_calibration_data(data, img_dir, CAMERA_PARAMETERS_FILE)
    plot_reprojection_error(frame_error_list, Average_error)

    return mat_inter, coff_dis

def save_preprocess(calib_ret, mat_inter, coff_dis, v_rot, v_trans, Average_error):
    data = {
          "ret": calib_ret,
          "mat_inter": mat_inter,
          "coff_dis": coff_dis,
          "v_rot": v_rot,
          "v_trans": v_trans,
          "Average_error": Average_error
      }
      
def post_process(obj_points, img_points, v_rot, v_trans, mat_inter, coff_dis):
      # Calculate reprojection error
      total_error = 0
      error_list = []
      frame_error_list = []
      x_error_list = []
      y_error_list = []
      x_error_ratio_list = []
      y_error_ratio_list = []
      for i in range(len(obj_points)):
          img_points_repro, _ = cv2.projectPoints(obj_points[i], v_rot[i], v_trans[i], mat_inter, coff_dis)
          num_points = img_points[i]
          frame_error = 0
          for j in range(len(num_points)):
              x_error = num_points[j][0][0] - img_points_repro[j][0][0]
              y_error = num_points[j][0][1] - img_points_repro[j][0][1]
              x_error_ratio = (num_points[j][0][0] - img_points_repro[j][0][0]) / num_points[j][0][0]
              y_error_ratio = (num_points[j][0][1] - img_points_repro[j][0][1]) / num_points[j][0][1]

              point_error = np.sqrt(x_error ** 2 + y_error ** 2)
              frame_error += point_error
              error_list.append(point_error)
              x_error_list.append(x_error)
              y_error_list.append(y_error)
              x_error_ratio_list.append(x_error_ratio)
              y_error_ratio_list.append(y_error_ratio)
          
          frame_error_list.append(frame_error / len(num_points))
          total_error += frame_error

      Average_error = total_error / len(obj_points)
      print("Average Reprojection Error: ", Average_error)

      return frame_error_list, Average_error
    
def undistortion(inter_corner_shape, img_dir, img_type, save_dir, mat_inter, coff_dis):
    w, h = inter_corner_shape
    images = glob.glob(img_dir + os.sep + '**.' + img_type)
    for fname in images:
        img_name = fname.split(os.sep)[-1]
        img = cv2.imread(fname)
        dst = cv2.undistort(img, mat_inter, coff_dis, None, mat_inter)
        cv2.imwrite(save_dir + os.sep + img_name, dst)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    print('Undistorted images have been saved to: %s' % save_dir)

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def image_process(camera_name, path, inter_corner_shape, size_per_grid, img_type, mode):
    img_dir = path + camera_name + '/'
    save_pio = img_dir.replace('raw','corner_finding')
    save_dir = img_dir.replace('raw','undistortion')
    # save_pio = img_dir + "../../corner_finding/"
    # save_dir = img_dir + '../../undistortion/'

    mkdir(save_pio)
    if mode == 'filter_corner_detectable':
        poi_finding(inter_corner_shape, size_per_grid, img_dir, img_type, save_pio)
    if mode == 'calibration':
        mat_inter, coff_dis = calib(inter_corner_shape, size_per_grid, img_dir, img_type, save_pio, camera_name)

        mkdir(save_dir)
        undistortion(inter_corner_shape, img_dir, img_type, save_dir, mat_inter, coff_dis)

if __name__ == '__main__':
    # Get parameters
    param = params()
    inter_corner_shape = param['inter_corner_shape']
    size_per_grid = param['size_per_grid']
    img_type = param['img_type']
    camera_name = param['camera_name']
    mode = param['mode']
    path = param['file_path']

    # Process data for each camera
    for cam in camera_name.values():
        image_process(cam, path, inter_corner_shape, size_per_grid, img_type, mode)
