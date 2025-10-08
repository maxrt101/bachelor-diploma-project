from ultralytics import YOLO
from functools import reduce
from log import logger
import cv2


def detect(filename: str, model: YOLO, conf: float = 0.6, imgsize: int = 416, scale_method: str = 'resize') -> str:
    capture = cv2.imread(filename)

    if scale_method == 'resize':
        resized = cv2.resize(capture, (imgsize, imgsize))
    elif scale_method == 'crop':
        h, w, _ = capture.shape
        x = int((w - imgsize) / 2)
        resized = capture[0:h, x:x+w]
    else:
        resized = capture

    filename_resized = filename.replace('.jpg', '_resized.jpg')

    cv2.imwrite(filename_resized, resized)

    result = model(filename_resized, conf=conf, verbose=False, save=True, imgsz=imgsize)
    classes = []

    for box in result[0].boxes:
        x1 = int(box.xyxy[0][0].item())
        y1 = int(box.xyxy[0][1].item())
        x2 = int(box.xyxy[0][2].item())
        y2 = int(box.xyxy[0][3].item())
        cls = int(box.cls)
        classes.append((x1, cls))

        cv2.rectangle(resized, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)

        font_scale = 0.5
        thickness = 1
        line_type = 2

        cv2.putText(
            resized,
            f'{int(round(box.conf.item(), 2) * 100)}',
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            font_scale,
            (0, 0, 255),
            thickness,
            line_type
        )

        cv2.putText(
            resized,
            f'{cls}',
            (x1, y1 - 20),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            font_scale,
            (0, 0, 255),
            thickness,
            line_type
        )

        logger.debug(f'Detect: x={x1} cls={cls} conf={round(box.conf.item(), 2)}')

    cv2.imwrite(filename.replace('.jpg', '_detect.jpg'), resized)

    classes = sorted(classes, key=lambda e: e[0])

    return reduce(lambda res, e: res + str(e[1]), classes, '')

