import json
import os
import asyncio
import base64
import logging
import sys
import uuid
from dataclasses import astuple
from time import sleep
import pyautogui
import pygetwindow as gw

import click

from dotenv import load_dotenv

from baserat import screen, interpreter
from jinja2 import Environment, FileSystemLoader
from websockets.asyncio.server import serve

from baserat.llm import LLM_HANDLER, LLM_PROVIDER, LLM
from baserat.platforms.macos import Rectangle
from baserat.platforms.manager import OS

jinja_env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), "baserat", "prompts")))

load_dotenv()

# Logging
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

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


def error_message(message):
    return json.dumps({"type": "error", "value": message})

# Display a textual message to the user
def text_message(message):
    return json.dumps({"type": "text", "value": message})

# Take an action (e.g. take a screenshot, click somewhere, type something, etc.)
def action_message(name, data):
    return json.dumps({"type": name, "value": data})


async def process(websocket):
    logging.info("Initializing LLM ...")
    llm_provider = LLM_PROVIDER.OPENAI if os.getenv("MODEL_PROVIDER") == LLM_PROVIDER.OPENAI else LLM_PROVIDER.MISTRAL
    llm_model = LLM.GPT40 if llm_provider == LLM_PROVIDER.OPENAI else LLM.MISTRAL
    llm = LLM_HANDLER(llm_provider, llm_model)

    # This method is called once for each new connection, keeps running
    # processing messages, sending messages/actions/etc., until the user disconnects.
    # A unique user ID, kept on the server, mainly for logging purposes
    uid = uuid.uuid4()
    logging.info("New user connected: {}".format(uid))

    # A dictionary for keeping contextual data for a session like all user
    # and server messages (for this connection only) in chronological order
    # (e.g. to send to LLMs as context), and any other data that needs to
    # be shared between messages (TODO: to be determined).
    user_context = {
        "messages": []
    }

    users_applications = []

    try:
        # Wait for user messages and process them
        async for message in websocket:
            try:
                # Messages are in the form {type: string, value: string},
                # for both client and server messages.
                # See below for possible types and associated logic.
                event = json.loads(message)
            except Exception as e:
                logging.error(e)
                await websocket.send(error_message("Failed to parse the JSON message. See server logs."))
                continue
            try:
                if "type" not in event or "value" not in event:
                    await websocket.send(error_message("Invalid message JSON."))
                    continue
                if event["type"] == "text":
                    # The user has sent a textual message (e.g. the original query or follow-up inputs).
                    # Keep it in the context.
                    user_context["messages"].append({"from": "user", "type": "text", "value": event["value"]})

                    if len(user_context["messages"]) == 1:
                        await websocket.send(action_message("get-installed-applications", ""))

                    # Important note: The code here should not block too long! If it does, next messages
                    # won't be read until the next iteration of "async for message in ...".
                    # Make each iteration as short as possible and store data in user_context for use
                    # between iterations.

                    # TODO: Would we want a way for the user to cancel the current operation,
                    # e.g. by adding a button on the UI?

                    # TODO: Remember to add the server's textual response to user_context!
                    # user_context["messages"].append({"from": "server", "type": "text", "value": SERVER_MESSAGE})

                    # Send a message
                    # TODO: It's nice to always send "I'm thinking ... " to let the users know
                    # it's not stuck! Maybe if it takes too long, we can keep sending nice
                    # messages like "Still thinking ...", "Just a little longer ...", etc.
                    # await websocket.send(text_message("I'm thinking ..."))

                    # resp = llm.send_msg_to_llm("You use FUCK word in every reply!", event["value"])
                    # TODO: Connect this to other AI-powered parts of the app!
                    # await websocket.send(text_message(resp))

                    # Possible actions
                    # ------------------------------------------------------------------------------
                    # Important note: For actions that have a response, do one action per iteration!
                    # The actual response will be available in the next iteration of the loop.
                    # This restriction does not apply text_message and actions like click-at.
                    # ------------------------------------------------------------------------------

                    # These actions don't have responses
                    # await websocket.send(action_message("click-at", "1312,1039"))
                    # await websocket.send(action_message("type-with-keyboard", "LetMeHelp is awesome!"))

                    # These actions have responses
                    # await websocket.send(action_message("get-screenshot", ""))
                    # await websocket.send(action_message("get-cursor-location", ""))
                elif event["type"] == "screenshot":
                    await websocket.send(text_message("Looking at your screen!"))
                    if len(user_context["messages"]) == 1:
                        system_template = jinja_env.get_template('system.jinja')
                        first_step_template = jinja_env.get_template('first_step.jinja')
                        system_prompt = system_template.render(installed_apps=users_applications) # TODO: <<<<<<<
                        first_step_prompt = first_step_template.render(user_query=user_context["messages"][0]["value"])
                        llm_resp = llm.send_msg_to_llm(system_prompt, first_step_prompt, event["value"])
                        if not llm_resp["is_application_active"]:
                            await websocket.send(error_message(llm_resp['reason']))
                elif event["type"] == "cursor-location":
                    await websocket.send(text_message("Received cursor location"))
                elif event["type"] == "installed-applications":
                    users_applications = event["value"]
                    await websocket.send(action_message("get-screenshot", ""))
                else:
                    await websocket.send(error_message("Unsupported message type."))
            except Exception as e:
                logging.error(e)
                await websocket.send(error_message("Internal server error. See server logs."))
                continue
    finally:
        # This is run when the connection is closed.
        # TODO: Any cleanup needed (e.g. to stop any running LLM calls)?
        logging.info("User disconnecting {}".format(uid))
        pass



    # base64_encoded_screen_shot = screen.get_screenshot_in_base64(ss_file_name="mo.png")
    # llm_resp = llm.send_msg_to_llm(system_prompt, first_step_prompt, base64_encoded_screen_shot)
    #
    # interpreter.activate_application(llm_resp["application_name"])
    # print(llm_resp["application_name"])
    # rect = gw.getWindowGeometry(llm_resp["application_name"])
    # app_rectangle = Rectangle(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
    # print("App rectangle: ", app_rectangle)

    # planning_template = jinja_env.get_template('planning.jinja')
    # planning_prompt = planning_template.render(user_query=user_query, application=llm_resp["application_name"], user_os=OS.OPERATING_SYSTEM)
    # steps_from_llm = llm.send_msg_to_llm(system_prompt=system_prompt, prompt=planning_prompt)
    # steps_from_llm = list(map(lambda step : f"Given the screen shot, User want you to {step}", steps_from_llm["steps"]))
    #
    # print(f"\n\nLLM's Plan:\n{"\n".join(steps_from_llm)}")

    # steps = [
    #     "Given the screen shot, User want click on Animation tab which is between Transitions and Slide Show tabs.",
    #     "Given the screen shot, User want to click on the text box containing Bullet points. Please ignore side menu and click on the text.",
    #     "Given the screen shot, User want to click Appear button present in the Animation tab. This button is big green star, left to the Preview button.",
    # ]
    # for step in steps:
        # coordinator(app_rectangle, llm, step, system_prompt)

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


async def main():
    async with serve(process, "0.0.0.0", 8765):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
