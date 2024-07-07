"""import inference
model = inference.get_model("gym_project/1")"""

from inference_sdk import InferenceHTTPClient

# initialize the client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="eR1fnL0DQWuaoyYl8lNg"
)

# infer on a local image
result = CLIENT.infer("YOUR_IMAGE.jpg", model_id="gym_project/1")