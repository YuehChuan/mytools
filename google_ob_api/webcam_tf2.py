#python object_detection/export_inference_graph.py \
#    --input_type image_tensor \
#    --pipeline_config_path /home/digits/works/Google_OB_Projects/faster_rcnn_inception_v2_coco/palm_num/faster_rcnn_inception_v2_coco.config \
#    --trained_checkpoint_prefix /home/digits/works/Google_OB_Projects/faster_rcnn_inception_v2_coco/palm_num/training/model.ckpt-9965 \
#    --output_directory /home/digits/works/Google_OB_Projects/faster_rcnn_inception_v2_coco/palm_num/graph

import numpy as np
import tensorflow as tf
import cv2 as cv
import imutils

model_path = "tf_frozened_masks_wearing.pb"
pbtxt_path = "dnn_masks_wearing.pbtxt"
source = "demo.mp4"  # "0","1".. --> webcam, or "/xx/xxxx.mp4"
rotate = 0
display_width = 720
#source ="0"

make_video = True
make_video_path = "output.avi"

class_map = {1:"none", 2:"mask", 3:"not_ok"}
#-----------------------------------------------------------

# Read the graph.
with tf.io.gfile.GFile(model_path, 'rb') as f:
    graph_def = tf.compat.v1.GraphDef()
    graph_def.ParseFromString(f.read())

with tf.compat.v1.Session() as sess:
    # Restore session
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name='')

    if(len(source)==1):
        INPUT = cv.VideoCapture(int(source))
    else:
        INPUT = cv.VideoCapture(source)

    width = int(INPUT.get(cv.CAP_PROP_FRAME_WIDTH))   # float
    height = int(INPUT.get(cv.CAP_PROP_FRAME_HEIGHT)) # float
    print(width, height)

    if make_video is True:
        fourcc = cv.VideoWriter_fourcc(*'MJPG')
        videoout = cv.VideoWriter(make_video_path, fourcc, 30, (width, height))


    while True:

        hasFrame, img = INPUT.read()
        # Stop the program if reached end of video
        if hasFrame:
            # Read and preprocess an image.
            if(rotate != 0):
                img = imutils.rotate_bound(img, rotate)

            rows = img.shape[0]
            cols = img.shape[1]
            inp = cv.resize(img, (300, 300))
            inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

            # Run the model
            out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                            sess.graph.get_tensor_by_name('detection_scores:0'),
                            sess.graph.get_tensor_by_name('detection_boxes:0'),
                            sess.graph.get_tensor_by_name('detection_classes:0')],
                            feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

            # Visualize detected bounding boxes.
            num_detections = int(out[0][0])
            for i in range(num_detections):
                classId = int(out[3][0][i])
                score = float(out[1][0][i])
                bbox = [float(v) for v in out[2][0][i]]
                if score > 0.35:
                    x = bbox[1] * cols
                    y = bbox[0] * rows
                    right = bbox[3] * cols
                    bottom = bbox[2] * rows
                    cv.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=2)
                    cv.putText(img,class_map[int(classId)] ,(int(x), int(y)),cv.FONT_HERSHEY_SIMPLEX,(.001*width),(0, 0, 255), 2)
                    print(class_map[classId], score, x, y)


            cv.imshow('TensorFlow MobileNet-SSD', imutils.resize(img, width=display_width))

            if(make_video is True):
                videoout.write(img)
            cv.waitKey(1)

        else:
            if make_video is True:
                videoout.release()
