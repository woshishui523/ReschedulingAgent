"""
列车晚点智能调度系统 - Web API 后端
FastAPI REST API，供前端页面调用
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.database import SessionLocal
from models.dispatch_record import DispatchRecord
from models.delay_record import DelayRecord
from models.train_model import TrainModel
from models.station import Station
from main import dispatch_input_processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="列车晚点智能调度系统 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DispatchRequest(BaseModel):
    text: str


class DispatchResponse(BaseModel):
    success: bool
    command: str
    parsed: dict
    timestamp: str
    diagram_url: Optional[str] = None


@app.post("/api/dispatch", response_model=DispatchResponse)
def api_dispatch(req: DispatchRequest):
    """接收调度员输入，返回调度命令"""
    try:
        from services.unified_dispatch_service import unified_process_delay
        from tools.nlp_parser_tool import parse_dispatch_text

        parsed_data = parse_dispatch_text(req.text)
        if "error" in parsed_data:
            raise ValueError(f"解析失败: {parsed_data['error']}")

        command, diagram_path = unified_process_delay(
            target_train_number=parsed_data["train_number"],
            target_station_name=parsed_data["station_name"],
            delay_minutes=parsed_data["delay_duration"],
            reason_text=parsed_data["delay_reason"],
            original_text=req.text,
        )

        return DispatchResponse(
            success=True,
            command=command,
            parsed=parsed_data,
            timestamp=datetime.now().isoformat(),
            diagram_url=diagram_path if diagram_path else None,
        )
    except Exception as e:
        logger.error(f"调度处理失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
def api_history(limit: int = 20, offset: int = 0):
    """查询历史调度记录"""
    db = SessionLocal()
    try:
        records = (
            db.query(DispatchRecord)
            .order_by(DispatchRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        total = db.query(DispatchRecord).count()

        items = []
        for r in records:
            train = db.query(TrainModel).filter(TrainModel.train_id == r.train_id).first()
            station = db.query(Station).filter(Station.station_id == r.station_id).first()
            items.append({
                "dispatch_id": r.dispatch_id,
                "train_number": train.train_number if train else "未知",
                "station_name": station.station_name if station else "未知",
                "adjustment_value": r.adjustment_value,
                "command_content": r.command_content,
                "created_at": r.created_at.isoformat() if r.created_at else None
            })

        return {"success": True, "total": total, "items": items}
    finally:
        db.close()


@app.get("/api/health")
def api_health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    print(f"静态文件目录: {static_dir}")
    print("启动服务: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
