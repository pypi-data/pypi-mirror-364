import logging
import mimetypes
import os
import time
from typing import Any, NoReturn

import requests

from .types import (
    CancelRunResponse,
    ExecuteWorkflowResponse,
    GetOutputResponse,
    HealthCheckResponse,
    QueueResponse,
    RunDetailResponse,
    RunListResponse,
)


class FlowscaleAPI:
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize the Flowscale API client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-API-KEY": api_key}

    def check_health(self) -> HealthCheckResponse:
        """
        Checks the health status of all ComfyUI instances within the specified cluster.

        Returns:
            The health status response
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/comfy/health", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def get_queue(self) -> QueueResponse:
        """
        Retrieves the queue data for all ComfyUI instances in the cluster.

        Returns:
            The queue status response
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/comfy/queue", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def execute_workflow(
        self, workflow_id: str, data: dict[str, Any], group_id: str | None = None
    ) -> ExecuteWorkflowResponse:
        """
        Executes a specified workflow by processing dynamic form data.

        Args:
            workflow_id: The ID of the workflow to execute
            data: Form data including text fields and file uploads
            group_id: Optional group ID

        Returns:
            The workflow execution response
        """
        files = {}
        form_data = {}
        opened_files = []

        try:
            # Process the data into files and form fields
            for key, value in data.items():
                if hasattr(value, "read") and callable(value.read):
                    # It's a file-like object
                    files[key] = value
                elif isinstance(value, list | tuple):
                    # Handle arrays (for multiple files)
                    for i, item in enumerate(value):
                        if hasattr(item, "read") and callable(item.read):
                            files[f"{key}_{i}"] = item
                        else:
                            form_data[f"{key}_{i}"] = item
                elif isinstance(value, str) and os.path.isfile(value):
                    # It's a file path
                    file_name = os.path.basename(value)
                    file_obj = open(value, "rb")
                    opened_files.append(file_obj)
                    files[key] = (
                        file_name,
                        file_obj,
                        mimetypes.guess_type(value)[0] or "application/octet-stream",
                    )
                else:
                    # It's a regular value
                    form_data[key] = value

            # Construct the URL with query parameters
            url = f"{self.base_url}/api/v1/runs?workflow_id={workflow_id}"
            if group_id:
                url += f"&group_id={group_id}"

            response = requests.post(
                url, headers=self.headers, data=form_data, files=files
            )
            response.raise_for_status()

            return response.json()

        except Exception as error:
            self._handle_error(error)
        finally:
            # Always close opened files
            for file_obj in opened_files:
                try:
                    file_obj.close()
                except Exception as e:
                    logging.error(f"Failed to close file: {file_obj}: {e}")

    def execute_workflow_async(
        self,
        workflow_id: str,
        data: dict[str, Any],
        group_id: str | None = None,
        timeout: int = 300,
        polling_interval: int = 1,
    ) -> GetOutputResponse | None:
        """
        Executes a workflow and polls for its output until completion or timeout.

        Args:
            workflow_id: The ID of the workflow to execute
            data: Form data including text fields and file uploads
            group_id: Optional group ID
            timeout: Maximum time to wait for results in seconds (default: 300)
            polling_interval: Time between polling attempts in seconds (default: 1)

        Returns:
            The output response or None if no output is found within timeout

        Raises:
            Exception: If the execution times out or encounters an error
        """
        # Execute the workflow
        execution_response = self.execute_workflow(workflow_id, data, group_id)

        # Get the filename from the response
        if not execution_response or "data" not in execution_response:
            raise Exception("No data in execution response")

        response_data = execution_response["data"]
        if "output_names" not in response_data or not response_data["output_names"]:
            raise Exception("No output_names in execution response")

        filename = response_data["output_names"][0]
        start_time = time.time()

        # Poll until we get a result or timeout
        while True:
            if time.time() - start_time > timeout:
                raise Exception(f"Workflow execution timed out after {timeout} seconds")

            output = self.get_output(filename)
            if output is not None:
                return output

            time.sleep(polling_interval)

    def get_output(self, filename: str) -> GetOutputResponse | None:
        """
        Retrieves the output of a specific run by providing the filename.

        Args:
            filename: The filename of the output to retrieve

        Returns:
            The output response or None if no output is found
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/runs/output",
                headers=self.headers,
                params={"filename": filename},
            )

            if response.status_code == 204:
                return None

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 204:
                return None
            elif error.response.status_code == 408:
                raise Exception("Run Timeout") from error
            else:
                self._handle_error(error)
        except Exception as error:
            self._handle_error(error)

    def cancel_run(self, run_id: str) -> CancelRunResponse:
        """
        Cancels a specific run using its unique run ID.

        Args:
            run_id: The ID of the run to cancel

        Returns:
            The cancellation response
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/runs/{run_id}/cancel", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def get_run(self, run_id: str) -> RunDetailResponse:
        """
        Retrieves detailed information about a specific run using its unique run ID.

        Args:
            run_id: The ID of the run to retrieve

        Returns:
            The run details response
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/runs/{run_id}", headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def get_runs(self, group_id: str | None = None) -> RunListResponse:
        """
        Retrieves a list of all runs associated with a specific group ID.
        If no group ID is provided, all runs will be returned.

        Args:
            group_id: The group ID to filter runs

        Returns:
            The list of runs response
        """
        try:
            params = {"group_id": group_id} if group_id else {}
            response = requests.get(
                f"{self.base_url}/api/v1/runs", headers=self.headers, params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_error(error)

    def _handle_error(self, error: Exception) -> NoReturn:
        """
        Error handling helper.

        Args:
            error: The exception to handle
        """
        if isinstance(error, requests.exceptions.HTTPError):
            response = error.response
            raise Exception(
                f"Error: {response.status_code} {response.reason} - {response.text}"
            )
        elif isinstance(error, requests.exceptions.RequestException):
            raise Exception(f"Request error: {str(error)}")
        else:
            logging.error(f"Unexpected error in FlowscaleAPI: {error}")
            raise Exception(f"Error: {str(error)}")
