import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Pull values from environment
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_API_VERSION")
endpoint = os.getenv("AZURE_ENDPOINT")
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")

if not all([api_key, api_version, endpoint, deployment_name]):
    raise RuntimeError("Missing one or more Azure OpenAI env variables")


client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=endpoint
)

def ask_azure_openai(prompt, temperature=0.0):
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful Agile assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content
