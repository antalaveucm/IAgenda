import os
import requests
from dotenv import load_dotenv
import yaml

load_dotenv()

def create_issue(data):
    """Crea un nuevo issue en GitHub"""
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_USER')}/{os.getenv('REPO_NAME')}/issues"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }
    
    # Formatear cuerpo en YAML
    body = yaml.dump({
        "content": data["content"],
        "type": data["type"],
        "tags": data["tags"]
    })
    
    payload = {
        "title": data["title"],
        "body": body,
        "labels": [f"type:{data['type']}"] + [f"tag:{tag}" for tag in data["tags"]]
    }

    response = requests.post(url, json=payload, headers=headers);
    return response.json()

def search_issues():
    """Obtiene todos los issues del repositorio"""
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_USER')}/{os.getenv('REPO_NAME')}/issues"
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    
    response = requests.get(url, headers=headers)
    issues = []
    
    for issue in response.json():
        content = yaml.safe_load(issue["body"])
        issues.append({
            "id": str(issue["number"]),
            "title": issue["title"],
            "content": content["content"],
            "type": content["type"],
            "tags": content["tags"]
        })
    
    return issues