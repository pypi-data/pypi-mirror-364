# Flowscale Python SDK

A comprehensive Python SDK designed to simplify interaction with the FlowScale ComfyUI API. This library abstracts away the complexities of API calls, enabling you to effortlessly invoke workflows, retrieve outputs, manage workflow runs, and monitor system health.

## 🚀 What's New in v1.1.2

- **📚 Comprehensive Documentation**: Completely updated README with advanced usage examples
- **✨ Enhanced `get_runs()`**: Pagination, sorting, and filtering with detailed examples
- **🖼️ Dynamic Image Parameters**: Support for dynamic parameter names (e.g., `image_35728`)
- **📤 Multiple Image Uploads**: Handle multiple images in a single workflow execution
- **🔧 Improved File Handling**: Better support for various file types and upload methods
- **📊 Updated Response Types**: New response structure with comprehensive metadata

---

## Installation

Install the Flowscale SDK using pip:

```bash
pip install flowscale
```

---

## Quick Start

### Importing the SDK

To get started, import the Flowscale SDK into your project:

```python
from flowscale import FlowscaleAPI
import os

# Initialize the SDK
api_key = os.environ.get("FLOWSCALE_API_KEY")
api_url = os.environ.get("FLOWSCALE_API_URL")

if not api_key or not api_url:
    print("FLOWSCALE_API_KEY or FLOWSCALE_API_URL not set in environment")
    exit(1)

flowscale = FlowscaleAPI(api_key, api_url)
```

**Environment Variables:** Add the following to your `.env` file:

```plaintext
FLOWSCALE_API_KEY=your-api-key
FLOWSCALE_API_URL=https://your-api-url.pod.flowscale.ai
```

---

## SDK Methods

Below is a detailed guide to the SDK methods, including descriptions, usage, and response formats.

### 1. `check_health()`

**Description:**
Check the health status of the Flowscale platform, including the status of containers and services.

**Usage:**
```python
health = flowscale.check_health()
print(f"API Health: {health}")
```

**Response Example:**
```json
{
  "status": "success",
  "data": [
    {
      "container": "container #1",
      "status": "idle"
    },
    {
      "container": "container #2",
      "status": "running"
    }
  ]
}
```

---

### 2. `get_queue()`

**Description:**
Retrieve the current status of the workflow queue, including running and pending jobs.

**Usage:**
```python
queue = flowscale.get_queue()
print(f"Queue Details: {queue}")
```

**Response Example:**
```json
{
  "status": "success",
  "data": [
    {
      "container": "container #1",
      "queue": {
        "queue_running": [
          [
            0,
            "2a0babc4-acce-4521-9576-00fa0e6ecc91"
          ]
        ],
        "queue_pending": [
          [
            1,
            "5d60718a-7e89-4c64-b32d-0d1366b44e2a"
          ]
        ]
      }
    }
  ]
}
```

---

### 3. `execute_workflow(workflow_id, data, group_id=None)`

**Description:**
Trigger a workflow execution using its unique `workflow_id`. Input data and an optional `group_id` can be provided for better organization and tracking.

**Parameters:**
- `workflow_id` *(string)*: The unique ID of the workflow.
- `data` *(object)*: Input parameters for the workflow.
- `group_id` *(string, optional)*: A custom identifier for grouping runs.

**Usage:**
```python
workflow_id = "bncu0a1kipv"
group_id = "test_group"

# Basic usage with text inputs
inputs = {
   "text_51536": "Prompt test",
   "another_param": "some value"
}

# Advanced usage with files and dynamic parameters
inputs = {
   "text_51536": "Prompt test",
   "image_35728": open("path/to/image.png", "rb"),  # File object
   "image_42561": "path/to/another_image.jpg",      # File path (auto-detected)
   "video_1239": open("path/to/video.mp4", "rb")   # Multiple file types
}

result = flowscale.execute_workflow(workflow_id, inputs, group_id)
print(f"Workflow Result: {result}")
```

**Dynamic Parameter Names:**
The SDK now supports dynamic parameter names that match your workflow's requirements:

```python
# Example with ComfyUI dynamic parameter names
inputs = {
    "image_35728": open("input.png", "rb"),      # Dynamic image parameter
    "image_42561": "path/to/second_image.jpg",   # Another dynamic image
    "text_input_123": "Your prompt here",        # Dynamic text parameter
    "seed_456": 12345                            # Dynamic numeric parameter
}
```

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "number": 0,
    "node_errors": {},
    "output_names": [
      "filename_prefix_58358_5WWF7GQUYF"
    ],
    "run_id": "808f34d0-ef97-4b78-a00f-1268077ea6db"
  }
}
```

---

### 3a. `execute_workflow_async(workflow_id, data, group_id=None, timeout=300, polling_interval=1)`

**Description:**
Execute a workflow and automatically poll for its output until completion or timeout. This is a convenience method that combines `execute_workflow` and `get_output` with polling logic.

**Parameters:**
- `workflow_id` *(string)*: The unique ID of the workflow
- `data` *(object)*: Input parameters for the workflow
- `group_id` *(string, optional)*: A custom identifier for grouping runs
- `timeout` *(int, optional)*: Maximum time to wait for results in seconds (default: 300)
- `polling_interval` *(int, optional)*: Time between polling attempts in seconds (default: 1)

**Usage:**
```python
workflow_id = "bncu0a1kipv"

# Simple usage
inputs = {
   "text_51536": "Prompt test",
   "image_1234": open("path/to/image.png", "rb")
}

# This will wait for the output, up to 5 minutes by default
result = flowscale.execute_workflow_async(workflow_id, inputs)
print(f"Workflow Result: {result}")

# With custom timeout and polling interval
result = flowscale.execute_workflow_async(
    workflow_id, 
    inputs,
    timeout=600,  # 10 minutes
    polling_interval=5  # Check every 5 seconds
)

# With multiple dynamic image parameters
inputs = {
    "prompt_text": "A beautiful landscape",
    "image_35728": open("reference1.png", "rb"),
    "image_42561": open("reference2.jpg", "rb"),
    "style_image_789": "path/to/style.png"
}

result = flowscale.execute_workflow_async(workflow_id, inputs, group_id="batch_001")
```

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "download_url": "https://runs.s3.amazonaws.com/generations/...",
    "generation_status": "success"
  }
}
```

**Note:** If the workflow doesn't complete within the timeout period, an exception will be raised.

---

### 4. `get_output(filename)`

**Description:**
Fetch the output of a completed workflow using its `filename`. Outputs typically include downloadable files or results.

**Parameters:**
- `filename` *(string)*: The name of the output file.

**Usage:**
```python
output = flowscale.get_output("filename_prefix_58358_5WWF7GQUYF.png")
print(f"Workflow Output: {output}")
```

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "download_url": "https://runs.s3.amazonaws.com/generations/...",
    "generation_status": "success"
  }
}
```

---

### 5. `cancel_run(run_id)`

**Description:**
Cancel a running workflow execution using its unique `run_id`.

**Parameters:**
- `run_id` *(string)*: The unique identifier of the running workflow.

**Usage:**
```python
result = flowscale.cancel_run("808f34d0-ef97-4b78-a00f-1268077ea6db")
print(f"Cancellation Result: {result}")
```

**Response Example:**
```json
{
  "status": "success",
  "data": "Run cancelled successfully"
}
```

---

### 6. `get_run(run_id)`

**Description:**
Retrieve detailed information about a specific workflow run.

**Parameters:**
- `run_id` *(string)*: The unique identifier of the run.

**Usage:**
```python
run_details = flowscale.get_run("808f34d0-ef97-4b78-a00f-1268077ea6db")
print(f"Run Details: {run_details}")
```

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "_id": "808f34d0-ef97-4b78-a00f-1268077ea6db",
    "status": "completed",
    "inputs": [
      {
        "path": "text_51536",
        "value": "a man riding a bike"
      }
    ],
    "outputs": [
      {
        "filename": "filename_prefix_58358_5WWF7GQUYF.png",
        "url": "https://runs.s3.amazonaws.com/generations/..."
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "started_at": "2024-01-15T10:30:15Z",
    "completed_at": "2024-01-15T10:32:45Z"
  }
}
```

---

### 7. `get_runs()` - ✨ Enhanced with Pagination & Sorting

**Description:**
Retrieve workflow runs with advanced pagination, sorting, and filtering capabilities. This method now supports comprehensive run management with metadata.

**Parameters:**
- `group_id` *(string, optional)*: Filter runs by group identifier
- `sort_by` *(string, optional)*: Field to sort by - `"created_at"`, `"started_at"`, or `"completed_at"` (default: `"created_at"`)
- `sort_order` *(string, optional)*: Sort order - `"asc"` or `"desc"` (default: `"desc"`)
- `page` *(int, optional)*: Page number starting from 1 (default: `1`)
- `page_size` *(int, optional)*: Number of items per page, 1-100 (default: `10`)

**Usage Examples:**

```python
# Basic usage - get recent runs
runs = flowscale.get_runs()
print(f"Recent Runs: {runs}")

# Filter by group
group_runs = flowscale.get_runs(group_id="test_group")
print(f"Group Runs: {group_runs}")

# Pagination with custom page size
paginated_runs = flowscale.get_runs(page=2, page_size=20)
print(f"Page 2 Runs: {paginated_runs}")

# Sort by completion time (oldest first)
completed_runs = flowscale.get_runs(
    sort_by="completed_at", 
    sort_order="asc",
    page_size=50
)

# Advanced filtering and sorting
filtered_runs = flowscale.get_runs(
    group_id="production_batch",
    sort_by="started_at",
    sort_order="desc",
    page=1,
    page_size=25
)
```

**New Response Format with Metadata:**
```json
{
  "status": "success",
  "meta": {
    "sort_by": "created_at",
    "sort_order": "desc",
    "page": 1,
    "group_id": "test_group",
    "page_size": 10,
    "total_count": 156,
    "total_pages": 16
  },
  "data": {
    "runs": [
      {
        "_id": "cc29a72d-75b9-4c7b-b991-ccaf2a04d6ea",
        "team_id": "team_123",
        "workflow_id": "bncu0a1kipv",
        "group_id": "test_group",
        "status": "completed",
        "inputs": [
          {
            "path": "text_51536",
            "value": "a man riding a bike",
            "s3_key": null,
            "url": null
          }
        ],
        "outputs": [
          {
            "filename": "filename_prefix_58358_G3DRLIVVYP.png",
            "s3_key": "generations/...",
            "url": "https://runs.s3.amazonaws.com/generations/..."
          }
        ],
        "created_at": "2024-01-15T10:30:00Z",
        "started_at": "2024-01-15T10:30:15Z",
        "completed_at": "2024-01-15T10:32:45Z"
      }
    ]
  }
}
```

**Pagination Helper:**
```python
def get_all_runs(group_id=None, sort_by="created_at"):
    """Example function to get all runs across multiple pages"""
    all_runs = []
    page = 1
    
    while True:
        response = flowscale.get_runs(
            group_id=group_id,
            sort_by=sort_by,
            page=page,
            page_size=100  # Max page size
        )
        
        runs = response["data"]["runs"]
        all_runs.extend(runs)
        
        # Check if we've reached the last page
        if page >= response["meta"]["total_pages"]:
            break
            
        page += 1
    
    return all_runs
```

---

## Advanced Usage Examples

### Working with Multiple File Types

```python
# Handle various file inputs
inputs = {
    "text_prompt": "Generate an image",
    "reference_image_1": open("ref1.png", "rb"),     # File object
    "reference_image_2": "/path/to/ref2.jpg",        # File path  
    "style_image_789": open("style.png", "rb"),      # Dynamic parameter name
    "mask_image_456": "mask.png",                    # Another file path
    "config_json": {"strength": 0.8, "steps": 20}   # JSON data
}

result = flowscale.execute_workflow_async("workflow_id", inputs)
```

### Batch Processing with Groups

```python
import time
from pathlib import Path

def process_image_batch(image_folder, workflow_id):
    """Process multiple images in batches with grouping"""
    image_files = list(Path(image_folder).glob("*.{png,jpg,jpeg}"))
    group_id = f"batch_{int(time.time())}"
    
    results = []
    for i, image_path in enumerate(image_files):
        inputs = {
            "input_image": str(image_path),
            "prompt": f"Process image {i+1}",
            "batch_index": i
        }
        
        result = flowscale.execute_workflow_async(
            workflow_id, 
            inputs, 
            group_id=group_id
        )
        results.append(result)
        
    # Get all results for this batch
    batch_runs = flowscale.get_runs(group_id=group_id, page_size=100)
    return batch_runs
```

### Error Handling and Retries

```python
import time

def robust_workflow_execution(workflow_id, inputs, max_retries=3):
    """Execute workflow with retry logic"""
    for attempt in range(max_retries):
        try:
            result = flowscale.execute_workflow_async(
                workflow_id, 
                inputs,
                timeout=600,  # 10 minutes
                polling_interval=2
            )
            return result
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

---

## FastAPI Integration Example

The SDK includes a complete FastAPI server example that demonstrates all functionality:

```python
from fastapi import FastAPI, UploadFile, File, Form
from flowscale import FlowscaleAPI

app = FastAPI()
flowscale = FlowscaleAPI(api_key, api_url)

@app.post("/execute_with_images")
async def execute_with_multiple_images(
    workflow_id: str = Form(...),
    image_35728: UploadFile = File(...),      # Dynamic parameter names
    image_42561: UploadFile = File(...),      # Multiple images supported
    text_prompt: str = Form("default prompt"),
    group_id: str = Form(None)
):
    """Execute workflow with multiple dynamic image parameters"""
    data = {
        "image_35728": image_35728.file,
        "image_42561": image_42561.file,
        "text_prompt": text_prompt
    }
    
    result = flowscale.execute_workflow_async(workflow_id, data, group_id)
    return result

@app.get("/runs")
async def get_runs_paginated(
    group_id: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 10
):
    """Get paginated runs with sorting"""
    return flowscale.get_runs(group_id, sort_by, sort_order, page, page_size)
```

---

## Best Practices

### Environment Configuration
- Always store sensitive information such as API keys in environment variables.
- Use `.env` files and libraries like `python-dotenv` for easy environment management.

### File Handling
- **File Objects**: Use `open("file.png", "rb")` for direct file uploads
- **File Paths**: Pass string paths for automatic file detection and opening
- **Dynamic Parameters**: Match parameter names exactly as defined in your ComfyUI workflow
- **Multiple Files**: The SDK handles multiple file uploads seamlessly

### Error Handling
- Wrap API calls in try-catch blocks to handle errors gracefully.
- Implement retry logic for network-related failures.
- Log errors for debugging and improve resilience.

### Performance Optimization
- Use `execute_workflow_async()` for long-running workflows
- Implement proper pagination when fetching large numbers of runs
- Use appropriate polling intervals based on expected workflow duration
- Group related runs for better organization and batch processing

### Testing and Debugging
- Test workflows in a development environment before deploying to production.
- Validate inputs to ensure they match the workflow requirements.
- Use the health check and queue status methods to monitor system status.

---

## Changelog

### v1.1.2 (Latest)
- ✨ **Enhanced `get_runs()`** with pagination, sorting, and filtering

### v1.1.0
- ✨ **Dynamic Image Parameters** support for flexible workflow inputs
- ✨ **Multiple Image Uploads** in single workflow execution
- 🔧 **Improved File Handling** with better error handling and type detection
- 📝 **Updated Response Types** with comprehensive metadata
- 🐛 **Fixed** async file upload issues in FastAPI examples
- 📚 **Enhanced Documentation** with advanced usage examples

### v1.0.0
- Initial release with core functionality
- Basic workflow execution and management
- Health monitoring and queue status

---

## Support

For any questions or assistance:
- Join the Flowscale community on **Discord**
- Refer to the [Flowscale Documentation](https://docs.flowscale.ai/)
- Submit issues on [GitHub](https://github.com/flowscale/flowscale-python)

---

**Simplify your workflow management with the Flowscale Python SDK. Happy coding! 🚀**