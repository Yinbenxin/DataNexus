import cv2
import numpy as np
from PIL import Image
from app.utils.logger import logger
import time
class OCRQAnything:
    def __init__(self, model_dir='model/ocr_models', device='cpu'):
        try:
            self.device = device
            self.text_detector = TextDetector(model_dir, device)
            self.text_recognizer = TextRecognizer(model_dir, device)
            self.drop_score = 0.5
            self.crop_image_res_index = 0
            import onnxruntime as ort
            self.det_model = ort.InferenceSession(f"{model_dir}/det.onnx", providers=['CPUExecutionProvider'] if device == 'cpu' else ['CUDAExecutionProvider'])
            self.rec_model = ort.InferenceSession(f"{model_dir}/rec.onnx", providers=['CPUExecutionProvider'] if device == 'cpu' else ['CUDAExecutionProvider'])
            
            # 加载字典文件
            with open(f"{model_dir}/ocr.res", 'r', encoding='utf-8') as f:
                self.character = [line.strip('\n') for line in f.readlines()]
            
            logger.info("OCR模型加载成功")
        except Exception as e:
            logger.error(f"OCR模型加载失败: {str(e)}")
            raise
    
    def preprocess(self, img):
        # 图像预处理
        if isinstance(img, str):
            img = cv2.imread(img)
        elif isinstance(img, np.ndarray):
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif len(img.shape) == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        h, w = img.shape[:2]
        scale = min(1024 / w, 1024 / h)
        nw, nh = int(scale * w), int(scale * h)
        img = cv2.resize(img, (nw, nh))
        
        # 归一化
        img = img.astype('float32')
        img = img / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype='float32')
        std = np.array([0.229, 0.224, 0.225], dtype='float32')
        img = (img - mean) / std
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        img = img.astype('float32')
        
        return img
    
    def detect(self, img):
        # 文本检测
        h, w = img.shape[2:]  # NCHW格式
        ort_inputs = {self.det_model.get_inputs()[0].name: img}
        ort_outs = self.det_model.run(None, ort_inputs)
        pred = ort_outs[0][0]
        
        # 后处理获取文本框
        pred = 1 / (1 + np.exp(-pred))
        pred = pred > 0.3
        
        # 获取连通区域
        contours, _ = cv2.findContours((pred * 255).astype(np.uint8), 
                                     cv2.RETR_LIST, 
                                     cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for cnt in contours:
            if cv2.contourArea(cnt) < 100:  # 过滤小面积区域
                continue
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            boxes.append(box)
        
        return boxes
    
    def recognize(self, img, box):
        # 获取文本区域
        h, w = img.shape[2:]  # NCHW格式
        box = np.array(box)
        box = box.astype(np.float32)
        box[:, 0] = np.clip(box[:, 0], 0, w - 1)
        box[:, 1] = np.clip(box[:, 1], 0, h - 1)
        
        # 透视变换
        src_pts = box.astype("float32")
        dst_pts = np.array([[0, 0], [192, 0], [192, 48], [0, 48]], dtype="float32")
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(img[0].transpose(1, 2, 0), M, (192, 48))
        
        # 预处理识别区域
        warped = (warped * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])) * 255
        warped = warped.astype(np.uint8)
        warped = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY)
        warped = warped.astype('float32') / 255.0
        warped = np.expand_dims(warped, axis=0)
        warped = np.expand_dims(warped, axis=0)
        
        # 文本识别
        ort_inputs = {self.rec_model.get_inputs()[0].name: warped}
        ort_outs = self.rec_model.run(None, ort_inputs)
        pred = ort_outs[0][0]
        
        # 解码获取文本
        pred_index = pred.argmax(axis=1)
        text = ''
        for idx in pred_index:
            if idx > 0 and (not (len(text) > 0 and idx == pred_index[len(text)-1])):
                text += self.character[idx]
        
        return text
    
    def extract_text(self, img):
        # 主处理函数
        try:
            time_dict = {'det': 0, 'rec': 0, 'cls': 0, 'all': 0}

            if img is None:
                return None, None, time_dict

            start = time.time()
            ori_im = img.copy()
            # print(img.shape)
            dt_boxes, elapse = self.text_detector(img)
            time_dict['det'] = elapse

            if dt_boxes is None:
                end = time.time()
                time_dict['all'] = end - start
                return None, None, time_dict
            # else:
            #     cron_logger.debug("dt_boxes num : {}, elapsed : {}".format(
            #         len(dt_boxes), elapse))
            img_crop_list = []

            dt_boxes = self.sorted_boxes(dt_boxes)

            for bno in range(len(dt_boxes)):
                tmp_box = copy.deepcopy(dt_boxes[bno])
                img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
                img_crop_list.append(img_crop)

            rec_res, elapse = self.text_recognizer(img_crop_list)

            time_dict['rec'] = elapse
            # cron_logger.debug("rec_res num  : {}, elapsed : {}".format(
            #     len(rec_res), elapse))

            filter_boxes, filter_rec_res = [], []
            texts = ""
            for box, rec_result in zip(dt_boxes, rec_res):
                text, score = rec_result
                if score >= self.drop_score:
                    filter_boxes.append(box)
                    filter_rec_res.append(rec_result)
                    text+= "\n"
                    texts += text
            end = time.time()
            time_dict['all'] = end - start
            print(f"time used: {time_dict}")
            return texts
        except Exception as e:
            logger.error(f"文本提取失败: {str(e)}")
            raise