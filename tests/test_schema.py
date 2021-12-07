from pathlib import Path

import pytest
from typer.testing import CliRunner

from pvi import __version__
from pvi.__main__ import cli


def test_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0, result
    assert result.stdout == __version__ + "\n"


@pytest.mark.parametrize("schema", ["device", "producer", "formatter"])
def test_schemas(tmp_path, schema):
    tmp_file = tmp_path / f"pvi.{schema}.schema.json"
    result = CliRunner().invoke(cli, ["schema", str(tmp_file)])
    assert result.exit_code == 0, result
    expected = Path(__file__).parent.parent / "schemas" / f"pvi.{schema}.schema.json"
    assert tmp_file.read_text() == expected.read_text()
