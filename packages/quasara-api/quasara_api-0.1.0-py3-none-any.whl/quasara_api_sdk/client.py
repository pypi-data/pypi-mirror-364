# src/your_service_sdk/client.py
import os
import tempfile
from zipfile import ZipFile
from typing import List, Optional

import requests

# --- HELPER FUNCTION (from your script) ---
# It's good practice to make this a "private" helper by starting with an underscore.
def _split_folder_to_zips(folder_path, zip_base_name, max_size_bytes):
    zip_files = []
    current_size = 0
    part_number = 1
    current_zip_path = f"{zip_base_name}_part{part_number}.zip"
    current_zip = ZipFile(current_zip_path, 'w')

    for root, _, files in os.walk(folder_path):
        for file in files:
            # Filter for jpg/png, same as your script
            if not (file.lower().endswith('.jpg') or file.lower().endswith('.png')):
                continue

            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)

            if current_size > 0 and current_size + file_size > max_size_bytes:
                current_zip.close()
                zip_files.append(current_zip_path)

                part_number += 1
                current_zip_path = f"{zip_base_name}_part{part_number}.zip"
                current_zip = ZipFile(current_zip_path, 'w')
                current_size = 0

            arcname = os.path.relpath(file_path, folder_path)
            current_zip.write(file_path, arcname)
            current_size += file_size

    current_zip.close()
    zip_files.append(current_zip_path)
    return zip_files


# This class will handle all dataset-related API calls
class DatasetsClient:
    def __init__(self, client: "Client"):
        self._client = client

    def create(self, name: str) -> dict:
        """
        Creates a new dataset.
        Returns Dataset ID
        """
        payload = {"name": name}
        # Assuming your endpoint is POST /datasets/
        return self._client._make_request("POST", "/define-dataset", json=payload)

    def get_datasets(self) -> dict:
        """Lists all Datasets related to the user """
        # Assuming your endpoint is GET /datasets/{dataset_id}
        return self._client._make_request("GET", f"/datasets")


    #This is what client calls :) 
    def upload_folder(self, dataset_id: str, folder_path: str, max_zip_size_gb: float = 1.8):
        """
        Zips a folder of images, splits it into chunks, and uploads them to the dataset.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to upload files to.
        folder_path : str
            The local path to the folder containing images.
        max_zip_size_gb : float, default=1.8
            The maximum size for each zip chunk in gigabytes.
        """
        if not os.path.isdir(folder_path):
            raise ValueError(f"The provided path is not a valid directory: {folder_path}")

        # Use a temporary directory to store the zips, which is automatically cleaned up.
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_base_name = os.path.join(temp_dir, "upload_chunk")
            max_size_bytes = max_zip_size_gb * 1024 * 1024 * 1024

            print("Splitting folder into zip files...")
            zip_files = _split_folder_to_zips(folder_path, zip_base_name, max_size_bytes)
            print(f"Created {len(zip_files)} zip file(s).")

            for i, zip_path in enumerate(zip_files):
                print(f"Uploading part {i+1}/{len(zip_files)}: {os.path.basename(zip_path)}...")
                try:
                    # This internal method handles the actual upload request
                    self._upload_zip_chunk(dataset_id, zip_path)
                except Exception as e:
                    print(f"Failed to upload {os.path.basename(zip_path)}. Aborting.")
                    raise e # Re-raise the exception to stop the process
            
            print("All parts uploaded successfully!")

    def _upload_zip_chunk(self, dataset_id: str, zip_path: str):
        """Internal method to upload a single zip file."""
        endpoint = "/upload-dataset/" # The endpoint from your script
        
        # The client's _make_request handles the base_url and auth headers automatically!
        with open(zip_path, 'rb') as file_obj:
            files = {'dataset_zip_file': file_obj}
            data = {'dataset_id': dataset_id}
            
            # Use the main client's request method
            self._client._make_request("POST", endpoint, files=files, data=data)

    def get_tags(self):
        """Retrieve All Tag IDs along with their associated resources and model labels."""
        return self._client._make_request("POST", "/tags")


#TODO
# This class will handle all job-related API calls
class JobClient:
    def __init__(self, client: "Client"):
        self._client = client

    def get_jobs(self):
        """Retrieve All Jobs associated with a user alongside details such as job ID, the dataset it is linked to, 
        current status, a message, and the timestamp of creation or last update are included."""
        return self._client._make_request("GET", "/jobs")

    def get_job_status(self,job_id):
        """
        Get Job Status
        """
        payload = {
            job_id = job_id
        }
        return self._client._make_request("POST","/job-status")

    def pause_job(self,job_id):
        """
        PAUSE RUNNING JOB
        """
        payload = {
            job_id = job_id
        }
        return self._client._make_request("PUT","/pause-job")


# This is the main client class the user interacts with
class Client:
    def __init__(self, api_key: str, base_url: str = "https://plato.quasara.io:8501/api/v1/"):
        self.api_key = api_key
        self.base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        
        # Create the sub-client for dataset operations
        self.datasets = DatasetsClient(self)


        # Create the sub-client for Job related operations
        self.jobs = JobClient(self)

        # Create the sub-client for object detection operations
        self.object_detection = ObjectDetectionClient(self)


    def _make_request(self, method: str, endpoint: str, **kwargs):
        # ... (same as before)
        url = f"{self.base_url}{endpoint}"
        response = self._session.request(method, url, **kwargs)
        response.raise_for_status()
        
        # Handle responses that might not have a JSON body (like file uploads)
        if response.status_code == 204: # No Content
            return None
        return response.json()

    def get_api_key(self,email,password):
        """
        Retrieves API KEY for user.
        """
        payload={
            email = email, 
            password = password
        }
        return self._client._make_request("POST", "/login", json=payload)

    def get_models(self):
        """
        Retrieves all the available models
        """
        return self._client._make_request("GET", "/models")

    def extract_embeddings(self,dataset_id,model_name,**kwargs):
        """
        Triggers the embedding extraction process for a dataset using a specific model.
        """
        payload = {
            dataset_id,
            model_name
        }
        
        #Add any additional optional arguments such as batch size
        payload.update(kwargs)

        return self._client._make_request("POST", '/extract_embeddings', json=payload)
    

    def search(
    self,
    tag_ids: List[str],
    text_query: Optional[str] = None,
    image_query: Optional[str] = None,
    search_in_small_objects: bool = True,
    search_in_images: bool = True,
    limit: int = 10,
    offset: int = 0
    ) -> dict:
        """
        Runs a search query. Exactly one of text_query or image_query must be provided.

        Parameters
        ----------
        tag_ids : List[str]
            A list of dataset tag IDs to search within.
        text_query : Optional[str], default=None
            The text prompt to search for.
        image_query : Optional[str], default=None
            A base64 encoded string of the image to search for.
        search_in_small_objects : bool, default=True
            Whether to include small objects in the search.
        search_in_images : bool, default=True
            Whether to include whole images in the search.
        limit : int, default=10
            The maximum number of results to return.
        offset : int, default=0
            The number of results to skip.

        Returns
        -------
        dict
            A dictionary containing the search results.
        """
        # Validate that exactly one query type is provided
        if not text_query and not image_query:
            raise ValueError("You must provide either a 'text_query' or an 'image_query'.")
        if text_query and image_query:
            raise ValueError("You cannot provide both 'text_query' and 'image_query'.")

        # Construct the JSON payload
        payload = {
            "tag_ids": tag_ids,
            "text_query": text_query,
            "image_query": image_query,
            "search_in_small_objects": search_in_small_objects,
            "search_in_images": search_in_images,
            "limit": limit,
            "offset": offset,
        }

        # Filter out optional keys that are None
        payload = {k: v for k, v in payload.items() if v is not None}

        return self._make_request("POST", "/search/", json=payload)

    

        