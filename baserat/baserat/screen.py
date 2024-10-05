import pyautogui
import io
import base64


def get_size() -> tuple[int, int]:
    screen_width, screen_height = pyautogui.size()  # Get the size of the primary monitor.
    return screen_width, screen_height


def get_screenshot_in_base64(ss_file_name="", region=None) -> str:
    # Base64 images work with ChatCompletions API but not Assistants API
    img_bytes = get_screenshot_as_file_object(ss_file_name, region)
    encoded_image = base64.b64encode(img_bytes.read()).decode('utf-8')
    return encoded_image


def get_screenshot_as_file_object(ss_file_name="", region = None):
    # In memory files don't work with OpenAI Assistants API because of missing filename attribute
    img_bytes = io.BytesIO()
    if not region:
        img = pyautogui.screenshot()  # Takes roughly 100ms # img.show()
    else:
        img = pyautogui.screenshot(region=region)  # Takes roughly 100ms # img.show()
    if ss_file_name:
        img.save(ss_file_name)
    img.save(img_bytes, format='PNG')  # Save the screenshot to an in-memory file.
    img_bytes.seek(0)
    return img_bytes
