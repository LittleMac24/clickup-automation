import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
API_KEY = os.getenv('CLICKUP_API_TOKEN')
TEAM_ID = os.getenv('CLICKUP_TEAM_ID')
JSON_FILE = 'learning-sprint-1.json'

HEADERS = {
    'Authorization': API_KEY,
    'Content-Type': 'application/json'
}

def get_id_by_name(url, key, name):
    """Generic helper to find an object ID by its name from a ClickUp GET request."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[!] API Error while fetching {key}: {response.text}")
        return None
    
    items = response.json().get(key, [])
    for item in items:
        # Note: If this fails to find your list, ensure hyphens (-) and em-dashes (—) match perfectly.
        if item['name'].lower().strip() == name.lower().strip():
            return item['id']
    return None

def get_sprint_list_id(space_name, folder_name, list_name):
    """Navigates Space -> Folder -> List to find the exact Sprint List ID."""
    print(f"Locating Space: '{space_name}'...")
    space_id = get_id_by_name(f"https://api.clickup.com/api/v2/team/{TEAM_ID}/space", 'spaces', space_name)
    if not space_id: 
        print(f"[!] Failed to find Space: '{space_name}'")
        return None
    
    print(f"Locating Folder: '{folder_name}'...")
    folder_id = get_id_by_name(f"https://api.clickup.com/api/v2/space/{space_id}/folder", 'folders', folder_name)
    if not folder_id: 
        print(f"[!] Failed to find Folder: '{folder_name}'")
        return None
    
    print(f"Locating List: '{list_name}'...")
    list_id = get_id_by_name(f"https://api.clickup.com/api/v2/folder/{folder_id}/list", 'lists', list_name)
    if not list_id:
        print(f"[!] Failed to find List: '{list_name}'")
        
    return list_id

def create_task(list_id, task_obj, parent_id=None):
    """Creates a task or subtask with full description and details."""
    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    
    # Only include keys if they exist to prevent sending 'null' values 
    payload = {
        "name": task_obj.get('name'),
        "description": task_obj.get('description', '')
    }
    
    if 'status' in task_obj:
        payload["status"] = task_obj["status"]
        
    if 'priority' in task_obj:
        payload["priority"] = task_obj["priority"]
        
    if parent_id:
        payload["parent"] = parent_id

    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return response.json().get('id')
    else:
        print(f"  [!] Error creating '{task_obj.get('name')}': {response.text}")
        return None

def main():
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File Error: Could not find '{JSON_FILE}'. Check the filename.")
        return
    except json.JSONDecodeError as e:
        print(f"File Error: Invalid JSON formatting. {e}")
        return

    list_id = get_sprint_list_id(data['space'], data['folder'], data['list'])
    
    if not list_id:
        print("\nExiting: Could not verify the ClickUp location path.")
        return

    print("\nLocation verified! Beginning task creation...\n")
    
    for t in data.get('tasks', []):
        print(f"Creating Task: {t['name']}")
        task_id = create_task(list_id, t)
        
        if task_id and 'subtasks' in t:
            for st in t['subtasks']:
                print(f"  - Creating Subtask: {st['name']}")
                create_task(list_id, st, parent_id=task_id)

if __name__ == "__main__":
    main()