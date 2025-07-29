"""Example module for demonstration purposes."""
from .prompt import Prompt
import json
from llmcore_sdk.models import Friday, FridayVision
import base64
from PIL import Image
import cv2
import time
import os
import io
import numpy as np

mllm_api = FridayVision(
    model="anthropic.claude-3.5-sonnet-v2",
    max_tokens=4096,
    temperature=0.01,
    direction="CaseGeneration")

def case_generation(page: str,  prompt: str)  -> str:
    request_img = base64.b64decode(page)
    image = Image.open(io.BytesIO(request_img))
    image = image.convert('RGB')
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    current_timestamp = str(int(time.time()*1000))
    app_traversal_dir = os.path.dirname(os.path.realpath(__file__))
    temp_dir = os.path.join(app_traversal_dir, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    image1_local_temp_pth = os.path.join(temp_dir, f'{current_timestamp}_image1.png')
    cv2.imwrite(image1_local_temp_pth, image)
    case_generation_prompt: str = Prompt.get_single_image_case_generation_prompt(prompt)
    generated_case: str = mllm_api.complex_chat(
        messages=[
            {
                "role": "user",
                "content": case_generation_prompt,
                "image_url": image1_local_temp_pth,
            }
        ]
    )
    if os.path.exists(image1_local_temp_pth):
        os.remove(image1_local_temp_pth)
    
    return json.loads(generated_case)