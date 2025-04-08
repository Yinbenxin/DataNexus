from app.services.ocr.ocr_core import Ocr
import cv2
import os

ocr = Ocr(device="cpu")

image_path = r"/Users/yinbenxin/Desktop/ocr"
out_path = r"/Users/yinbenxin/Desktop/out"

def ocr_image(image_path, out_path, image_name):
    try:
        # 读取本地图片并进行OCR识别
        image_file = os.path.join(image_path, image_name)
        cv_image = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
        if cv_image is None:
            print({"error": f"无法读取图片 {image_name}，请检查路径是否正确"})
            return False
        
        open_cv_image = cv_image[:, :, ::-1].copy()
        results = ocr.ocr_mode.extract_text(open_cv_image)
        
        # 将OCR结果保存为txt文件
        txt_name = os.path.splitext(image_name)[0] + '.txt'
        txt_path = os.path.join(out_path, txt_name)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(str(results) + "\n")
        print({"results": f"OCR成功处理图片：{image_name}"})
        return True
    except Exception as e:
        print(f"处理图片 {image_name} 失败：\n{e}")
        print({"error": "OCR 失败"})
        return False

def process_directory(image_path, out_path):
    # 确保输出目录存在
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    
    # 获取所有图片文件
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    success_count = 0
    failed_count = 0
    
    for filename in os.listdir(image_path):
        if filename.lower().endswith(image_extensions):
            if ocr_image(image_path, out_path, filename):
                success_count += 1
            else:
                failed_count += 1
    
    print(f"\n处理完成！成功：{success_count}个文件，失败：{failed_count}个文件")

# 执行批量处理
process_directory(image_path, out_path)