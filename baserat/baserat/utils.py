import json

def jsonify(json_text: str):
    if json_text.startswith("```"):
        json_text = json_text.replace("```json", "")[:-3]
    return json.loads(json_text)

