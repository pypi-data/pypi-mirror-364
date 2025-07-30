# Taskflow SDK

Simple Python SDK for the Taskflow distributed task runner platform.

## 🚀 Quick Start

### Using the SDK

```python
from orkera import OrkeraClient
from datetime import datetime, timedelta

# Initialize client (API URL is automatically set to https://api.orkera.com)
client = OrkeraClient(
    api_key="vgBSGW6A1zYDNHVIPB1Ctry2rR8DOCvg"
)

# Schedule a task
task_id = client.schedule_task(
    task_name="calculate_sum",
    task_kwargs={"a": 10, "b": 20},
    timeout=300
)

print(f"Task scheduled: {task_id}")

# List all tasks
tasks = client.list_tasks()
print(f"Total tasks: {len(tasks)}")

# Get specific task
task = client.get_task(task_id)
print(f"Task status: {task['status']}")
```

### Using Raw HTTP Requests

```python
import requests

response = requests.post(
    "http://localhost:8000/api/tasks/",
    json={
        "task_name": "calculate_sum",
        "task_kwargs": {"a": 10, "b": 20},
        "timeout": 300
    },
    headers={
        "Authorization": "Bearer vgBSGW6A1zYDNHVIPB1Ctry2rR8DOCvg",
        "Content-Type": "application/json"
    }
)

task_id = response.json()["task_id"]
print(f"Task scheduled: {task_id}")
```

## 📦 Installation

### Install from source
```bash
pip install -e .
```

### Install dependencies only
```bash
pip install -r requirements.txt
```

## 🔧 Usage

### SDK Client

The `OrkeraClient` provides a clean interface for interacting with the Orkera server:

```python
from orkera import OrkeraClient

client = OrkeraClient("your-api-key")

# Schedule immediate task
task_id = client.schedule_task("my_task", task_kwargs={"param": "value"})

# Schedule delayed task
from datetime import datetime, timedelta
future_time = datetime.now() + timedelta(minutes=5)
task_id = client.schedule_task("my_task", schedule_time=future_time)

# Schedule with callback
task_id = client.schedule_task(
    "my_task", 
    callback_url="http://myserver.com/webhook"
)
```

### FastAPI Example

Run the included FastAPI example:

```bash
python examples/rest_example.py
```

This starts a server on port 8080 with endpoints:
- `GET /` - API documentation
- `POST /schedule` - Schedule a test task
- `GET /status` - Check server status

## 📝 Examples

The `examples/` directory contains:
- `rest_example.py` - Complete FastAPI server showing task scheduling

## 🔐 Requirements

- Python 3.7+
- `requests>=2.25.0`
- `fastapi>=0.68.0` (for examples)
- `uvicorn>=0.15.0` (for examples)

## 🚨 Server Setup

Make sure your Django Taskflow server is running on `http://localhost:8000` with a valid API key.

## API Reference

### TaskflowClient

#### `__init__(server_url, api_key, timeout=30)`
Initialize the client with server URL and API key.

#### `schedule_task(task_name, task_args=None, task_kwargs=None, schedule_time=None, timeout=300, retry_count=0, callback_url=None)`
Schedule a task for execution.

#### `list_tasks()`
List all tasks for the authenticated user.

#### `get_task(task_id)`
Get details of a specific task.