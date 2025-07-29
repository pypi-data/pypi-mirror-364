# Flowscale SDK FastAPI Example

This example demonstrates how to use the Flowscale Python SDK with FastAPI to create a web API that wraps all Flowscale SDK functionality.

## Features

- **Complete SDK Coverage**: APIs for all Flowscale SDK functions
- **Image Upload Support**: Special endpoint for workflow execution with image uploads
- **Environment Configuration**: Uses environment variables for API credentials
- **Error Handling**: Proper HTTP error responses
- **Interactive Documentation**: Automatic OpenAPI/Swagger documentation

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual Flowscale API credentials
   ```

3. **Run the Server**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Health & Queue Management
- `GET /health` - Check ComfyUI health status
- `GET /queue` - Get workflow queue status

### Workflow Execution
- `POST /execute` - Execute workflow immediately
- `POST /execute_async` - Execute workflow and wait for completion
- `POST /execute_with_image` - Execute workflow with image upload (multipart/form-data)

### Run Management
- `GET /output/{filename}` - Get workflow output by filename
- `POST /cancel` - Cancel a running workflow
- `GET /run/{run_id}` - Get detailed run information
- `GET /runs` - List runs (optionally filter by group_id)

## Usage Examples

### Execute Workflow with JSON Data
```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "your-workflow-id",
    "data": {
      "prompt": "A beautiful sunset",
      "steps": 20
    },
    "group_id": "optional-group-id"
  }'
```

### Execute Workflow with Image Upload
```bash
curl -X POST "http://localhost:8000/execute_with_image" \
  -F "workflow_id=your-workflow-id" \
  -F "image=@/path/to/your/image.jpg" \
  -F "timeout=300" \
  -F "additional_data={\"prompt\": \"Process this image\"}"
```

### Check Health Status
```bash
curl -X GET "http://localhost:8000/health"
```

### Get Workflow Output
```bash
curl -X GET "http://localhost:8000/output/output_filename.jpg"
```

### Cancel a Run
```bash
curl -X POST "http://localhost:8000/cancel" \
  -H "Content-Type: application/json" \
  -d '{"run_id": "your-run-id"}'
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test all endpoints directly from your browser.

## Environment Variables

- `FLOWSCALE_API_KEY`: Your Flowscale API key (required)
- `FLOWSCALE_API_URL`: Your Flowscale API base URL (required)

## Dependencies

- `fastapi>=0.104.0` - Modern web framework for building APIs
- `uvicorn>=0.24.0` - ASGI server for running FastAPI
- `python-multipart>=0.0.6` - For handling file uploads
- `flowscale-sdk>=1.0.0` - The Flowscale Python SDK
- `python-dotenv>=1.0.0` - For loading environment variables from .env file

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `204` - No content (when output is not yet available)
- `500` - Internal server error (with error details)

## Development

To run in development mode with auto-reload:
```bash
uvicorn main:app --reload
```

The server will restart automatically when you make changes to the code.