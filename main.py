import requests
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from googleapiclient.discovery import build
import openai
from langchain.chains import ConversationChain
# from langchain.llms import OpenAI
import uuid
from langchain_community.llms import OpenAI
# from langchain_openai import OpenAI

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import base64
import uuid
import openai

from decouple import config
openai_api_key = config("OPENAI_API_KEY")

# Assuming OpenAI API key is set as an environment variable or directly here
# Set up OpenAI API key
openai.api_key =openai_api_key
# Set up YouTube API key
API_KEY_youtube = config("YOUTUBE_API_KEY")


app = FastAPI()

# Placeholder for storing session data
sessions = {}

class TextRequest(BaseModel):
    text: str
    session_id: str = None

class ImageRequest(BaseModel):
    image_base64: str
    session_id: str = None

def get_or_create_session(session_id):
    if session_id is None:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"history": []}
    elif session_id not in sessions:
        sessions[session_id] = {"history": []}  # Optionally create a new session if not found
    return session_id

def append_to_session_history(session_id, item_type, content):
    session = sessions[session_id]
    session["history"].append({"type": item_type, "content": content})

def generate_response_from_history(session_id):
    # Placeholder for generating a response based on the session history
    # This function should be implemented based on your specific logic
    # For this example, let's concatenate the contents as a simple response
    session = sessions[session_id]
    combined_text = " ".join(item["content"] for item in session["history"])
    return combined_text  # This would be replaced with your response generation logic

def search_youtube_videos(keyword, max_results=2):
    youtube = build('youtube', 'v3', developerKey=API_KEY_youtube)
    search_response = youtube.search().list(
        q=keyword,
        part='snippet',
        maxResults=max_results
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        video_title = search_result['snippet']['title']

        # try:
        video_id = search_result['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        videos.append({"title": video_title, "url": video_url})
        # except:
        #     return videos
    return videos

# Function to encode image to base64
def encode_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    return base64_image

# OpenAI API request
def generate_summary_from_image(image_base64):
    api_key_openai =openai_api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key_openai}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Generate single phrase from the image such that I can use that phrase on YouTube and search it"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print(response)
    if response.status_code == 200:
        summary = response.json()["choices"][0]["message"]["content"]
        # print(summary)
        return summary
    else:
        return None

# Initialize the OpenAI language model
llm = OpenAI(temperature=0, openai_api_key=openai.api_key)


def generate_summary(text):
    # Set your OpenAI API key
    openai.api_key =openai_api_key

    # Generate summary using OpenAI's Completion API
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=f"Summarize in a single phrase so that I could search that text on youtube and I will get similar content:\n{text}",
        max_tokens=50
    )

    # Extract and return the summary
    summary = response.choices[0].text.strip()
    return summary

# Create a conversation chain
conversation = ConversationChain(llm=llm, verbose=True)
@app.post("/text")
def handle_text_input(request: TextRequest):
    print(request.session_id)
    session_id = get_or_create_session(request.session_id)
    append_to_session_history(session_id, "text", request.text)

    # Generate a response based on the updated session history
    response = generate_response_from_history(session_id)
    data = generate_summary(response)
    videos=search_youtube_videos(data)
    return {"session_id": session_id, "response": response,"videos":videos}



class CombinedRequest(BaseModel):
    text: str = None
    session_id: str = None

async def handle_image(file: UploadFile):
    contents = await file.read()
    base64_string = base64.b64encode(contents).decode('utf-8')
    summary = generate_summary_from_image(base64_string)
    return summary

def handle_text(text: str):
    summary = generate_summary(text)
    return summary

@app.post("/combined")
async def combined_handler(text: str = Form(None), file: UploadFile = File(None)):
    summary = None
    if not text and not file:
        raise HTTPException(status_code=400, detail="Either text or file must be provided.")
    if file:
        summary = await handle_image(file)
    if text and not summary:
        summary = handle_text(text)
    if not summary:
        raise HTTPException(status_code=400, detail="Unable to generate a summary from the provided input.")
    videos = search_youtube_videos(summary)
    return {"summary": summary, "videos": videos}



def make_openai_request(prompt):
    headers = {"Authorization": f"Bearer {openai_api_key}"}
    data = {
        "prompt": prompt,
        "max_tokens": 50,
        "temperature": 0.7,
    }
    response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"]
    else:
        return "Error generating response"