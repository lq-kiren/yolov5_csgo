import cv2.cv2 as cv2
import win32con
import win32gui
import torch
from aim_csgo.cs_model import load_model
from aim_csgo.grap_screen import grab_screen_mss, get_parameters
from utils.general import non_max_suppression, scale_boxes, xyxy2xywh
from utils.augmentations import letterbox
from aim_csgo.aim_lock import lock
import numpy as np
import pynput


x, y = get_parameters()[2], get_parameters()[3]
imgsize = 416

mouse = pynput.mouse.Controller()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = load_model()
stride, names, pt = model.stride, model.names, model.pt
lock_mode = False


#添加鼠标监听事件
def on_click(x, y, button, pressed):
    global lock_mode
    if pressed and button == button.x1:
        lock_mode = not lock_mode
        print("lock mode:", 'on' if lock_mode else 'off')

listener = pynput.mouse.Listener(on_click = on_click)
listener.start()


while True:
    im0 = grab_screen_mss(get_parameters())
    im0 = cv2.resize(im0, (x, y))

    # print(img.shape)
    img = letterbox(im0, imgsize, stride=stride, auto=pt)[0]  # padded resize
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)  # contiguous
    img = torch.from_numpy(img).to(device)
    img = img.half() if model.fp16 else img.float()
    img /= 255.
    if len(img.shape) == 3:
        img = img[None]
    pred = model(img, augment=False, visualize=False)
    pred = non_max_suppression(pred, 0.6, 0.05)

    aims = []
    for i, det in enumerate(pred):
        gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]

        if len(det):
            det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], im0.shape).round()

            for *xyxy, conf, cls in reversed(det):
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                line = (cls, *xywh)  # label format
                aim =  ('%g ' * len(line)).rstrip() % line
                aim = aim.split(' ')
                aims.append(aim)

        if len(aims):
            if lock_mode:
                lock(aims, mouse, x, y, 80)
            for i, det in enumerate(aims):
                _, x_center, y_center, width, height = det
                x_center, width = x * float(x_center), x * float(width)
                y_center, height = y * float(y_center), y * float(height)
                top_left = (int(x_center - width / 2.), int(y_center - height / 2.))
                bottom_right = (int(x_center + width / 2.), int(y_center + height / 2.))
                color = (0, 255, 0)
                cv2.rectangle(im0, top_left, bottom_right, color, thickness=3)

    cv2.namedWindow('csgo-detect', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('csgo-detect', x//3, y//3)
    cv2.imshow('csgo-detect', im0)

    #让窗口处在置顶状态
    hwnd = win32gui.FindWindow(None, 'csgo-detect')
    CVRECT = cv2.getWindowImageRect('csgo-detect')
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
