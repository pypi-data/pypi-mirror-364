"""Tests for unicycler.py."""

import json
from decimal import Decimal
from pathlib import Path
from unittest import TestCase

import pytest
from defusedxml import ElementTree
from pydantic import ValidationError

from aurora_cycler_manager.unicycler import (
    ConstantCurrent,
    ConstantVoltage,
    Loop,
    MeasurementParams,
    OpenCircuitVoltage,
    Protocol,
    SafetyParams,
    SampleParams,
    Tag,
    from_dict,
    from_json,
)


class TestUnicycler(TestCase):
    """Unit tests for the unicycler module."""

    def setUp(self) -> None:
        """Set up for the tests."""
        base_folder = Path(__file__).parent / "test_data" / "protocols"
        self.example_protocol_paths = [
            base_folder / "test_protocol.json",
            base_folder / "test_protocol_placeholder_sample.json",
            base_folder / "test_protocol_no_sample.json",
            base_folder / "test_protocol_with_floats.json",
        ]
        data = []
        for path in self.example_protocol_paths:
            with path.open("r") as f:
                data.append(json.load(f))
        self.example_protocol_data = data

    def test_from_json(self) -> None:
        """Test creating a Protocol instance from a JSON file."""
        protocol = from_json(self.example_protocol_paths[0])
        assert isinstance(protocol, Protocol)
        assert protocol.sample.name == "test_sample"
        assert protocol.sample.capacity_mAh == Decimal("123")
        assert len(protocol.method) == 15
        assert isinstance(protocol.method[0], OpenCircuitVoltage)
        assert isinstance(protocol.method[1], ConstantCurrent)
        assert isinstance(protocol.method[2], OpenCircuitVoltage)
        assert isinstance(protocol.method[3], ConstantCurrent)
        assert isinstance(protocol.method[4], ConstantVoltage)
        assert isinstance(protocol.method[5], ConstantCurrent)
        assert isinstance(protocol.method[6], Loop)

    def test_from_dict(self) -> None:
        """Test creating a Protocol instance from a dictionary."""
        protocol_from_dict = from_dict(self.example_protocol_data[0])
        protocol_from_file = from_json(self.example_protocol_paths[0])
        assert protocol_from_dict == protocol_from_file

    def test_check_sample_details(self) -> None:
        """Test handling of missing sample details."""
        missing_name_msg = (
            "If using blank sample name or $NAME placeholder, a sample name must be provided in this function."
        )
        protocol = from_dict(self.example_protocol_data[1])
        with pytest.raises(ValueError) as context:
            protocol.to_neware_xml()
        assert str(context.value) == missing_name_msg
        protocol = from_dict(self.example_protocol_data[2])
        with pytest.raises(ValueError) as context:
            protocol.to_neware_xml()
        assert str(context.value) == missing_name_msg

        missing_cap_msg = "Sample capacity must be set if using C-rate steps."
        protocol = from_dict(self.example_protocol_data[1], sample_name="test_sample")
        with pytest.raises(ValueError) as context:
            protocol.to_neware_xml()
        assert str(context.value) == missing_cap_msg
        protocol = from_dict(self.example_protocol_data[2], sample_name="test_sample")
        with pytest.raises(ValueError) as context:
            protocol.to_neware_xml()
        assert str(context.value) == missing_cap_msg

        # should not raise error if both are provided
        protocol1 = from_dict(self.example_protocol_data[1], sample_name="test_sample", sample_capacity_mAh=123)
        protocol2 = from_dict(self.example_protocol_data[2], sample_name="test_sample", sample_capacity_mAh=123)
        protocol1.to_neware_xml()
        protocol2.to_neware_xml()
        assert protocol1.sample.name == "test_sample"
        assert protocol1.sample.capacity_mAh == Decimal("123")
        assert protocol1 == protocol2

    def test_overwriting_sample_details(self) -> None:
        """Test overwriting sample details when creating from a dictionary."""
        protocol = from_dict(self.example_protocol_data[0], sample_name="NewName", sample_capacity_mAh=456)
        assert protocol.sample.name == "NewName"
        assert protocol.sample.capacity_mAh == Decimal("456")

    def test_to_neware_xml(self) -> None:
        """Test converting a Protocol instance to Neware XML format."""
        protocol = from_dict(self.example_protocol_data[0])
        xml_string = protocol.to_neware_xml()
        assert isinstance(xml_string, str)
        assert xml_string.startswith("<?xml")
        assert "<config" in xml_string
        # read the xml to element tree
        root = ElementTree.fromstring(xml_string)
        assert root.tag == "root"
        config = root.find("config")
        assert config is not None
        assert config.attrib["type"] == "Step File"
        assert config.attrib["client_version"].startswith("BTS Client")
        assert config.find("Head_Info") is not None
        assert config.find("Whole_Prt") is not None
        assert config.find("Whole_Prt/Protect") is not None
        assert config.find("Whole_Prt/Record") is not None
        step_info = config.find("Step_Info")
        assert step_info is not None
        assert step_info.attrib["Num"] == str(len(protocol.method) + 1)  # +1 for 'End' step added for Neware
        assert len(step_info) == int(step_info.attrib["Num"])

    def test_to_tomato_mpg2(self) -> None:
        """Test converting a Protocol instance to Tomato MPG2 format."""
        protocol = from_dict(self.example_protocol_data[0])
        json_string = protocol.to_tomato_mpg2()
        assert isinstance(json_string, str)
        tomato_dict = json.loads(json_string)
        assert all(k in tomato_dict for k in ["version", "sample", "method", "tomato"])
        assert isinstance(tomato_dict["method"], list)
        assert len(tomato_dict["method"]) == len(protocol.method)
        assert tomato_dict["method"][0]["device"] == "MPG2"
        assert tomato_dict["method"][0]["technique"] == "open_circuit_voltage"
        assert tomato_dict["method"][1]["technique"] == "constant_current"
        assert tomato_dict["method"][2]["technique"] == "open_circuit_voltage"
        assert tomato_dict["method"][3]["technique"] == "constant_current"
        assert tomato_dict["method"][4]["technique"] == "constant_voltage"
        assert tomato_dict["method"][5]["technique"] == "constant_current"
        assert tomato_dict["method"][6]["technique"] == "loop"

    def test_to_pybamm_experiment(self) -> None:
        """Test converting a Protocol instance to PyBaMM experiment format."""
        protocol = from_dict(self.example_protocol_data[0])
        experiment_list = protocol.to_pybamm_experiment()
        assert isinstance(experiment_list, list)
        assert len(experiment_list) > 0
        assert isinstance(experiment_list[0], str)
        assert experiment_list[0].startswith("Rest for")
        assert experiment_list[1].startswith("Charge at")
        assert experiment_list[2].startswith("Rest for")
        assert experiment_list[3].startswith("Charge at")
        assert experiment_list[4].startswith("Hold at")
        assert experiment_list[5].startswith("Discharge at")
        assert experiment_list[6].startswith("Charge at")  # no 'loop' in pybamm experiment

    def test_constant_current_validation(self) -> None:
        """Test validation of ConstantCurrent technique."""
        with pytest.raises(ValueError):
            # Missing rate_C and current_mA
            ConstantCurrent(name="constant_current")
        with pytest.raises(ValueError):
            # rate_C and current_mA are zero
            ConstantCurrent(name="constant_current", rate_C=0, current_mA=0)
        with pytest.raises(ValueError):
            # Missing stop condition
            ConstantCurrent(name="constant_current", rate_C=0.1)
        with pytest.raises(ValueError):
            # stop conditions are zero
            ConstantCurrent(name="constant_current", rate_C=0.1, until_time_s=0, until_voltage_V=0)
        cc = ConstantCurrent(name="constant_current", rate_C=0.1, until_voltage_V=4.2)
        assert isinstance(cc, ConstantCurrent)

    def test_constant_voltage_validation(self) -> None:
        """Test validation of ConstantVoltage technique."""
        with pytest.raises(ValueError):
            # Missing stop condition
            ConstantVoltage(name="constant_voltage", voltage_V=4.2)
        with pytest.raises(ValueError):
            # stop conditions are zero
            ConstantVoltage(name="constant_voltage", voltage_V=4.2, until_time_s=0, until_rate_C=0, until_current_mA=0)
        cv = ConstantVoltage(name="constant_voltage", voltage_V=4.2, until_rate_C=0.05)
        assert isinstance(cv, ConstantVoltage)

    def test_protocol_c_rate_validation(self) -> None:
        """Test validation of Protocol with C-rate steps."""
        # Valid protocol
        protocol = from_dict(self.example_protocol_data[0])
        assert isinstance(protocol, Protocol)

        # Invalid protocol (missing capacity)
        protocol.sample.capacity_mAh = Decimal(0)
        with pytest.raises(ValueError) as context:
            protocol.to_neware_xml()
        assert str(context.value) == "Sample capacity must be set if using C-rate steps."

    def test_loop_validation(self) -> None:
        """Test validation of Loop technique."""
        with pytest.raises(ValueError):
            Loop(name="loop", start_step=0, cycle_count=1)  # start_step is zero
        with pytest.raises(ValueError):
            Loop(name="loop", start_step=1, cycle_count=0)  # cycle_count is zero
        loop = Loop(name="loop", start_step=1, cycle_count=1)
        assert isinstance(loop, Loop)

    def test_create_protocol(self) -> None:
        """Test creating a Protocol instance from a dictionary."""
        protocol = from_dict(self.example_protocol_data[0])
        protocol = Protocol(
            sample=SampleParams(
                name="test_sample",
                capacity_mAh=123,
            ),
            measurement=MeasurementParams(
                time_s=Decimal(10),
                voltage_V=0.1,
                current_mA="0.1",
            ),
            safety=SafetyParams(
                max_current_mA=10,
                min_current_mA=-10,
                max_voltage_V=5,
                min_voltage_V=-0.1,
                delay_s=10,
            ),
            method=[
                OpenCircuitVoltage(
                    until_time_s=60 * 60,
                ),
                ConstantCurrent(
                    rate_C=1 / 10,
                    until_time_s=60 * 10,
                    until_voltage_V=2,
                ),
                OpenCircuitVoltage(
                    until_time_s=60 * 60 * 12,
                ),
                ConstantCurrent(
                    rate_C=0.1,
                    until_time_s=60 * 60 * 1 / 0.1 * 1.5,
                    until_voltage_V=4.9,
                ),
                ConstantVoltage(
                    voltage_V=4.9,
                    until_rate_C=0.01,
                    until_time_s=60 * 60 * 6,
                ),
                ConstantCurrent(
                    rate_C=-0.1,
                    until_time_s=60 * 60 * 1 / 0.1 * 1.5,
                    until_voltage_V=3.5,
                ),
                Loop(
                    start_step=4,
                    cycle_count=3,
                ),
            ],
        )
        protocol_dict = json.loads(protocol.model_dump_json())
        assert protocol_dict["sample"]["name"] == "test_sample"
        # Should be able to be parsed into other formats
        protocol.to_neware_xml()
        protocol.to_tomato_mpg2()
        protocol.to_pybamm_experiment()
        protocol.to_eclab_settings()

    def test_tags(self) -> None:
        """Test tags in Protocol."""
        protocol = Protocol(
            measurement=MeasurementParams(time_s=1),
            safety=SafetyParams(),
            method=[
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=1),
                Loop(start_step=2, cycle_count=3),
            ],
        )
        protocol.tag_to_indices()
        # this should not change the loop step
        assert isinstance(protocol.method[4], Loop)
        assert protocol.method[4].start_step == 2

        protocol = Protocol(
            measurement=MeasurementParams(time_s=1),
            safety=SafetyParams(),
            method=[
                OpenCircuitVoltage(until_time_s=1),  # 0
                OpenCircuitVoltage(until_time_s=1),  # 1
                Tag(tag="tag1"),
                OpenCircuitVoltage(until_time_s=1),  # 2
                OpenCircuitVoltage(until_time_s=1),  # 3
                Loop(start_step="tag1", cycle_count=3),  # 4
                OpenCircuitVoltage(until_time_s=1),  # 5
                Loop(start_step=3, cycle_count=3),  # 6
            ],
        )
        # tag should be removed and replaced with the index
        protocol.tag_to_indices()
        assert isinstance(protocol.method[4], Loop)
        assert protocol.method[4].start_step == 3
        assert isinstance(protocol.method[6], Loop)
        assert protocol.method[6].start_step == 3

        protocol = Protocol(
            measurement=MeasurementParams(time_s=1),
            safety=SafetyParams(),
            method=[
                OpenCircuitVoltage(until_time_s=1),  # 0
                OpenCircuitVoltage(until_time_s=1),  # 1
                Tag(tag="tag1"),
                OpenCircuitVoltage(until_time_s=1),  # 2
                Tag(tag="tag2"),
                OpenCircuitVoltage(until_time_s=1),  # 3
                Loop(start_step="tag1", cycle_count=3),  # 4
                OpenCircuitVoltage(until_time_s=1),  # 5
                Loop(start_step=6, cycle_count=3),  # 6
                Tag(tag="tag3"),
                OpenCircuitVoltage(until_time_s=1),  # 7
                Loop(start_step="tag2", cycle_count=3),  # 8
                OpenCircuitVoltage(until_time_s=1),  # 9
                OpenCircuitVoltage(until_time_s=1),  # 10
                Loop(start_step="tag1", cycle_count=3),  # 11
                Tag(tag="tag that doesnt do anything"),
                Loop(start_step="tag3", cycle_count=3),  # 12
            ],
        )
        protocol.tag_to_indices()
        assert isinstance(protocol.method[4], Loop)
        assert protocol.method[4].start_step == 3
        assert isinstance(protocol.method[6], Loop)
        assert protocol.method[6].start_step == 4
        assert isinstance(protocol.method[8], Loop)
        assert protocol.method[8].start_step == 4
        assert isinstance(protocol.method[11], Loop)
        assert protocol.method[11].start_step == 3
        assert isinstance(protocol.method[12], Loop)
        assert protocol.method[12].start_step == 8

        # You should not be able to create a loop with a tag that does not exist
        with pytest.raises(ValidationError):
            protocol = Protocol(
                measurement=MeasurementParams(time_s=1),
                safety=SafetyParams(),
                method=[
                    OpenCircuitVoltage(until_time_s=1),
                    OpenCircuitVoltage(until_time_s=1),
                    OpenCircuitVoltage(until_time_s=1),
                    OpenCircuitVoltage(until_time_s=1),
                    Loop(start_step="this tag does not exist", cycle_count=3),
                ],
            )

        # Loops cannot go forwards
        with pytest.raises(ValidationError):
            protocol = Protocol(
                measurement=MeasurementParams(time_s=1),
                safety=SafetyParams(),
                method=[
                    OpenCircuitVoltage(until_time_s=1),
                    Loop(start_step="tag1", cycle_count=3),
                    OpenCircuitVoltage(until_time_s=1),
                    Tag(tag="tag1"),
                ],
            )

        # Loops cannot go forwards or land on themselves
        for i in [4, 5]:
            with pytest.raises(ValidationError):
                protocol = Protocol(
                    measurement=MeasurementParams(time_s=1),
                    safety=SafetyParams(),
                    method=[
                        OpenCircuitVoltage(until_time_s=1),
                        OpenCircuitVoltage(until_time_s=1),
                        OpenCircuitVoltage(until_time_s=1),
                        Loop(start_step=i, cycle_count=3),
                        OpenCircuitVoltage(until_time_s=1),
                        OpenCircuitVoltage(until_time_s=1),
                        OpenCircuitVoltage(until_time_s=1),
                    ],
                )

        # Loops cannot go back to one index to a tag
        with pytest.raises(ValidationError):
            protocol = Protocol(
                measurement=MeasurementParams(time_s=1),
                safety=SafetyParams(),
                method=[
                    OpenCircuitVoltage(until_time_s=1),
                    Tag(tag="tag1"),
                    Loop(start_step="tag1", cycle_count=3),
                    OpenCircuitVoltage(until_time_s=1),
                ],
            )

    def test_tag_neware(self) -> None:
        """Test tags in Neware XML."""
        protocol = Protocol(
            measurement=MeasurementParams(time_s=1),
            safety=SafetyParams(),
            method=[
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=1),
                Tag(tag="tag1"),
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=1),
                Loop(start_step="tag1", cycle_count=3),
            ],
        )
        xml_string = protocol.to_neware_xml(sample_name="test")
        neware_ET = ElementTree.fromstring(xml_string)
        loopstep = neware_ET.find("config/Step_Info/Step5")
        assert loopstep.attrib["Step_Type"] == "5"
        start_step = loopstep.find("Limit/Other/Start_Step")
        assert start_step.attrib["Value"] == "3"

        protocol1 = Protocol(
            measurement=MeasurementParams(time_s=1),
            safety=SafetyParams(),
            method=[
                OpenCircuitVoltage(until_time_s=1),
                Tag(tag="tag1"),
                OpenCircuitVoltage(until_time_s=2),
                Tag(tag="tag2"),
                OpenCircuitVoltage(until_time_s=3),
                OpenCircuitVoltage(until_time_s=4),
                OpenCircuitVoltage(until_time_s=5),
                Loop(start_step="tag2", cycle_count=3),
                OpenCircuitVoltage(until_time_s=6),
                Loop(start_step="tag1", cycle_count=5),
                OpenCircuitVoltage(until_time_s=7),
            ],
        )

        protocol2 = Protocol(
            measurement=MeasurementParams(time_s=1),
            safety=SafetyParams(),
            method=[
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=2),
                OpenCircuitVoltage(until_time_s=3),
                OpenCircuitVoltage(until_time_s=4),
                OpenCircuitVoltage(until_time_s=5),
                Loop(start_step=3, cycle_count=3),
                OpenCircuitVoltage(until_time_s=6),
                Loop(start_step=2, cycle_count=5),
                OpenCircuitVoltage(until_time_s=7),
            ],
        )
        neware1 = protocol1.to_neware_xml(sample_name="test")
        neware2 = protocol2.to_neware_xml(sample_name="test")
        # remove the date and uuid from the xml, starts with Guid=" and ends with "
        # use regex to remove it
        idx = neware1.find("date=")
        neware1 = neware1[:idx] + neware1[idx + 65 :]
        neware2 = neware2[:idx] + neware2[idx + 65 :]
        assert neware1 == neware2

    def test_to_eclab_settings(self) -> None:
        """Test conversion to ECLab settings."""
        protocol = Protocol(
            measurement=MeasurementParams(time_s=1),
            safety=SafetyParams(),
            method=[
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=1),
                Tag(tag="tag1"),
                OpenCircuitVoltage(until_time_s=1),
                OpenCircuitVoltage(until_time_s=1),
                Loop(start_step="tag1", cycle_count=3),
                Loop(start_step=4, cycle_count=3),
            ],
        )
        eclab_settings = protocol.to_eclab_settings(sample_name="test", capacity_mAh=1.0)
        # Find where the line begins with "ctrl_seq"
        lines = eclab_settings.splitlines()
        ctrl_seq_start = next((i for i, line in enumerate(lines) if line.startswith("ctrl_seq")), None)
        assert ctrl_seq_start is not None, "ctrl_seq not found in ECLab settings"
        test_str = (
            "ctrl_seq            0                   0                   0                   "
            "0                   2                   2                   "
        )
        assert lines[ctrl_seq_start] == test_str, "ctrl_seq line does not match expected"
