import requests

URL = "http://localhost:11434/api/generate"

def name_task(titles):
    prompt = (
        "Give a short task name (3–5 words) for these browser tabs:\n" +
        "\n".join(titles)
    )

    res = requests.post(URL, json={
        "model": "phi3",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    })

    return res.json()["response"].strip()
