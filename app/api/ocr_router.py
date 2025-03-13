from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import requests
from app.services.ocr_service import OCRService
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()
ocr_service = OCRService()

@router.post("/image", response_model=Dict[str, Any])
async def extract_image_text(request: Request):
    """从图片中提取文本"""
    try:
        logger.info("开始处理上传的图片数据")
        
        # 读取图片数据
        image_data = await request.body()
        
        # 验证图片数据
        if not image_data:
            logger.error("接收到空的图片数据")
            raise HTTPException(status_code=400, detail="空的图片数据")
            
        try:
            result = await ocr_service.extract_image_text(image_data)
            logger.info("图片处理完成")
            return {"result": result}
        except ValueError as ve:
            logger.error(f"图片数据验证失败: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class PDFRequest(BaseModel):
    pdf_url: str
    page: int = -1

@router.post('/pdf')
async def handle_post_request(request: PDFRequest):
    try:
        pdf_url = request.pdf_url
        page = request.page
        logger.info(f"extract_pdf {pdf_url}")
        
        # 验证PDF URL
        try:
            response = requests.head(pdf_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="无效的PDF URL")
        except requests.RequestException:
            raise HTTPException(status_code=400, detail="无效的PDF URL")
            
        results = await ocr_service.extract_pdf_text(pdf_url, page)
        
        # 验证结果
        if not results:
            if page != -1:
                raise HTTPException(status_code=400, detail="无效的页码")
            else:
                raise HTTPException(status_code=400, detail="PDF处理失败")
                
        # 合并多页文本
        text = "\n".join(results)
        return {"result": text}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF处理失败：{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


