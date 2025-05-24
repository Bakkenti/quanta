import requests

AI_FEEDBACK_URL = "https://quanta-production.up.railway.app/feedback"

def get_code_hint(student_code, student_output, expected_output, prompt_language="python"):
    prompt = (
        f"Student has incorrect answer: {student_output}. "
        f"Needed answer: {expected_output}. "
        f"His code: {student_code}. "
        f"Give hint for him to get correct answer. Sentences only no more 3."
    )
    try:
        resp = requests.post(
            AI_FEEDBACK_URL,
            json={
                "parameter": prompt,
                "language": prompt_language
            },
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json().get("result", "No hint received.")
        else:
            return f"AI service error: {resp.status_code}"
    except Exception as e:
        return f"AI service not available: {str(e)}"
