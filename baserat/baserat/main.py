import os
import base64
import sys
import click

from dotenv import load_dotenv
from openai import OpenAI

from baserat import screen

load_dotenv()


@click.command()
def main(args=None) -> int:
    click.echo("Replace this message by putting your code into "
               "baserat.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")

    # Define the folder path containing PNG images
    folder_path = os.path.join(os.getcwd(), "baserat", "data")
    # (37,358), (128,410)

    test_prompts = [
        {
            "screen_view_prompt": "what is the name of the presentation software shown? only return 'full name' nothing else",
            "screen_pixel_prompt": f"My screen size is {screen.get_size()}, I want you to give me only co-ordinates of where I need to click to select slide with bullet points. Only return co ordinates in (x,y) e.g (12,34) no other text!",
            "screen_view_ground_truth": "microsoft powerpoint",
            "screen_pixel_ground_truth": "(37,358), (128,410)" # (37,358), (128,410)
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
    return 0


def send_msg_to_llm(base64_encoded_img, file_number, prompt):
    message = [
        {'type': 'text',
         'text': prompt},
        {'type': 'image_url',
         'image_url': {
             'url': f'data:image/jpeg;base64,{base64_encoded_img}'
         }
         }
    ]
    print("Sending image to LLM")
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    response = client.chat.completions.create(
        model=os.getenv("MODEL_IN_USE"),
        messages=[
            {
                'role': 'user',
                'content': message,
            }
        ]
    )
    llm_response = response.choices[0].message.content.strip()
    return llm_response


if __name__ == "__main__":
    sys.exit(main())
