# Server

This is a web-socket server responsible for communicating with the user client, retrieving data, and executing commands.

## Workflow

1. Once a user client connects to the server, a session identified by a unique ID is created.
2. The user client then waits for the user to type their query and click Send.
3. Once the user query has been received, a loop is started on the server, in which it performs the 
following actions, one-at-a-time, until the goal has been achieved:
    * Use the LLM/VLM engine to process the user query
    * Display a message
    * Ask something from the user
    * Take a screenshot
    * Perform a click at a specific location
    * Get the current cursor position
    * Type something on the keyboard
    * End the session

## Development Environment

Use `rebuild.sh`, `start.sh`, and `stop.sh` to control the Dockerized development environment.

Once the server has been started, it is available at `localhost:8765` and `YOUR_NETWORK_IP:8765` if allowed by 
your firewall. Note that since it uses the web-socket protocol, it cannot be directly opened in the browser.

To test it, enter the address in the user client and start a session.

You can alternatively use an API testing tool like [Insomnia](https://github.com/Kong/insomnia).