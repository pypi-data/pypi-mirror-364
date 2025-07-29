import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from flowscale import FlowscaleAPI

load_dotenv()

app = FastAPI(
    title="Flowscale SDK FastAPI Example",
    description="FastAPI server demonstrating all Flowscale SDK functions",
    version="1.0.0"
)

# Initialize Flowscale API client
api_key = os.getenv("FLOWSCALE_API_KEY")
api_url = os.getenv("FLOWSCALE_API_URL")

if not api_key or not api_url:
    raise ValueError("FLOWSCALE_API_KEY and FLOWSCALE_API_URL environment variables are required")

flowscale_client = FlowscaleAPI(api_key=api_key, base_url=api_url)


# Pydantic models for request/response
class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    data: Dict[str, Any]
    group_id: Optional[str] = None


class ExecuteWorkflowAsyncRequest(BaseModel):
    workflow_id: str
    data: Dict[str, Any]
    group_id: Optional[str] = None
    timeout: int = 300
    polling_interval: int = 1


class CancelRunRequest(BaseModel):
    run_id: str


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Flowscale SDK FastAPI Example",
        "endpoints": {
            "health": "/health - Check ComfyUI health status",
            "queue": "/queue - Get workflow queue status",
            "execute": "/execute - Execute workflow immediately",
            "execute_async": "/execute_async - Execute workflow and wait for completion",
            "execute_with_image": "/execute_with_image - Execute workflow with image upload",
            "output": "/output/{filename} - Get workflow output by filename",
            "cancel": "/cancel - Cancel a running workflow",
            "run": "/run/{run_id} - Get run details",
            "runs": "/runs - List all runs (optionally filter by group_id)"
        }
    }


@app.get("/health")
async def check_health():
    """Check the health status of all ComfyUI instances"""
    try:
        health_status = flowscale_client.check_health()
        return JSONResponse(content=health_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/queue")
async def get_queue():
    """Get the queue data for all ComfyUI instances"""
    try:
        queue_data = flowscale_client.get_queue()
        return JSONResponse(content=queue_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
async def execute_workflow(request: ExecuteWorkflowRequest):
    """Execute a workflow immediately"""
    try:
        result = flowscale_client.execute_workflow(
            workflow_id=request.workflow_id,
            data=request.data,
            group_id=request.group_id
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute_async")
async def execute_workflow_async(request: ExecuteWorkflowAsyncRequest):
    """Execute a workflow and wait for completion"""
    try:
        result = flowscale_client.execute_workflow_async(
            workflow_id=request.workflow_id,
            data=request.data,
            group_id=request.group_id,
            timeout=request.timeout,
            polling_interval=request.polling_interval
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute_with_image")
async def execute_workflow_with_image(
    workflow_id: str = Form(...),
    image: UploadFile = File(...),
    group_id: Optional[str] = Form(None),
    timeout: int = Form(300),
    polling_interval: int = Form(1),
    additional_data: Optional[str] = Form("{}")
):
    """Execute a workflow with image upload and wait for completion"""
    try:
        # Parse additional data if provided
        import json
        extra_data = json.loads(additional_data) if additional_data else {}
        
        # Create data dictionary with uploaded image
        data = {
            "image": image.file,
            **extra_data
        }
        
        result = flowscale_client.execute_workflow_async(
            workflow_id=workflow_id,
            data=data,
            group_id=group_id,
            timeout=timeout,
            polling_interval=polling_interval
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/output/{filename}")
async def get_output(filename: str):
    """Get workflow output by filename"""
    try:
        output = flowscale_client.get_output(filename)
        if output is None:
            raise HTTPException(status_code=204, detail="No output found")
        return JSONResponse(content=output)
    except Exception as e:
        if "No output found" in str(e):
            raise HTTPException(status_code=204, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cancel")
async def cancel_run(request: CancelRunRequest):
    """Cancel a running workflow"""
    try:
        result = flowscale_client.cancel_run(request.run_id)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/run/{run_id}")
async def get_run(run_id: str):
    """Get detailed information about a specific run"""
    try:
        run_details = flowscale_client.get_run(run_id)
        return JSONResponse(content=run_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/runs")
async def get_runs(group_id: Optional[str] = None):
    """Get list of runs, optionally filtered by group_id"""
    try:
        runs = flowscale_client.get_runs(group_id=group_id)
        return JSONResponse(content=runs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8989)