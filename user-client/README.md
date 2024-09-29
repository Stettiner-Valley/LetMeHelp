# User Client

This is an Electron-like, web-based, and cross-platform user client written in Golang.

It uses the [Wails](https://wails.io/) Go library to package the Vue.js application, a local web server, and a Webkit
browser into a single executable.

## Development Environment

Use `rebuild.sh`, `start.sh`, and `stop.sh` to control the Dockerized development environment.

Once inside the container, go to the `~/src/letmehelp` directory and run `wails dev`.

**Note: `wails dev` requires access to X11. `docker-compose.yaml` is currently configured to bind X11, and therefore
expects the host machine to be running Linux. If you're not on Linux, consider editing `docker-compose.yaml`.
You can still build the Linux and Windows binaries without X11.**

The development web server will be available at http://localhost:34115/.

The front-end development server will be available at http://localhost:5173/.

Note that it takes a minute or two for the development server to finish compiling.

## Building Executables

Run the following in the `src/letmehelp` directory:

* Linux (x64): `wails build -platform linux/amd64`
* Windows (x64): `wails build -platform windows/amd64`

To enable debugging and devtools, pass `-debug` to the build command.

Binaries will be available under `src/letmehelp/build/bin`.
Copy the binary to `test-environment/opt`.

Since Wails does not support crosscompiling to Mac, `wails build -platform darwin/arm64` needs to be run
on a Mac host (not in the Dockerized development above).

See [Wails documentation](https://wails.io/docs/reference/cli#platforms) for more information.

## Notes

When using `wails dev`, the WebSocket connection may not work for `localhost:8765` (because it's running in a Docker
container, but thr server is running elsewhere).
To solve this, either build the binary and run, or use your internal IP address  (e.g. `192.168.X.X`).
We can also later create a `docker-compose.yaml` in the root of the project and run everything
at once, so that then we could call services via Docker's DNS (e.g. `server:8765`).