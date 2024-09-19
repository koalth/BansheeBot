from argparse import ArgumentParser
from dotenv import load_dotenv

from core import BansheeBot

if __name__ == "__main__":
    parser = ArgumentParser(prog="BansheeBot")
    parser.add_argument(
        "-d",
        "--debug",
        dest="cogs",
        action="extend",
        nargs="*",
        help="run in debug mode",
    )

    args = parser.parse_args()
    debug = args.cogs is not None

    load_dotenv(".env")

    bot = BansheeBot()
    bot.run(debug=debug)
