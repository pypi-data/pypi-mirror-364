# src/rest_encrypt/cli.py
"""Command line interface for ``rest-encrypt``."""

import argparse
import sys
from pathlib import Path

from .store import SecretStore
from .platforms import DPAPIScope


def main() -> None:
    """Entry point for the ``rest-encrypt`` command line tool."""

    p = argparse.ArgumentParser(prog="rest-encrypt")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--secrets-path", required=True)
    common.add_argument("--wrapped-key-path", required=True)
    common.add_argument(
        "--scope",
        choices=[DPAPIScope.USER, DPAPIScope.MACHINE],
        default=DPAPIScope.USER,
    )
    common.add_argument("--serializer", "--format", default="json")
    common.add_argument(
        "--passphrase-path",
        help="Linux only: path to passphrase file",
        default="/etc/rest-encrypt/passphrase",
    )

    # init
    sp = sub.add_parser("init", parents=[common])
    sp.add_argument("--from-file", help="plaintext secrets file")
    sp.add_argument("--stdin", action="store_true")

    # load
    sp = sub.add_parser("load", parents=[common])
    sp.add_argument("--print", action="store_true")

    # env-run
    sp = sub.add_parser("env-run", parents=[common])
    sp.add_argument("cmd_and_args", nargs=argparse.REMAINDER)

    # rotate
    sub.add_parser("rotate-key", parents=[common])

    args = p.parse_args()

    store = SecretStore(
        args.secrets_path,
        args.wrapped_key_path,
        args.scope,
        serializer=args.serializer,
        passphrase_path=args.passphrase_path,
    )

    if args.cmd == "init":
        if args.stdin:
            text = sys.stdin.read()
        elif args.from_file:
            text = Path(args.from_file).read_text()
        else:
            p.error("init requires --from-file or --stdin")

        data = store.serializer.loads(text)
        store.init_from_plain(data)

    elif args.cmd == "load":
        data = store.load()
        if args.print:
            print(store.serializer.dumps(data))

    elif args.cmd == "env-run":
        if not args.cmd_and_args:
            p.error("env-run needs a command")
        data = store.load()
        store.inject_env(data, scope="process")
        import subprocess

        subprocess.run(args.cmd_and_args)

    elif args.cmd == "rotate-key":
        store.rotate_data_key()


if __name__ == "__main__":
    main()
