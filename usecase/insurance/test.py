import requests

def upload_file(api_url, file_path, repo_name, agent_name,api_key=None):
    """
    Sends a file and repo name to a REST API.
    
    :param api_url: The endpoint URL of the API.
    :param file_path: The path to the file being uploaded.
    :param repo_name: The name of the repository.
    :param api_key: (Optional) API key for authentication.
    :return: Response from the API.
    """
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    files = {"file": open(file_path, "rb")}
    data = {"repository_name": repo_name,'agent_name':agent_name}

    try:
        response = requests.post(api_url, files=files, data=data, headers=headers)
        response.raise_for_status()
        return response.json()  # Assuming API returns JSON
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Example usage:
api_url = "http://localhost:8000/api_upload_document/upload"
file_path = ".\\file.txt"
repo_name = "my-repository"
api_key = "your_api_key"  # If authentication is required
agent_name = 'Claim Processing Task'

response = upload_file(api_url, file_path, repo_name, agent_name,api_key)
print(response)
