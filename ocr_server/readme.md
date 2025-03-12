## 以4个worker同步方式启动ocr_server
    uvicorn main:app --workers 4 --host 0.0.0.0 --port 6007
    