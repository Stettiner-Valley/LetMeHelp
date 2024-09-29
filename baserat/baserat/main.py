import os
import base64
import sys
from dataclasses import astuple
from time import sleep
import pyautogui

import click

from dotenv import load_dotenv

from baserat import screen, interpreter
from jinja2 import Environment, FileSystemLoader

from baserat.llm import LLM_HANDLER, LLM_PROVIDER, LLM
from baserat.platforms.manager import OS

jinja_env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), "baserat", "prompts")))

load_dotenv()


def coordinator(app_rectangle, llm, user_prompt, system_prompt, self_ask=False):
    base64_encoded_screen_shot = screen.get_screenshot_in_base64(region=astuple(app_rectangle))
    print('Coordinator was called ...')
    if not self_ask:
        prompt_template = jinja_env.get_template('get_coordinates.jinja')
        prompt = prompt_template.render(user_prompt=user_prompt)
    else:
        print("\nSELF ASKING .....")
        prompt_template = jinja_env.get_template('self_ask.jinja')
        prompt = prompt_template.render(user_prompt=user_prompt, x_coordinate=self_ask['x'], y_coordinate=self_ask['y'],
                                    prev_reason=self_ask['reason'])

    print("COORDINATE: sending App screenshot ..")
    print("USER PROMPT: ", user_prompt)
    frac_xy = llm.send_msg_to_llm(system_prompt, prompt, base64_encoded_screen_shot)

    if 'correction_required' in frac_xy and not frac_xy['correction_required']:
        return

    x = app_rectangle.x + int(app_rectangle.width * frac_xy["x"])
    y = app_rectangle.y + int(app_rectangle.height * frac_xy["y"])
    sleep(2)
    print("\nMOVING ")
    pyautogui.moveTo(x, y)
    print("CLICKING \n")
    pyautogui.click(x, y)

    if ('correction_required' in frac_xy and frac_xy['correction_required']) or (not self_ask):
        base64_encoded_screen_shot = screen.get_screenshot_in_base64(region=astuple(app_rectangle))
        coordinator(app_rectangle, llm, user_prompt, system_prompt, frac_xy)


@click.command()
def main(args=None) -> int:
    print("Initializing LLM ...")
    llm_provider = LLM_PROVIDER.OPENAI if os.getenv("MODEL_PROVIDER") == LLM_PROVIDER.OPENAI else LLM_PROVIDER.MISTRAL
    llm_model = LLM.GPT40 if llm_provider == LLM_PROVIDER.OPENAI else LLM.MISTRAL
    llm = LLM_HANDLER(llm_provider, llm_model)

    print("Initializing OS manager ...")
    os_manager = OS()

    system_template = jinja_env.get_template('system.jinja')
    first_step_template = jinja_env.get_template('first_step.jinja')

    system_prompt = system_template.render(installed_apps=', '.join(os_manager.os.list_open_applications()))

    user_query = "Add animations to the slides with the bullet points so that each bullet point appears one after each other"
    # user_query= "Duplicate the slide which has the bullet points"

    base64_encoded_screen_shot = screen.get_screenshot_in_base64()
    first_step_prompt = first_step_template.render(user_query=user_query)
    llm_resp = llm.send_msg_to_llm(system_prompt, first_step_prompt, base64_encoded_screen_shot)

    interpreter.activate_application(llm_resp["application_name"])
    app_rectangle = os_manager.os.get_app_window_rectangle(llm_resp["application_name"])

    prompt = "Given the screen shot, User want click on second slide with bullet points present in this screenshot."
    coordinator(app_rectangle, llm, prompt, system_prompt)
    prompt = "Given the screen shot, User want click on Animation tab which is between Transitions and Slide Show tabs."
    coordinator(app_rectangle, llm, prompt, system_prompt)
    prompt = "Given the screen shot, User want to click on the text box containing Bullet points. Please ignore side menu and click on the text."
    coordinator(app_rectangle, llm, prompt, system_prompt)
    prompt = "Given the screen shot, User want to click Appear button present in the Animation tab. This button is big green star, left to the Preview button."
    coordinator(app_rectangle, llm, prompt, system_prompt)

    return 0


if __name__ == "__main__":
    sys.exit(main())
