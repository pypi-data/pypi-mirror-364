
import functools
import time
import requests
import json
from datetime import datetime
from typing import Any, Dict, Callable
import hashlib
import inspect
import base64
import io
from PIL import Image

# Configure the base URL for your API
API_BASE_URL = "https://unscale.replit.app/api"


def trace(project_id: str, function_name: str = None):
    """
    Decorator to automatically trace function calls and log them to the API.
    
    Args:
        project_id: The project ID to log traces to
        function_name: Optional custom function name (defaults to actual function name)
    """

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate trace ID and function info
            trace_id = f"trace_{int(time.time() * 1000)}_{hash(str(args) + str(kwargs)) % 10000}"
            actual_function_name = function_name or func.__name__

            # Get function hash and code snippet based on source code
            try:
                source = inspect.getsource(func)
                function_hash = hashlib.md5(source.encode()).hexdigest()[:8]
                # Get first 500 characters of function code as snippet
                function_code_snippet = source.strip()[:500]
                if len(source) > 500:
                    function_code_snippet += "..."
            except:
                function_hash = None
                function_code_snippet = None

            # Prepare input data from function arguments
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            input_data = dict(bound_args.arguments)

            # Convert non-serializable types to strings
            def make_serializable(obj):
                if isinstance(obj, (str, int, float, bool, type(None))):
                    return obj
                elif isinstance(obj, (list, tuple)):
                    return [make_serializable(item) for item in obj]
                elif isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, Image.Image):
                    # Convert PIL Image to base64
                    buffer = io.BytesIO()
                    obj.save(buffer, format='PNG')
                    img_str = base64.b64encode(buffer.getvalue()).decode()
                    return f"data:image/png;base64,{img_str}"
                elif hasattr(obj, 'read'):  # File-like object
                    try:
                        obj.seek(0)
                        content = obj.read()
                        if isinstance(content, bytes):
                            # Try to determine if it's an image
                            try:
                                img = Image.open(io.BytesIO(content))
                                buffer = io.BytesIO()
                                img.save(buffer, format='PNG')
                                img_str = base64.b64encode(buffer.getvalue()).decode()
                                return f"data:image/png;base64,{img_str}"
                            except:
                                # Not an image, convert to base64 anyway
                                return base64.b64encode(content).decode()
                        else:
                            return str(content)
                    except:
                        return str(obj)
                else:
                    return str(obj)

            input_data = make_serializable(input_data)

            # Record start time
            start_time = time.time()
            error_occurred = False
            output = None

            try:
                # Execute the function
                output = func(*args, **kwargs)
                return output
            except Exception as e:
                error_occurred = True
                output = str(e)
                raise
            finally:
                # Calculate latency
                end_time = time.time()
                latency = end_time - start_time

                # Prepare trace payload
                trace_payload = {
                    "project_id": project_id,
                    "trace_id": trace_id,
                    "function_name": actual_function_name,
                    "function_hash": function_hash,
                    "function_code_snippet": function_code_snippet,
                    "input": input_data,
                    "output":
                    make_serializable(output) if not error_occurred else None,
                    "error": error_occurred,
                    "latency": latency,
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Send to API asynchronously (non-blocking)
                try:
                    response = requests.post(f"{API_BASE_URL}/update_trace",
                                             json=trace_payload,
                                             timeout=5)
                    if response.status_code != 200:
                        print(
                            f"Warning: Failed to log trace for {actual_function_name}: {response.text}"
                        )
                except Exception as api_error:
                    print(f"Warning: Failed to send trace to API: {api_error}")

        return wrapper

    return decorator


def update_trace_rating(project_id: str, trace_id: str, rating: float):
    """
    Update the rating for a specific trace.
    
    Args:
        project_id: The project ID
        trace_id: The trace ID to update
        rating: Rating value (typically 1-5)
    """
    try:
        payload = {
            "project_id": project_id,
            "trace_id": trace_id,
            "rating": rating
        }

        response = requests.post(f"{API_BASE_URL}/update_trace",
                                 json=payload,
                                 timeout=5)

        if response.status_code == 200:
            print(f"Successfully updated rating for trace {trace_id}")
        else:
            print(f"Failed to update rating: {response.text}")

    except Exception as e:
        print(f"Error updating trace rating: {e}")


def get_traces(project_id: str, function_name: str, filter_mode: str = "all"):
    """
    Fetch traces for a specific function.
    
    Args:
        project_id: The project ID
        function_name: The function name to fetch traces for
        filter_mode: Filter mode ('all', 'improve', 'excellent', 'annotate')
    
    Returns:
        Dict containing traces and recommendations
    """
    try:
        response = requests.get(f"{API_BASE_URL}/fetch_traces",
                                params={
                                    "project_id": project_id,
                                    "function_name": function_name,
                                    "filter_mode": filter_mode
                                },
                                timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch traces: {response.text}")
            return None

    except Exception as e:
        print(f"Error fetching traces: {e}")
        return None
