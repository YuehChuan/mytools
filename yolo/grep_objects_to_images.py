from yoloOpencv import opencvYOLO
import cv2
import imutils
import time
import os

yolo = opencvYOLO(modeltype="yolov3", \
    objnames="../../../darknet/data/coco.names", \
    weights="../../../darknet/weights/yolov3.weights",\
    cfg="../../../darknet/cfg/yolov3.cfg")

objects = ("truck", "car", "motorcycle", "bus", "bicycle")
output_path = "yolo_objects/"
frame_interval =30

inputType = "video"  # webcam, image, video
media = "/home/chtseng/works/alpr/videos/4K/IMG_2195.MOV"
write_video = True
video_out = "/media/flash/cars_waiting/IMG_2195.avi"
output_rotate = False
rotate = 0

def check_env():
    if not os.path.exists(output_path):
        os.makedirs(output_path)

def chk_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

#fps count
start = time.time()
def fps_count(num_frames):
    end = time.time()
    seconds = end - start
    fps  = num_frames / seconds;
    print("Estimated frames per second : {0}".format(fps))
    return fps

if __name__ == "__main__":
    check_env()

    if(inputType == "webcam"):
        INPUT = cv2.VideoCapture(0)
    elif(inputType == "image"):
        INPUT = cv2.imread(media)
    elif(inputType == "video"):
        INPUT = cv2.VideoCapture(media)

    if(inputType == "image"):
        yolo.getObject(INPUT, labelWant="", drawBox=True, bold=1, textsize=0.6, bcolor=(0,0,255), tcolor=(255,255,255))
        print ("Object counts:", yolo.objCounts)
        print("classIds:{}, confidences:{}, labelName:{}, bbox:{}".\
        format(len(yolo.classIds), len(yolo.scores), len(yolo.labelNames), len(yolo.bbox)) )
        cv2.imshow("Frame", imutils.resize(INPUT, width=850))

        k = cv2.waitKey(0)
        if k == 0xFF & ord("q"):
            out.release()

    else:
        if(video_out!=""):
            width = int(INPUT.get(cv2.CAP_PROP_FRAME_WIDTH))   # float
            height = int(INPUT.get(cv2.CAP_PROP_FRAME_HEIGHT)) # float
            total_frames = int(INPUT.get(cv2.CAP_PROP_FRAME_COUNT))
            input("Total frames is "+str(total_frames)+", click ENTER to start.")

            if(write_video is True):
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter(video_out,fourcc, int(30.0/frame_interval), (int(width),int(height)))

        pic_id = 0
        frameID = 0
        obj_count = {}

        while True:
            hasFrame, frame = INPUT.read()
            if not hasFrame:
                print("Done processing !!!")
                break

            if(frameID % frame_interval == 0):
                frame_org = frame.copy()

                if(output_rotate is True):
                    frame = imutils.rotate(frame, rotate)

                yolo.getObject(frame, labelWant=objects, drawBox=True, bold=2, textsize=1.2, bcolor=(0,255,0), tcolor=(0,0,255))
                print("[FRAME #{}] objects:{}".format(total_frames-frameID, yolo.labelNames))

                for i, label in enumerate(yolo.labelNames):
                    folder_path = os.path.join(output_path, label)
                    chk_path(folder_path)
                    box = yolo.bbox[i]
                    x, y, w, h = box[0], box[1], box[2], box[3]
                    img_area = frame_org[y:y+h, x:x+w]

                    if(label in obj_count):
                        counts = obj_count[label]+1
                    else:
                        counts = 1

                    obj_count.update({label:counts})

                    filename = label + '_' + str(counts) + '.jpg'
                    cv2.imwrite(os.path.join(folder_path, filename), img_area)

                #print("classIds:{}, confidences:{}, labelName:{}, bbox:{}".\
                #    format(len(yolo.classIds), len(yolo.scores), len(yolo.labelNames), len(yolo.bbox)) )

                #cv2.imshow("Frame", imutils.resize(frame, width=850))
                pic_id += 1
                #fps_count(frameID)

                if(write_video is True):
                    out.write(frame)

                k = cv2.waitKey(1)
                if k == 0xFF & ord("q"):
                    if(write_video is True):
                        out.release()

                    break

            frameID += 1
