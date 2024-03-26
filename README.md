# YouTube ChatBot

It will suggest you YouTube links based on text or image given.

## Prerequisites

Before proceeding, ensure you have the following installed on your system:

- Python
- pip (Python package installer)

## Setup

1. Create a virtual environment using Python's built-in `venv` module:

    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment. The command might differ based on your operating system:

    - **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    - **Unix/macOS:**
        ```bash
        source venv/bin/activate
        ```

3. Install the required Python packages from the provided `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To run the FastAPI application, follow these steps:

1. Launch the FastAPI application using Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

2. Once the application is running, you can interact with it using HTTP requests.

## Sending a Request

To send a request to the running FastAPI application, you can use tools like `curl` or any HTTP client. Below is an example `curl` command to send a file and text data to the `/combined` endpoint:

```bash
curl --location 'http://127.0.0.1:8000/combined' \
--form 'file=@"/C:/Users/HP/Desktop/llm-assignment-master/backend/tajmahal.jpg"' \
--form 'text="IIT Patna"'
