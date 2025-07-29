# SPDX-License-Identifier: LicenseRef-OQL-1.2

import sys
from unittest import mock
from PrintTolCalc import cli
import pytest
import subprocess


def test_cli_runs_without_error(capsys):
    test_args = ["prog", "--help"]
    with mock.patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.value.code == 0
        out = capsys.readouterr().out
        assert "usage" in out.lower()


def test_cli_version_output(capsys):
    test_args = ["prog", "--version"]
    with mock.patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.value.code == 0
        out = capsys.readouterr().out.strip()
        assert out.startswith("PrintTolCalc ")
        assert len(out.split()) == 2
        assert all(part.isdigit() for part in out.split()[1].split("."))


@pytest.mark.parametrize(
    "index,axis,bad_value,expected_message",
    [
        (0, "X", "a", "invalid float value"),
        (1, "Y", "b", "invalid float value"),
        (2, "Z", "c", "invalid float value"),
        (0, "X", "x", "invalid float value"),
        (1, "Y", "y", "invalid float value"),
        (2, "Z", "z", "invalid float value"),
    ],
)
def test_invalid_type_letters_cli(index, axis, bad_value, expected_message):
    expected = [20, 20, 20]
    measured = [20, 20, 20]

    if axis == "expected":
        expected[index] = bad_value
    else:
        measured[index] = bad_value

    test_args = [
        sys.executable,
        "-m",
        "PrintTolCalc.cli",
    ]

    if axis == "expected":
        test_args.append("--expected")
        test_args.extend(map(str, expected))
    else:
        test_args.append("--measured")
        test_args.extend(map(str, measured))

    result = subprocess.run(test_args, capture_output=True, text=True)

    assert result.returncode != 0
    assert expected_message in result.stderr
