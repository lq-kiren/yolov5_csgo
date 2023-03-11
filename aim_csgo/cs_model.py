import torch
from models.common import DetectMultiBackend

device = torch.device('cuda') if torch.cuda.is_available() else 'cpu'

weights = r'E:\python\pycharm\project\yolov5_csgo\Include\aim_csgo\model\best.pt'
imgsz = (416, 416)

def load_model():

    model = DetectMultiBackend(weights, device=device, dnn=False, data=r'E:\python\pycharm\project\yolov5_csgo\Include\aim_csgo\model\cs_dataset.yaml', fp16=False)
    model.warmup(imgsz=(1 if model.pt or model.triton else 1, 3, *imgsz))  # warmup
    return model
