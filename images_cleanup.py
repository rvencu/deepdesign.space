import cvlib    # high level module, uses YOLO model with the find_common_objects method
import cv2      # image/video manipulation, allows us to pass frames to cvlib
from argparse import ArgumentParser
import os
import sys
from datetime import datetime
#import smtplib, ssl # for sending email alerts
import imghdr
#from imutils.object_detection import non_max_suppression
import numpy as np
import math


# these will need to be fleshed out to not miss any formats
IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.JPEG', '.JPG','.PNG','.WEBP']

# used to make sure we are at least examining one valid file
VALID_FILE_ALERT = False

net = cv2.dnn.readNet("frozen_east_text_detection.pb")

def decode(scores, geometry, scoreThresh):
    detections = []
    confidences = []

    ############ CHECK DIMENSIONS AND SHAPES OF geometry AND scores ############
    assert len(scores.shape) == 4, "Incorrect dimensions of scores"
    assert len(geometry.shape) == 4, "Incorrect dimensions of geometry"
    assert scores.shape[0] == 1, "Invalid dimensions of scores"
    assert geometry.shape[0] == 1, "Invalid dimensions of geometry"
    assert scores.shape[1] == 1, "Invalid dimensions of scores"
    assert geometry.shape[1] == 5, "Invalid dimensions of geometry"
    assert scores.shape[2] == geometry.shape[2], "Invalid dimensions of scores and geometry"
    assert scores.shape[3] == geometry.shape[3], "Invalid dimensions of scores and geometry"
    height = scores.shape[2]
    width = scores.shape[3]
    for y in range(0, height):

        # Extract data from scores
        scoresData = scores[0][0][y]
        x0_data = geometry[0][0][y]
        x1_data = geometry[0][1][y]
        x2_data = geometry[0][2][y]
        x3_data = geometry[0][3][y]
        anglesData = geometry[0][4][y]
        for x in range(0, width):
            score = scoresData[x]

            # If score is lower than threshold score, move to next x
            if(score < scoreThresh):
                continue

            # Calculate offset
            offsetX = x * 4.0
            offsetY = y * 4.0
            angle = anglesData[x]

            # Calculate cos and sin of angle
            cosA = math.cos(angle)
            sinA = math.sin(angle)
            h = x0_data[x] + x2_data[x]
            w = x1_data[x] + x3_data[x]

            # Calculate offset
            offset = ([offsetX + cosA * x1_data[x] + sinA * x2_data[x], offsetY - sinA * x1_data[x] + cosA * x2_data[x]])

            # Find points for rectangle
            p1 = (-sinA * h + offset[0], -cosA * h + offset[1])
            p3 = (-cosA * w + offset[0],  sinA * w + offset[1])
            center = (0.5*(p1[0]+p3[0]), 0.5*(p1[1]+p3[1]))
            detections.append((center, (w,h), -1*angle * 180.0 / math.pi))
            confidences.append(float(score))

    # Return detections and confidences
    return [detections, confidences]

# function takes a file name(full path), checks that file for human shaped objects
# saves the frames with people detected into directory named 'save_directory'
def humanChecker(video_file_name, save_directory, yolo='yolov4', continuous=False, nth_frame=10, confidence=.65, gpu=True):

    # for modifying our global variarble VALID_FILE
    global VALID_FILE_ALERT

    # tracking if we've found a human or not
    is_human_found = False
    analyze_error = False
    is_valid = False

    # we'll need to increment every time a person is detected for file naming
    person_detection_counter = 0

    # check if image
    if os.path.splitext(video_file_name)[1] in IMG_EXTENSIONS:
        frame = cv2.imread(video_file_name)  # our frame will just be the image
        #make sure it's a valid image
        if frame is not None:
            frame_count = 8   # this is necessary so our for loop runs below
            nth_frame = 1
            VALID_FILE_ALERT = True
            is_valid = True
            #print(f'Image')
        else:
            is_valid = False
            analyze_error = True
    else:
        print(f'', end='')
    
    if is_valid:
        # look at every nth_frame of our video file, run frame through detect_common_objects
        # Increase 'nth_frame' to examine fewer frames and increase speed. Might reduce accuracy though.
        # Note: we can't use frame_count by itself because it's an approximation and could lead to errors
        for frame_number in range(1, frame_count - 6, nth_frame):

            # feed our frame (or image) in to detect_common_objects
            try:
                
                bbox, labels, conf = cvlib.detect_common_objects(frame, model=yolo, confidence=confidence, enable_gpu=gpu)
            except Exception as e:
                print(e)
                analyze_error = True
                break

            if 'person' in labels:
                person_detection_counter += 1
                is_human_found = True

                # create image with bboxes showing people and then save
                marked_frame = cvlib.object_detection.draw_bbox(frame, bbox, labels, conf, write_conf=True)
                save_file_name = os.path.basename(os.path.splitext(video_file_name)[0]) + '-human-' + str(person_detection_counter) + '.jpeg'
                cv2.imwrite(save_directory + '\\\\' + save_file_name , marked_frame)

                if continuous is False:
                    break

    return is_human_found, analyze_error

def textChecker(video_file_name, save_directory, continuous=False, nth_frame=10, confidence=.65, gpu=False):

    # we'll need to increment every time a person is detected for file naming
    text_detection_counter = 0

    is_text_found=False

    if os.path.splitext(video_file_name)[1] in IMG_EXTENSIONS:

        image = cv2.imread(video_file_name)
        orig = image.copy()
        (H, W) = image.shape[:2]

        # set the new width and height and then determine the ratio in change
        # for both the width and height
        (newW, newH) = (320, 320)
        rW = W / float(newW)
        rH = H / float(newH)

        # resize the image and grab the new image dimensions
        image = cv2.resize(image, (newW, newH))
        (H, W) = image.shape[:2]

        # define the two output layer names for the EAST detector model that
        # we are interested -- the first is the output probabilities and the
        # second can be used to derive the bounding box coordinates of text
        layerNames = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"]

        # construct a blob from the image and then perform a forward pass of
        # the model to obtain the two output layer sets
        blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
        net.setInput(blob)
        (scores, geometry) = net.forward(layerNames)

        # grab the number of rows and columns from the scores volume, then
        # initialize our set of bounding box rectangles and corresponding
        # confidence scores
        (numRows, numCols) = scores.shape[2:4]
        rects = []
        confidences = []

        [boxes, confidences] = decode(scores, geometry, 0.9999)

        indices = cv2.dnn.NMSBoxesRotated(boxes, confidences, 0.9999, 0.9999)

        if len(indices)>0:
            text_detection_counter += 1
            is_text_found=True

            # show the output image
            save_file_name = os.path.basename(os.path.splitext(video_file_name)[0]) + '-text-' + str(text_detection_counter) + '.jpeg'
            cv2.imwrite(save_directory + '\\\\' + save_file_name , orig)
    
    return is_text_found

def dimChecker(video_file_name, save_directory, continuous=False, nth_frame=10, confidence=.65, gpu=False):

    # we'll need to increment every time a person is detected for file naming
    small_detection_counter = 0

    is_small_found=False

    if os.path.splitext(video_file_name)[1] in IMG_EXTENSIONS:

        image = cv2.imread(video_file_name)
        orig = image.copy()
        (H, W) = image.shape[:2]

        if min(H, W)<300:
            small_detection_counter += 1
            is_small_found=True

            # show the output image
            save_file_name = os.path.basename(os.path.splitext(video_file_name)[0]) + '-small-' + str(small_detection_counter) + '.jpeg'
            cv2.imwrite(save_directory + '\\\\' + save_file_name , orig)
    else:
        small_detection_counter += 1
        is_small_found=True
    
    return is_small_found

# takes a directory and returns all files and directories within
def getListOfFiles(dir_name):
    list_of_files = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in list_of_files:
        # ignore hidden files and directories
        if entry[0] != '.':
            # Create full path
            full_path = os.path.join(dir_name+os.sep+os.sep, entry)
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(full_path):
                all_files = all_files + getListOfFiles(full_path)
            else:
                all_files.append((dir_name,full_path))
    return all_files

#############################################################################################################################
if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-d', '--directory', default='', help='Path to video folder')
    parser.add_argument('-f', default='', help='Used to select an individual file')
    parser.add_argument('--tiny_yolo', action='store_true', help='Flag to indicate using YoloV4-tiny model instead of the full one. Will be faster but less accurate.')
    parser.add_argument('--confidence', type=int, choices=range(1,100), default=65, help='Input a value between 1-99. This represents the percent confidence you require for a hit. Default is 65')
    parser.add_argument('--gpu', action='store_true', help='Attempt to run on GPU instead of CPU. Requires Open CV compiled with CUDA enables and Nvidia drivers set up correctly.')

    args = vars(parser.parse_args())

    # decide which model we'll use, default is 'yolov3', more accurate but takes longer
    if args['tiny_yolo']:
        yolo_string = 'yolov4-tiny'
    else:
        yolo_string = 'yolov4'

        
    #check our inputs, can only use either -f or -d but must use one
    if args['f'] == '' and args['directory'] == '':
        print('You must select either a directory with -d <directory> or a file with -f <file name>')
        sys.exit(1)
    if args['f'] != '' and args['directory'] != '' :
        print('Must select either -f or -d but can''t do both')
        sys.exit(1)

    confidence_percent = args['confidence'] / 100
    
    gpu_flag = False
    if args['gpu']:
        gpu_flag = True

    # create a directory to hold snapshots and log file
    time_stamp = datetime.now().strftime('%m%d%Y-%H-%M-%S')
    os.mkdir(time_stamp)

    print('Beginning Detection')
    print(f'Directory {time_stamp} has been created')
    print(f"GPU is set to {args['gpu']}")
    print('\n\n')
    print(datetime.now().strftime('%m%d%Y-%H:%M:%S'))

    # open a log file and loop over all our video files
    with open(time_stamp + '\\' + time_stamp +'.txt', 'w') as log_file:
        if args['f'] == '':
            video_directory_list = getListOfFiles(args['directory'] + '\\\\')
        else:
            video_directory_list = [args['f']]

        # what video we are on
        working_on_counter = 1

        path_tuple = ("humans","small","texts")

        for (file_path,video_file) in video_directory_list:
            if not file_path.endswith(path_tuple):
                print(f'', end='')

                if not os.path.exists(file_path+os.sep+os.sep+'humans'):
                    os.mkdir(file_path+os.sep+os.sep+'humans')
                    os.mkdir(file_path+os.sep+os.sep+'small')
                    os.mkdir(file_path+os.sep+os.sep+'texts')

                # check for people
                human_detected, error_detected =  humanChecker(str(video_file), file_path+os.sep+os.sep+'humans', yolo=yolo_string, confidence=confidence_percent, gpu=gpu_flag)

                if human_detected:    
                    HUMAN_DETECTED_ALERT = True
                    print(f'Human detected in {video_file}')
                    log_file.write(f'{video_file} \n' )
                    os.remove(f'{video_file}')

                elif dimChecker(str(video_file), file_path+os.sep+os.sep+'small', confidence=confidence_percent, gpu=gpu_flag):
                    SMALL_DETECTED_ALERT = True
                    print(f'Small dimensions detected in {video_file}')
                    log_file.write(f'{video_file} \n' )
                    os.remove(f'{video_file}')

                elif textChecker(str(video_file), file_path+os.sep+os.sep+'texts', confidence=confidence_percent, gpu=gpu_flag):
                    TEXT_DETECTED_ALERT = True
                    print(f'Text detected in {video_file}')
                    log_file.write(f'{video_file} \n' )
                    os.remove(f'{video_file}')
                
                if error_detected:
                    ERROR_ALERT = True
                    print(f'\nError in analyzing {video_file}')
                    log_file.write(f'Error in analyzing {video_file} \n' )

                working_on_counter += 1

    if VALID_FILE_ALERT is False:
        print('No valid image or video files were examined')

    print(datetime.now().strftime('%m%d%Y-%H:%M:%S'))