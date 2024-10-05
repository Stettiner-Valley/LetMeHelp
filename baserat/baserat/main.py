import os
import pygetwindow as gw
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
from baserat.platforms.macos import Rectangle
from baserat.platforms.manager import OS

jinja_env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), "baserat", "prompts")))

load_dotenv()


def coordinator(app_rectangle, llm, user_prompt, system_prompt, self_ask=False):
    base64_encoded_screen_shot = screen.get_screenshot_in_base64(ss_file_name="maq.png", region=astuple(app_rectangle))
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
    print(f"app_rectangle.x {app_rectangle.x}, app_rectangle.width {app_rectangle.width}, frac_x {frac_xy['x']}")
    print(f"app_rectangle.y {app_rectangle.y}, app_rectangle.height {app_rectangle.height}, frac_y {frac_xy['y']}")

    print(f"\nMOVING {x}, {y} ")
    pyautogui.moveTo(x, y)
    print(f"CLICKING {x}, {y} \n")
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
    # user_query = "Add animations to the slides with the bullet points so that each bullet point appears one after each other"
    # user_query= "Duplicate the slide which has the bullet points"\
    user_query = "Add animation to make the bullet points appears one by one"

    system_template = jinja_env.get_template('system.jinja')
    first_step_template = jinja_env.get_template('first_step.jinja')
    system_prompt = system_template.render(installed_apps=', '.join(os_manager.os.list_open_applications()))
    first_step_prompt = first_step_template.render(user_query=user_query)

    base64_encoded_screen_shot = screen.get_screenshot_in_base64(ss_file_name="mo.png")
    llm_resp = llm.send_msg_to_llm(system_prompt, first_step_prompt, base64_encoded_screen_shot)

    interpreter.activate_application(llm_resp["application_name"])
    print(llm_resp["application_name"])
    rect = gw.getWindowGeometry(llm_resp["application_name"])
    app_rectangle = Rectangle(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
    print("App rectangle: ", app_rectangle)

    # planning_template = jinja_env.get_template('planning.jinja')
    # planning_prompt = planning_template.render(user_query=user_query, application=llm_resp["application_name"], user_os=OS.OPERATING_SYSTEM)
    # steps_from_llm = llm.send_msg_to_llm(system_prompt=system_prompt, prompt=planning_prompt)
    # steps_from_llm = list(map(lambda step : f"Given the screen shot, User want you to {step}", steps_from_llm["steps"]))
    #
    # print(f"\n\nLLM's Plan:\n{"\n".join(steps_from_llm)}")

    steps = [
        "Given the screen shot, User want click on Animation tab which is between Transitions and Slide Show tabs.",
        "Given the screen shot, User want to click on the text box containing Bullet points. Please ignore side menu and click on the text.",
        "Given the screen shot, User want to click Appear button present in the Animation tab. This button is big green star, left to the Preview button.",
    ]
    for step in steps:
        coordinator(app_rectangle, llm, step, system_prompt)

    # for idx, step in enumerate(steps_from_llm):
    #     if idx != 0:
    #         base64_encoded_screen_shot = screen.get_screenshot_in_base64(region=astuple(app_rectangle))
    #     self_ask_planning_template = jinja_env.get_template('self_ask_planning.jinja')
    #     self_ask_planning_prompt = self_ask_planning_template.render(step=step, user_query=user_query)
    #
    #     print("\n\nVALIDATING STEP: ", step)
    #     print("\n")
    #     resp = llm.send_msg_to_llm(system_prompt=system_prompt, prompt=self_ask_planning_prompt, base64_encoded_img=base64_encoded_screen_shot)
    #     if not resp["executable"]:
    #         print(f"UNCLICKABLE STEP: `{step}` was not performable! reason: {resp['reason']} ")
    #         print(f"new step: {resp["step"]}")
    #         step = resp["step"]
    #     else:
    #         print("STEP is VALID: ", resp['reason'])
    #     coordinator(app_rectangle, llm, step, system_prompt)

    return 0


if __name__ == "__main__":
    sys.exit(main())
