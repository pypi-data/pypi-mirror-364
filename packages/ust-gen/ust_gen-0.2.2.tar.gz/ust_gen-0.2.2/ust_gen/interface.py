from .file_parser import parse_pdf, parse_excel
from .generator.story_generator import generate_epics, generate_user_stories, generate_tasks

def generate_from_file(filepath: str):
    if filepath.endswith(".pdf"):
        text = parse_pdf(filepath)
    elif filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        text = parse_excel(filepath)
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or Excel file.")

    epics = generate_epics(text)
    all_data = []
    for epic_idx, epic in enumerate(epics, start=1):
        epic_id = str(epic_idx)
        epic['id'] = epic_id
        stories = generate_user_stories(epic, epic_id)
        for story_idx, story in enumerate(stories, start=1):
            story_id = f"{epic_id}.{story_idx}"
            story['id'] = story_id
            tasks = generate_tasks(story, story_id)
            for task_idx, task in enumerate(tasks, start=1):
                task_id = f"{story_id}.{task_idx}"
                task['id'] = task_id
                task['subtasks'] = []
            story['tasks'] = tasks
        epic['stories'] = stories
        all_data.append(epic)

    return all_data
