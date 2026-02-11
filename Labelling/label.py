import cv2
import os

IMAGE_DIR = "Labelling/images"
LABEL_DIR = "Labelling/labels"

os.makedirs(LABEL_DIR, exist_ok=True)

class_id = 0  # person

images = sorted(os.listdir(IMAGE_DIR))

drawing = False
ix, iy = -1, -1
boxes = []

def draw(event, x, y, flags, param):
    global ix, iy, drawing, img, boxes

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp = img.copy()
            cv2.rectangle(temp, (ix, iy), (x, y), (0,255,0), 2)
            cv2.imshow("image", temp)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img, (ix, iy), (x, y), (0,255,0), 2)
        boxes.append((ix, iy, x, y))
        cv2.imshow("image", img)

for name in images:
    img_path = os.path.join(IMAGE_DIR, name)
    img = cv2.imread(img_path)
    h, w, _ = img.shape

    boxes = []

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", draw)

    print(f"Labeling {name}")
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    label_file = os.path.join(LABEL_DIR, name.replace(".jpg",".txt"))

    with open(label_file, "w") as f:
        for b in boxes:
            x1,y1,x2,y2 = b
            xc = ((x1+x2)/2)/w
            yc = ((y1+y2)/2)/h
            bw = abs(x2-x1)/w
            bh = abs(y2-y1)/h
            f.write(f"{class_id} {xc} {yc} {bw} {bh}\n")

print("DONE")