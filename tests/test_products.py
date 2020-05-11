from pathlib import Path

from pvi import ChannelConfig, Group, Schema, Widget, cli

PILATUS_YAML = Path(__file__).parent / "pilatus.pvi.yaml"
EXPECTED = Path(__file__).parent / "expected"


def test_channels():
    pilatus_schema = Schema.load(PILATUS_YAML.parent, "pilatus")
    channel_tree = pilatus_schema.producer.produce_channels(pilatus_schema.components)
    assert len(channel_tree) == 1
    assert isinstance(channel_tree[0], Group)
    channels = channel_tree[0].children
    assert len(channels) == 7
    assert channels[0] == ChannelConfig(
        name="ThresholdEnergy",
        label="Threshold Energy",
        read_pv="$(P)$(R)ThresholdEnergy_RBV",
        write_pv="$(P)$(R)ThresholdEnergy",
        widget=Widget.TEXTINPUT,
        description="""Threshold energy in keV

camserver uses this value to set the discriminators in each pixel.
It is typically set to the incident x-ray energy ($(P)$(R)Energy),
but sometimes other values may be preferable.
""",
        display_form=None,
    )


def check_generation(tmp_path: Path, fname: str):
    cli.main(["generate", str(PILATUS_YAML), str(tmp_path / fname)])
    assert open(tmp_path / fname).read() == open(EXPECTED / fname).read()


def test_yaml(tmp_path: Path):
    check_generation(tmp_path, "pilatus.coniql.yaml")


def test_h(tmp_path: Path):
    check_generation(tmp_path, "pilatus_parameters.h")


def test_cpp(tmp_path: Path):
    check_generation(tmp_path, "pilatus_parameters.cpp")


def test_template(tmp_path: Path):
    check_generation(tmp_path, "pilatus_parameters.template")


def test_csv(tmp_path: Path):
    check_generation(tmp_path, "pilatus_parameters.csv")


def test_edl(tmp_path: Path):
    check_generation(tmp_path, "pilatus_parameters.edl")
