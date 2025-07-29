import json
import subprocess
import sys


def _setup_files(tmp_path):
    secrets = tmp_path / "secrets.enc"
    wrapped = tmp_path / "wrapped.key"
    passphrase = tmp_path / "pass"
    passphrase.write_text("pw")
    infile = tmp_path / "secrets.json"
    infile.write_text('{"foo":"bar"}')
    return secrets, wrapped, passphrase, infile


def test_cli_init_load_rotate(tmp_path):
    secrets, wrapped, passphrase, infile = _setup_files(tmp_path)

    subprocess.run([
        sys.executable,
        "-m",
        "rest_encrypt.cli",
        "init",
        "--secrets-path",
        str(secrets),
        "--wrapped-key-path",
        str(wrapped),
        "--from-file",
        str(infile),
        "--passphrase-path",
        str(passphrase),
    ], check=True)

    out = subprocess.run([
        sys.executable,
        "-m",
        "rest_encrypt.cli",
        "load",
        "--secrets-path",
        str(secrets),
        "--wrapped-key-path",
        str(wrapped),
        "--passphrase-path",
        str(passphrase),
        "--print",
    ], check=True, capture_output=True, text=True)
    assert json.loads(out.stdout) == {"foo": "bar"}

    subprocess.run([
        sys.executable,
        "-m",
        "rest_encrypt.cli",
        "rotate-key",
        "--secrets-path",
        str(secrets),
        "--wrapped-key-path",
        str(wrapped),
        "--passphrase-path",
        str(passphrase),
    ], check=True)

    out2 = subprocess.run([
        sys.executable,
        "-m",
        "rest_encrypt.cli",
        "load",
        "--secrets-path",
        str(secrets),
        "--wrapped-key-path",
        str(wrapped),
        "--passphrase-path",
        str(passphrase),
        "--print",
    ], check=True, capture_output=True, text=True)
    assert json.loads(out2.stdout) == {"foo": "bar"}


def test_cli_env_run(tmp_path):
    secrets, wrapped, passphrase, infile = _setup_files(tmp_path)

    subprocess.run([
        sys.executable,
        "-m",
        "rest_encrypt.cli",
        "init",
        "--secrets-path",
        str(secrets),
        "--wrapped-key-path",
        str(wrapped),
        "--from-file",
        str(infile),
        "--passphrase-path",
        str(passphrase),
    ], check=True)

    out = subprocess.run([
        sys.executable,
        "-m",
        "rest_encrypt.cli",
        "env-run",
        "--secrets-path",
        str(secrets),
        "--wrapped-key-path",
        str(wrapped),
        "--passphrase-path",
        str(passphrase),
        sys.executable,
        "-c",
        "import os,sys; sys.stdout.write(os.getenv('foo'))",
    ], check=True, capture_output=True, text=True)
    assert out.stdout == "bar"

