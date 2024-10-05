import asyncio
import json
import logging
import uuid
import sys
import openai

from websockets.asyncio.server import serve

# Logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

# Server messages

# Display an error message to the user
def error_message(message):
    return json.dumps({"type": "error", "value": message})

# Display a textual message to the user
def text_message(message):
    return json.dumps({"type": "text", "value": message})

# Take an action (e.g. take a screenshot, click somewhere, type something, etc.)
def action_message(name, data):
    return json.dumps({"type": name, "value": data})

# Event handler
async def process(websocket):
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
                    await websocket.send(text_message("I'm thinking ..."))

                    # TODO: Connect this to other AI-powered parts of the app!
                    await websocket.send(text_message("Nothing to do for now. :)"))

                    # Possible actions
                    # ------------------------------------------------------------------------------
                    # Important note: For actions that have a response, do one action per iteration!
                    # The actual response will be available in the next iteration of the loop.
                    # This restriction does not apply text_message and actions like click-at.
                    # ------------------------------------------------------------------------------

                    # These actions don't have responses
                    # TODO: Add cmd + space and other combination presses
                    # await websocket.send(action_message("click-at", "1312,1039"))
                    # await websocket.send(action_message("type-with-keyboard", "LetMeHelp is awesome!"))

                    # These actions have responses
                    # await websocket.send(action_message("get-screenshot", ""))
                    # await websocket.send(action_message("get-cursor-location", ""))
                    # await websocket.send(action_message("get-installed-applications", ""))
                    # For the list of possible keys, see https://github.com/go-vgo/robotgo/blob/master/docs/keys.md
                    # await websocket.send(action_message("press-key-combo", {"key": "f4", "modifiers": ["alt"]}))
                    
                    # THIS IS IN PROGRESS: await websocket.send(action_message("get-running-applications", ""))
                elif event["type"] == "screenshot":
                    await websocket.send(text_message("Received the screenshot"))
                elif event["type"] == "cursor-location":
                    await websocket.send(text_message("Received cursor location"))
                elif event["type"] == "installed-applications":
                    await websocket.send(text_message("Received list of installed applications"))
                elif event["type"] == "running-applications":
                    await websocket.send(text_message("Received list of running applications"))
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


async def main():
    async with serve(process, "0.0.0.0", 8765):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":

    asyncio.run(main())
