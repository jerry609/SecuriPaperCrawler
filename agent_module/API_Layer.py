from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
from datetime import datetime


class AnalysisRequest(BaseModel):
    paper_url: HttpUrl
    analysis_config: Optional[Dict[str, any]] = None
    priority: Optional[str] = "medium"


class AnalysisResponse(BaseModel):
    task_id: str
    status: str
    created_at: datetime
    estimated_completion_time: Optional[datetime]


class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    results: Optional[Dict[str, any]]
    error: Optional[str]


app = FastAPI(title="Paper Code Analysis API")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化工作流协调器
workflow_coordinator = WorkflowCoordinator()


@app.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(
        request: AnalysisRequest,
        background_tasks: BackgroundTasks
):
    """启动论文分析任务"""
    try:
        # 验证输入
        if not request.paper_url:
            raise HTTPException(status_code=400, detail="Paper URL is required")

        # 创建默认配置
        config = request.analysis_config or {}

        # 启动分析任务
        task_id = await workflow_coordinator.process_paper(
            str(request.paper_url),
            config
        )

        return AnalysisResponse(
            task_id=task_id,
            status="accepted",
            created_at=datetime.now(),
            estimated_completion_time=datetime.now() + timedelta(minutes=30)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        status = await workflow_coordinator.get_task_status(task_id)
        if status.get('status') == 'not_found':
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """取消任务"""
    try:
        success = await workflow_coordinator.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or already completed")
        return {"message": "Task cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{task_id}")
async def get_results(task_id: str):
    """获取分析结果"""
    try:
        status = await workflow_coordinator.get_task_status(task_id)
        if status.get('status') == 'not_found':
            raise HTTPException(status_code=404, detail="Results not found")
        if status.get('status') != 'completed':
            raise HTTPException(status_code=400, detail="Analysis not yet completed")
        return status.get('results')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }


# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "error": str(exc),
        "timestamp": datetime.now(),
        "path": request.url.path
    }