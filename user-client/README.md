# User Client

## Development Environment

To start:

```shell
docker compose build
docker compose up -d
docker compose exec -it user-client /bin/bash
```

To stop:

```shell
docker compose down
```

## Package Executable

```shell
pyinstaller main.py --add-data assets:. --add-binary /usr/local/lib/libpython3.11.so.1.0:. --onefile
```

Once done, go to the `dist` folder and copy the `_internal/assets` folder next to the `main` binary.
Rename `main` to `letmehelp` for use in the test environment.