from app.services.ocr_core import Ocr
import cv2 
file = ""
ocr = Ocr(device="cpu")

image_path = r"app/tests/data/ocr发展史.png"
try:
    # 读取本地图片并进行OCR识别
    cv_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if cv_image is None:                
        print({"error": "无法读取图片，请检查路径是否正确"})
    else:
        open_cv_image = cv_image[:, :, ::-1].copy()
        results = ocr.ocr_mode.extract_text(open_cv_image)
        print({"results": results})
except Exception as e:
    print(f"本地图片OCR失败：\n{e}")
    print({"error": "OCR 失败"})