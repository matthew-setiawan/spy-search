import os
import json


def create_env_file(path, content):
    with open(path, "w") as f:
        f.write(content.strip() + "\n")


def create_json_file(path, content):
    with open(path, "w") as f:
        json.dump(content, f)


if __name__ == "__main__":
    file_path = ".env"
    env_content = """\
# AI Model API Keys
DEEPSEEK_API=<YOUR-DEEPSEEK-API>
GEMINI_API=<YOUR-GEMINI-API>
XAI_API_KEY=<YOUR-XAI-API-KEY>
OPENAI_API_KEY=<YOUR-OPENAI-API-KEY>
ANTHROPIC_API_KEY=<YOUR-ANTHROPIC-API-KEY>

# Google Custom Search Engine API
GOOGLE_CSE_API_KEY=<YOUR-GOOGLE-CSE-API-KEY>
GOOGLE_CSE_ID=<YOUR-GOOGLE-CSE-ID>
"""
    create_env_file(file_path, env_content)
    print(f".env file created at {os.path.abspath(file_path)}")

    os.makedirs("./tmp/screenshot", exist_ok=True)
    os.makedirs("./local_files", exist_ok=True)

    messages_file = "messages.json"
    create_json_file(messages_file, [])
    print(f"{messages_file} created with empty list content")
