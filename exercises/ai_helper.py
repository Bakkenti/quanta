import requests
import re
from main.models import ConspectMessage
import time
from requests.exceptions import Timeout, RequestException
import json

EXECUTE_URL = "https://microservice-quanta.up.railway.app/execute"
AI_FEEDBACK_URL = "https://microservice-quanta.up.railway.app/feedback"
ASK_AI_URL = "https://microservice-quanta.up.railway.app/ask"
RECOMMENDATION_URL = "https://microservice-quanta.up.railway.app/recomend"
CONSPECT_URL = "https://microservice-quanta.up.railway.app/conspect"


def execute_code(language, code):
    try:
        resp = requests.post(
            EXECUTE_URL,
            json={
                "language": language,
                "code": code
            },
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("stdout", ""), data.get("stderr", ""), data.get("exitCode", 1)
        else:
            return "", f"Execution service error: {resp.status_code}", 1
    except Exception as e:
        return "", f"Execution service not available: {str(e)}", 1

def get_code_hint(input_code, question, prompt_language="python"):
    try:
        resp = requests.post(
            AI_FEEDBACK_URL,
            json={
                "input": input_code,
                "question": question,
                "language": prompt_language
            },
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json().get("text", "No hint received."), resp.json().get("code", "")
        else:
            return f"AI service error: {resp.status_code}", ""
    except Exception as e:
        return f"AI service not available: {str(e)}", ""

def clean_language_name(s):
    return re.sub(r'[^a-zA-Z]', '', s).strip().capitalize()

def forward_answers_to_ai(answers: str) -> dict:
    try:
        payload = {"question": answers}

        start_time = time.time()
        response = requests.post(RECOMMENDATION_URL, json=payload, timeout=60)
        duration = time.time() - start_time

        if response.status_code != 200:
            raise Exception(f"AI service failed with {response.status_code}: {response.text[:300]}")

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise Exception("Failed to parse JSON from AI response")

        return data

    except Timeout:
        raise Exception("AI request timed out (over 60s)")

    except RequestException as e:
        raise Exception(f"AI request error: {str(e)}")

    except Exception as e:
        raise Exception(f"AI communication error: {str(e)}")


def generate_conspect_response(chat, user_message):
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in chat.messages.order_by("timestamp")
    ] + [{"role": "user", "content": user_message}]

    payload = {
        "topic": chat.topic,
        "language": chat.language,
        "rules_style": chat.rules_style,
        "messages": messages
    }

    response = requests.post(CONSPECT_URL, json=payload, timeout=30)
    if response.status_code != 200:
        raise Exception(f"AI error: {response.text}")

    return response.json()["text"]
