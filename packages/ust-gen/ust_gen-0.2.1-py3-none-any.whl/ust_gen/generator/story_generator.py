import json
import time
from utils.azure_openai import ask_azure_openai

import re

def clean_json_response(text):
    """
    Remove triple backticks and 'json' language tag from model output.
    """
    return re.sub(r"^```json|```$", "", text.strip(), flags=re.IGNORECASE).strip()


EPIC_PROMPT_TEMPLATE = """
You are a senior product owner. Your task is to break down a high-level software requirement into large, strategic Agile Epics.

Each Epic must:
- Be focused and implementable in 1–2 sprints
- Have a user-centered description (what, why)
- Be written in a structured JSON format

---

Input Requirement:
\"\"\"{requirement}\"\"\"

---

Output format (strict JSON):
[
  {{
    "epic": "<Concise title>",
    "description": "As a <role>, I want to <do something> so that <value/outcome>."
  }}
]
"""

def generate_epics(requirement_text, max_retries=3):
    prompt = EPIC_PROMPT_TEMPLATE.format(requirement=requirement_text.strip())

    for attempt in range(max_retries):
        try:
            response_text = ask_azure_openai(prompt, temperature=0.0)


            epics = json.loads(response_text)


            if isinstance(epics, list) and all('epic' in e and 'description' in e for e in epics):
                return epics
            else:
                print("[WARN] JSON structure invalid, retrying...")

        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parsing failed: {e}. Retrying...")
            time.sleep(1)

    raise RuntimeError("Failed to generate valid epics after multiple attempts.")


USER_STORY_PROMPT_TEMPLATE = """
You are an Agile business analyst. Given an Epic, generate high-quality user stories that follow the INVEST principles and include a domain tag.

Each user story must:
- Be atomic, valuable, and independent
- Follow: "As a <role>, I want to <action> so that <benefit>"
- Include a `domain` tag: Frontend, Backend, Database, DevOps, Mobile, or Fullstack

---

Epic:
"{epic_title}"

Description:
"{epic_description}"

---

Output format (strict JSON):
[
  {{
    "story": "As a <role>, I want to <action> so that <benefit>",
    "domain": "<domain>"
  }}
]
"""

def generate_user_stories(epic, epic_id, max_retries=3):
    prompt = USER_STORY_PROMPT_TEMPLATE.format(
        epic_title=epic["epic"],
        epic_description=epic["description"]
    )

    for _ in range(max_retries):
        try:
            response_text = ask_azure_openai(prompt, temperature=0.3)
            cleaned = clean_json_response(response_text)
            stories = json.loads(cleaned)

            if isinstance(stories, list):
                for i, story in enumerate(stories, start=1):
                    story["id"] = f"{epic_id}.{i}"
                return stories

        except json.JSONDecodeError:
            time.sleep(1)

    raise RuntimeError("Failed to generate user stories after multiple attempts.")


TASK_PROMPT_TEMPLATE = """
You are a senior technical project manager collaborating with a software engineering team.

Your job is to break down the following Agile user story into 3 to 6 actionable technical tasks. Each task should be implementation-ready and specific to the assigned domain (e.g., Frontend, Backend, DevOps, etc.).

User Story:
"{story}"

Domain:
"{domain}"

Instructions:
- Tasks must be precise, technical, and oriented toward developers.
- Avoid duplicates or vague items like "do the work" or "implement logic".
- Write tasks as clear actions using imperative verbs (e.g., "Design UI", "Implement API endpoint").
- Keep tasks domain-specific. For example, if the domain is Frontend, do not include database or backend logic.
- Use clear terminology used in real-world engineering teams.

---

Output format (strict JSON):
[
  {{
    "task": "<technical task description>",
    "domain": "{domain}"
  }}
]
"""
def generate_tasks(story, story_id, max_retries=3):
    prompt = TASK_PROMPT_TEMPLATE.format(
        story=story["story"],
        domain=story["domain"]
    )

    for _ in range(max_retries):
        try:
            response_text = ask_azure_openai(prompt, temperature=0.3)
            cleaned = clean_json_response(response_text)
            tasks = json.loads(cleaned)

            if isinstance(tasks, list):
                for i, task in enumerate(tasks, start=1):
                    task["id"] = f"{story_id}.{i}"
                return tasks

        except json.JSONDecodeError:
            time.sleep(1)

    raise RuntimeError("Failed to generate tasks after multiple attempts.")


SUBTASK_PROMPT_TEMPLATE = """
You are a technical team lead. Break the following task into detailed subtasks that are actionable by a developer.

Task:
"{task}"

Domain:
"{domain}"

---

Output format (strict JSON):
[
  {{
    "subtask": "<detailed dev subtask>"
  }}
]
"""

def generate_subtasks(task, task_id, max_retries=3):
    prompt = SUBTASK_PROMPT_TEMPLATE.format(
        task=task["task"],
        domain=task["domain"]
    )

    for _ in range(max_retries):
        try:
            response_text = ask_azure_openai(prompt, temperature=0.3)
            cleaned = clean_json_response(response_text)
            subtasks = json.loads(cleaned)

            if isinstance(subtasks, list):
                for i, subtask in enumerate(subtasks, start=1):
                    subtask["id"] = f"{task_id}.{i}"
                return subtasks

        except json.JSONDecodeError:
            time.sleep(1)

    raise RuntimeError("Failed to generate subtasks after multiple attempts.")
