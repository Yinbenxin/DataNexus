import io
import cv2
import numpy as np
import requests
from pdf2image import convert_from_bytes
from app.utils.logger import logger
from app.services.ocr.ocr_core import OCRQAnything

class OCRService:
    def __init__(self, model_dir='model/ocr_models', device='cpu'):
        try:
            self.ocr_model = OCRQAnything(model_dir=model_dir, device=device)
            logger.info(f"OCR模型加载完成，使用设备: {device}")
        except Exception as e:
            logger.error(f"OCR模型加载失败: {str(e)}")
            raise Exception(f"OCR模型加载失败: {str(e)}")

    async def extract_pdf_text(self, pdf_url: str, page_num: int = -1) -> list:
        """从PDF文件中提取文本

        Args:
            pdf_url: PDF文件的URL
            page_num: 要处理的页码，-1表示处理所有页面

        Returns:
            list: 提取的文本列表，每个元素对应一个页面的文本
        """
        try:
            response = requests.get(pdf_url)
            if response.status_code != 200:
                logger.error(f"PDF下载失败，状态码: {response.status_code}")
                return []

            pdf_file = io.BytesIO(response.content)
            logger.info(f'成功下载PDF: {pdf_url}')
            
            pages = convert_from_bytes(pdf_file.getvalue(), 300)
            texts = []

            if page_num != -1:
                if page_num >= len(pages):
                    logger.error(f"页码 {page_num} 超出PDF页数范围")
                    return []
                page = pages[page_num]
                open_cv_image = np.array(page)
                open_cv_image = open_cv_image[:, :, ::-1].copy()
                text = self.ocr_model.extract_text(open_cv_image)
                texts.append(text)
            else:
                for page in pages:
                    open_cv_image = np.array(page)
                    open_cv_image = open_cv_image[:, :, ::-1].copy()
                    text = self.ocr_model.extract_text(open_cv_image)
                    texts.append(text)

            return texts

        except Exception as e:
            logger.error(f"PDF文本提取失败: {str(e)}")
            raise Exception(f"PDF文本提取失败: {str(e)}")

    async def extract_image_text(self, image_data: bytes) -> str:
        """从图片数据中提取文本

        Args:
            image_data: 图片的二进制数据

        Returns:
            str: 提取的文本

        Raises:
            ValueError: 当图片数据无效或无法解析时
        """
        try:
            if not image_data:
                raise ValueError("空的图片数据")

            # 将图片数据转换为numpy数组
            nparr = np.frombuffer(image_data, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            
            if cv_image is None:
                raise ValueError("无法解析图片数据，请确保上传了有效的图片文件")
                
            if cv_image.shape[-1] == 4:  # RGBA格式
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2BGR)
                
            open_cv_image = cv_image[:, :, ::-1].copy()
            text = self.ocr_model.extract_text(open_cv_image)
            return text

        except ValueError as ve:
            logger.error(f"图片数据验证失败: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"图片文本提取失败: {str(e)}")
            raise Exception(f"图片文本提取失败: {str(e)}")