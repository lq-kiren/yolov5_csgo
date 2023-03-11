import ctypes
import time
from threading import Thread

import win32api
import win32con
import pynput
import csv
PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

def lock(aims, mouse, x, y, k=5):
    """
    aims : yolo输出的5个参数 （标签值， 中心点x轴坐标， 中心点y轴坐标， bbox长， bbox宽）的列表
    mouse: pynput mouse对象
    x: 屏幕长
    y: 屏幕宽
    k: 优先瞄头参数
    """
    mouse_pos_x, mouse_pos_y = mouse.position
    dist_list = []

    for det in aims:
        tag, x_c, y_c, _, _ = det

        #   优先瞄准头部
        #   将身子的dist*k
        dist = (x*float(x_c)-mouse_pos_x)**2 + (y*float(y_c) - mouse_pos_y)**2
        if tag == 0 or tag == 2:
            dist *= k
        dist_list.append(dist)

    det = aims[dist_list.index(min(dist_list))]

    tag, x_center, y_center, width, height = det

    tag = int(tag)
    x_center, width = x*float(x_center), x*float(width)
    y_center, height = y*float(y_center), y*float(height)

    re_x = x_center - x/2
    re_y = y_center - y/2

    if tag == 0 or tag == 2:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(re_x), int(re_y))
        # mouse.position = (int(x_center), int(y_center))
    elif tag == 1 or tag == 3:
        #   打身体要向上偏移一点
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(re_x), int(re_y-1/6*height))
        # mouse.position = (int(x_center), int(y_center - 1 / 6 * height))

# def recoil_control():
#     ak47_recoil = []
#     recoil_mode = False
#     k = -1
#
#     mouse = pynput.mouse.Controller()
#     #是否开枪（按下左键）
#     flag = 0
#
#     for i in csv.reader(open(r'E:\python\pycharm\project\yolov5_csgo\aim_csgo\model\ak47.csv', encoding='utf-8-sig')):
#         ak47_recoil.append([float(x) for x in i])
#
#     with pynput.mouse.Events() as events:
#         for event in events:
#             if isinstance(event, pynput.mouse.Events.Click):
#                 if event.button == event.button.left:
#                     if event.pressed:
#                         flag = 1
#                     else:
#                         flag = 0
#                 if event.button == event.button.x2 and event.pressed:
#                     recoil_mode = not recoil_mode
#                     print('recoil mode', 'on' if recoil_mode else 'off')
#
#             if flag and recoil_mode:
#                 i = 0
#                 a = next(events)
#                 while True:
#                     print("i:", i)
#                     mouse.move(int(-ak47_recoil[i][0] * k), int(ak47_recoil[i][1] * k))
#
#                     i += 1
#                     if i == 30:
#                         break
#                     # if event is not None and isinstance(event, pynput.mouse.Events.Click) and event.button == event.button.left and not event.pressed:
#                     if event is not None and isinstance(event, pynput.mouse.Events.Click) and event.button == event.button.left and not event.pressed:
#                         print("in")
#                         break
#                     while event is not None and not isinstance(a, pynput.mouse.Events.Click):
#                         a = next(events)
#                     time.sleep(ak47_recoil[i][2] / 1000 - 0.01)
#                 flag = 0
#
# #
# t = Thread(target=recoil_control)
# t.start()
# t.join()
#
