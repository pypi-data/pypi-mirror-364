# QUASARA API SDK

The official Python SDK for interacting with the **Quasara API**.  
This package provides a convenient wrapper for all API endpoints, including:

- Dataset management  
- File uploads  
- Embedding extraction  
- Semantic search

---

## 📦 Installation

Install the package directly from PyPI:

```bash
pip install quasara-api
```

## Authentication

First initialise the client with your API key.

```python 
client = Client(api_key="YOUR_API_KEY")
```
If you need to retrieve your API key programmatically, you can use the get_api_key method:

```python 
# This is an alternative if you don't have your key yet
api_key = client.get_api_key(email="user@example.com", password="your_password")
client = Client(api_key=api_key)
```


# Example: Complete Workflow

Here’s a complete example of creating a dataset, uploading images, starting the vectorization job, monitoring its status, and finally searching.

1. Create a Dataset

```python
try:
    dataset = client.datasets.create(name="My Awesome Photos")
    dataset_id = dataset.get("id")
    print(f"Successfully created dataset with ID: {dataset_id}")
except Exception as e:
    print(f"Error creating dataset: {e}")
```

2. Upload a Folder of Images
The SDK handles zipping, splitting into chunks, and uploading automatically.

```python
if dataset_id:
    try:
        client.datasets.upload_folder(
            dataset_id=dataset_id,
            folder_path="/path/to/your/local/images_or_documents"
        )
        print("Folder upload complete.")
    except Exception as e:
        print(f"Error uploading folder: {e}")
```

3. Extract Embeddings
Trigger the vectorization process on the server. This will return a job ID.

```python
import time

job_id = None
if dataset_id:
    try:
        job = client.extract_embeddings(
            dataset_id=dataset_id,
            model_name="best:v2"
        )
        job_id = job.get("job_id")
        print(f"Embedding job started with ID: {job_id}")
    except Exception as e:
        print(f"Error starting embedding job: {e}")
```

4. Monitor Job Status
Use the JobClient to check the status of your running job.

```python
if job_id:
    while True:
        try:
            status_info = client.jobs.get_job_status(job_id=job_id)
            current_status = status_info.get("status")
            print(f"Current job status: {current_status}")
            
            if current_status in ["COMPLETED", "FAILED"]:
                break
            
            time.sleep(30) # Wait for 30 seconds before checking again
        except Exception as e:
            print(f"Error checking job status: {e}")
            break
```

5. Perform a Search
Once the job is complete, you can perform a search query.

```python
# Assuming your new dataset was given a tag_id upon creation/processing
tag_id = "some_tag_id_associated_with_your_dataset"

try:
    results = client.search(
        tag_ids=[tag_id],
        text_query="a photo of a house by a lake"
    )
    print("Search Results:")
    for result in results.get("results", []):
        print(f"- {result}")
except Exception as e:
    print(f"Error performing search: {e}")
```
API Reference
Main Client (client)
.get_api_key(email, password): Retrieves an API key.

.get_models(): Retrieves all available models.

.extract_embeddings(dataset_id, model_name, **kwargs): Triggers an embedding job.

.search(tag_ids, **kwargs): Performs a search query.

Datasets (client.datasets)
.create(name): Creates a new dataset.

.get_datasets(): Lists all datasets for the user.

.upload_folder(dataset_id, folder_path): Uploads a local folder of images.

.get_tags(): Retrieves all tags.

Jobs (client.jobs)
.get_jobs(): Retrieves all jobs for the user.

.get_job_status(job_id): Gets the status of a specific job.

.pause_job(job_id): Pauses a running job.