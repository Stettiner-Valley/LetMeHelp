import os
import base64
import sys
import click

from dotenv import load_dotenv

from baserat import screen, interpreter
from jinja2 import Environment, FileSystemLoader

from baserat.llm import LLM_HANDLER, LLM_PROVIDER, LLM

jinja_env = Environment(loader = FileSystemLoader(os.path.join(os.getcwd(), "baserat", "prompts")))

load_dotenv()


def _code_for_corordinates():
    # Define the folder path containing PNG images
    folder_path = os.path.join(os.getcwd(), "baserat", "data")
    # (37,358), (128,410)

    test_prompts = [
        {
            "screen_view_prompt": "what is the name of the presentation software shown? only return 'full name' nothing else",
            "screen_pixel_prompt": f"My screen size is {screen.get_size()}, I want you to give me only co-ordinates of where I need to click to select slide with bullet points. Only return co ordinates in (x,y) e.g (12,34) no other text!",
            "screen_view_ground_truth": "microsoft powerpoint",
            "screen_pixel_ground_truth": "(37,358), (128,410)"  # (37,358), (128,410)
        },
        {
            "screen_view_prompt": "Is slide with bullet point selected already? Only answer Yes or No",
            "screen_pixel_prompt": f"My screen size is {screen.get_size()}, I want you to give me only co-ordinates of Where I need to click to select bullet points only return co ordinates in (x,y) e.g (12,34) no other text!",
            "screen_view_ground_truth": "yes",
            "screen_pixel_ground_truth": "(448,236)"
        },
        {
            "screen_view_prompt": "Is text box with bullet point selected already? Only answer Yes or No",
            "screen_pixel_prompt": f"My screen size is {screen.get_size()}, I want you to give me only co-ordinates of Where I need to click to apply animations to bullet points only return co ordinates in (x,y) e.g (12,34) no other text!",
            "screen_view_ground_truth": "Yes",
            "screen_pixel_ground_truth": "(569,123)"
        },
        {
            "screen_view_prompt": "Is Animation tab from menu bar already selected? Only answer Yes or No",
            "screen_pixel_prompt": f"My screen size is {screen.get_size()}, I want you to give me only co-ordinates of Where I need to click to apply animations to bullet points only return co ordinates in (x,y) e.g (12,34) no other text!",
            "screen_view_ground_truth": "Yes",
            "screen_pixel_ground_truth": "(594,126)"
        },
        {
            "screen_view_prompt": "Are animations already applied to bullet points? Only answer Yes or No",
            "screen_view_ground_truth": "Yes"
        },
    ]

    for filename in os.listdir(folder_path):
        file_number = int(''.join(filter(str.isdigit, filename)))
        print(f"\nReading: {filename}, no: {file_number}")
        # Check if the file is a PNG image
        file_path = os.path.join(folder_path, filename)

        try:
            # Read the content of the PNG file
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()

            # Convert the file content to base64 encoding
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
            print(f"Done reading: {filename}")
            prompt_data_obj = test_prompts[file_number - 1]
            prompt = prompt_data_obj["screen_view_prompt"]
            # llm_response = send_msg_to_llm(base64_encoded, file_number, prompt)
            # print(prompt.lower())
            # print("LLM response: ", llm_response, " correct?: ",
            #       llm_response.lower() == prompt_data_obj["screen_view_ground_truth"].lower())

            if "screen_view_prompt" in prompt_data_obj:
                print(prompt_data_obj["screen_pixel_prompt"].lower())
                llm_response = send_msg_to_llm(base64_encoded, file_number, prompt_data_obj["screen_pixel_prompt"])
                print("LLM response: ", llm_response)

            input()
            print("------------------------")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    print("All PNG images processed.")


def execute_next_step(llm, base64_encoded_screen_shot, system_prompt, user_query):
    next_step_template = jinja_env.get_template('next_step.jinja')
    next_step_prompt = next_step_template.render(user_query=user_query)

    print("Executing next steps ..")
    llm_resp = llm.send_msg_to_llm(base64_encoded_screen_shot, system_prompt, next_step_prompt)
    print("Self asking ..")
    self_ask_template = jinja_env.get_template('self_ask.jinja')
    self_ask_prompt = self_ask_template.render(user_query=user_query, llm_json_response=llm_resp)
    llm_resp = llm.send_msg_to_llm(base64_encoded_screen_shot, system_prompt, self_ask_prompt)

    interpreter.execute_key_commands(llm_resp["keys"])


@click.command()
def main(args=None) -> int:
    print("Initializing LLM ...")
    llm_provider = LLM_PROVIDER.OPENAI if os.getenv("MODEL_PROVIDER") == LLM_PROVIDER.OPENAI else LLM_PROVIDER.MISTRAL
    llm_model = LLM.GPT40 if llm_provider == LLM_PROVIDER.OPENAI else LLM.MISTRAL
    llm = LLM_HANDLER(llm_provider, llm_model)

    system_template = jinja_env.get_template('system.jinja')
    first_step_template = jinja_env.get_template('first_step.jinja')

    system_prompt = system_template.render()
    user_query= "Add animations to the slides with the bullet points so that each bullet point appears one after each other"
    # user_query= "Duplicate the slide which has the bullet points"

    base64_encoded_screen_shot = screen.get_screenshot_in_base64()
    first_step_prompt = first_step_template.render(user_query=user_query)
    llm_resp = llm.send_msg_to_llm(base64_encoded_screen_shot, system_prompt, first_step_prompt)

    if not llm_resp["is_application_active"]:
        print(llm_resp["reason"])
    else:
        print(f"Putting {llm_resp["application_name"]} in focus ...")
        interpreter.activate_application(llm_resp["application_name"])

        # Application is now active
        execute_next_step(llm, base64_encoded_screen_shot, system_prompt, user_query)

    return 0


if __name__ == "__main__":
    sys.exit(main())
