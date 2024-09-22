
import sys
import click

from baserat import screen

@click.command()
def main(args=None) -> int:
    click.echo("Replace this message by putting your code into "
               "baserat.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")

    cont = True
    while cont:
        print("taking ss")
        screen.get_screenshot_in_base64()
        print("done")
        input()

    return 0


if __name__ == "__main__":
    sys.exit(main())
