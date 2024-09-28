import torch, uvicorn, json, base64, uuid, os
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
from fastapi import FastAPI, Request

"""
Usage:

import base64
import requests   

image_path = "/path/to/screenshot.png"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
        
base64_image = encode_image(image_path)

url = 'https://YOUR_RUN_POD_PROXY_ADDRESS/'
data = {
  'prompt': 'In this UI screenshot, what is the position of the element corresponding to the View menu (with point)?',
  'image': base64_image
}

response = requests.post(url, json = data)

# {'response': '(0.96,0.41)'}
print(response.json())


"""

# NOTE: Qwen-VL scales the resolution to 448 so that it can be evaluated end-to-end!
# TODO: Use/fine-tune Qwen-VL-Max, which supports large resolution input images?
# https://github.com/QwenLM/Qwen-VL

def torch_gc():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

app = FastAPI()

@app.post("/")
async def create_item(request: Request):
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    image = json_post_list.get('image')
    history = json_post_list.get('history')
    if image is None or not image:
        return {
            "error": "image must be a base64-encoded string"
        }
    temp_name = uuid.uuid4()
    image_file = "/tmp/{}".format(temp_name)
    with open(image_file, "wb") as fh:
        fh.write(base64.b64decode(image))
    temperature = json_post_list.get('temperature')
    if temperature is None or temperature <= 0:
        temperature = 0.0001
    query = tokenizer.from_list_format([
        {'image': image_file},
        {'text': prompt},
    ])
    response, history = model.chat(tokenizer, query=query, history=history, temperature=temperature)
    os.remove(image_file)
    return {
        "response": response
    }


tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", device_map={"":0}, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("cckevinn/SeeClick", device_map={"":0}, trust_remote_code=True, bf16=True).eval()
model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-VL-Chat", device_map={"":0}, trust_remote_code=True)
model.eval()
uvicorn.run(app, host='0.0.0.0', port=8000, workers=1)
