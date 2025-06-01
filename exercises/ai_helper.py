import requests

EXECUTE_URL = "https://quanta-production.up.railway.app/execute"
AI_FEEDBACK_URL = "https://quanta-production.up.railway.app/feedback"

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
