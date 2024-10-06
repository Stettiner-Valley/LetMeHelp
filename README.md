# LetMeHelp

## On-Demand AI-Powered Remote Support

An AI-powered solution to automatically perform actions on the computer based on the user query.

![](assets/letmehelp.jpg)

A project by [Mohammad Tomaraei](https://tomaraei.com) and [Maqbool ur Rahim Khan](https://www.maqboolurrahim.com/).

## [Google Slides Presentation](https://docs.google.com/presentation/d/1ejqZSFOikY8LfFfq9ocV9vMR6dUskckhHZTmvVDIW4E/edit#slide=id.g3068a5e32e5_0_69)

## Why did we make it?

* It’s a real problem we have (we're constantly approached by family and friends to solve their IT problems)
* We wanted to challenge ourselves, learn more about the current state of AI and cross-platform development, and do it as part of an AI Hackathon in Berlin (**we got selected as finalists out of 27 teams! 🚀**)
* Personal and enterprise use cases
* On-demand remote support is a big market
* Current solutions are not really feasible
  * No consumer product like LetMeHelp available yet
  * Not intuitive for non-developers
  * Hard to set up
  * Platform-specific
  * Limited capabilities

## How does it work?

Very simple! It has a cross-platform user client that talks to the API on a server with access to a visual large language model (VLLM).

![alt text](assets/how-to.png)

## [User Client](user-client/README.md)

* Cross-platform
* Lightweight
* Simple
* Capabilities
    * Call system APIs
    * See the screen
    * Click anywhere
    * Type anything

![](assets/screenshot.png)

## What have we learned from this project?

* There's a market gap for such a product (promising startup idea)
* Emerging research field
* VLMs are not good at locating UI elements yet
* VLMs downscale screenshots
* Hallucination is a problem
* Self-ask and reflection can help
* Don’t give all power to AI
* User experience matters most
* Fail fast
* SOTA research is all you need


## Getting Started

Our aim has been to Dockerize every component of this project, but this is a work in progress due to compatibility issues with different platforms. On Windows and Mac, we recommend installing dependencies and run the server and client directly from your machine.

The following are the development dependencies, but once compiled, the client is a single binary for Windows, Linux, and Mac:

* Python 3 (see `pyproject.toml` files for specific version requirements)
* Poetry
* Wails (see [their installation guide here](https://wails.io/docs/gettingstarted/installation))
  * Golang (1.22 or newer)
  * Node.js (12 or newer)
  * WebView2 (latest version)
  * On Windows, you might also require [tdm-gcc](https://jmeubank.github.io/tdm-gcc/download/)
  * Use `wails doctor` to diagnose issues

Start by cloning the project:

```
git clone https://github.com/Stettiner-Valley/LetMeHelp.git
```

The [test server](server/) is a simple Python script to create a WebSocket server and test the capabilities of the user client, such as receiving the user query and followup text messages, executing commands, and retrieving the data returned by commands.

To run the test server, open a terminal, navigate to `server/src/server`, run `poetry install`, and finally `poetry run python -m server`. The WebSocket server will be listening on `0.0.0.0:8765`. Take a look at the comments in `__main__.py` and add your own commands to test bi-directional communication with the client.

You can also try running the LLM-powered server, but this is a work in progress. See the [baserat](baserat) directory. To run it, either use `make run` or `poetry run python baserat/main.py`.

To run the user client, open a terminal, navigate to `user-client/src/letmehelp`, and run `wails dev`. The client takes a few seconds to build, and will automatically reload when you make a change. See [Wails Docs](https://wails.io/docs/introduction) for more info.

## Roadmap

- Assess the feasibility of the idea ✅
- Research similar projects and SOTA AI papers ✅
- Define a concrete sample use case (adding animation to PowerPoint) ✅
- Create a cross-platform user-client 🛠️
  - Some actions are not yet implemented for some platforms (see `user-client/src/letmehelp/app.go`)
- Create a test WebSocket server to showcase client features ✅
- Experiment with using GPT-4o and sample screenshots to create an MVP of the sample use case ✅
  - See the demo video here: https://www.youtube.com/watch?v=vYXPqMt-mx0
- Integrate the server in the MVP AI-powered engine (Baserat) 🛠️
- Write blog posts about our experiences working on this project 🛠️
- Create a Dockerized test environment to spin up Debian with XFCE, LibreOffice Impress, a web-based VNC viewer, and automatically open PowerPoint and the user client ✅

## [Test Environment](test-environment/README.md)

## [Test Server](server/README.md)

## [Server / AI Engine (WIP)](baserat/README.md)

## Contributing

If you'd like to contribute to our project, feel free to open a pull request :)
