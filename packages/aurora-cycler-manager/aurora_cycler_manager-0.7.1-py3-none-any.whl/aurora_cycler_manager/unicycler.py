"""Copyright © 2025, Empa.

A universal cycling Protocol model to convert to different formats.

Protocol is a Pydantic model that defines a cycling protocol which can be stored/read in JSON format.
The model only contains a subset of all possible techniques and parameters.
This can be converted into a Neware XML file, Tomato JSON file, or PyBaMM list of strings with
to_neware_xml(), to_tomato_mpg2() and to_pybamm_experiment() methods respectively.
"""

import json
import uuid
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Annotated, Literal
from xml.dom import minidom

from pydantic import BaseModel, BeforeValidator, Field, field_validator, model_validator
from typing_extensions import Self

getcontext().prec = 10


def coerce_to_decimal(v: Decimal | float | str) -> Decimal | None:
    """Coerces input (int, float, str) to Decimal."""
    if v is None or v == "":
        return None
    if isinstance(v, float):
        return Decimal(str(v))  # Avoids float precision issues
    return Decimal(v)


PreciseDecimal = Annotated[Decimal | float | str, BeforeValidator(coerce_to_decimal)]


class SampleParams(BaseModel):
    """Sample parameters."""

    name: str = Field(default="$NAME")
    capacity_mAh: PreciseDecimal | None = Field(gt=0, default=None)

    model_config = {"extra": "forbid"}


class MeasurementParams(BaseModel):
    """Measurement parameters, i.e. when to record."""

    current_mA: PreciseDecimal | None = None
    voltage_V: PreciseDecimal | None = None
    time_s: PreciseDecimal = Field(gt=0)

    model_config = {"extra": "forbid"}


class SafetyParams(BaseModel):
    """Safety parameters, i.e. limits before cancelling measurement."""

    max_voltage_V: PreciseDecimal | None = None
    min_voltage_V: PreciseDecimal | None = None
    max_current_mA: PreciseDecimal | None = None
    min_current_mA: PreciseDecimal | None = None
    max_capacity_mAh: PreciseDecimal | None = None
    delay_s: PreciseDecimal = Field(ge=0, default=Decimal(0))

    model_config = {
        "extra": "forbid",
    }


class BaseTechnique(BaseModel):
    """Base class for all techniques."""

    name: str
    # optional id field
    id: str | None = Field(default=None, description="Optional ID for the technique step")
    model_config = {"extra": "forbid"}


class OpenCircuitVoltage(BaseTechnique):
    """Open circuit voltage technique."""

    name: Literal["open_circuit_voltage"] = "open_circuit_voltage"
    until_time_s: PreciseDecimal = Field(gt=0)


class ConstantCurrent(BaseTechnique):
    """Constant current technique."""

    name: Literal["constant_current"] = "constant_current"
    rate_C: PreciseDecimal | None = None
    current_mA: PreciseDecimal | None = None
    until_time_s: PreciseDecimal | None = None
    until_voltage_V: PreciseDecimal | None = None

    @model_validator(mode="after")
    def ensure_rate_or_current(self) -> Self:
        """Ensure at least one of rate_C or current_mA is set."""
        has_rate_C = self.rate_C is not None and self.rate_C != 0
        has_current_mA = self.current_mA is not None and self.current_mA != 0
        if not (has_rate_C or has_current_mA):
            msg = "Either rate_C or current_mA must be set and non-zero."
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def ensure_stop_condition(self) -> Self:
        """Ensure at least one stop condition is set."""
        has_time_s = self.until_time_s is not None and self.until_time_s != 0
        has_voltage_V = self.until_voltage_V is not None and self.until_voltage_V != 0
        if not (has_time_s or has_voltage_V):
            msg = "Either until_time_s or until_voltage_V must be set and non-zero."
            raise ValueError(msg)
        return self


class ConstantVoltage(BaseTechnique):
    """Constant voltage technique."""

    name: Literal["constant_voltage"] = "constant_voltage"
    voltage_V: PreciseDecimal
    until_time_s: PreciseDecimal | None = None
    until_rate_C: PreciseDecimal | None = None
    until_current_mA: PreciseDecimal | None = None

    @model_validator(mode="after")
    def check_stop_condition(self) -> Self:
        """Ensure at least one of until_rate_C or until_current_mA is set."""
        has_time_s = self.until_time_s is not None and self.until_time_s != 0
        has_rate_C = self.until_rate_C is not None and self.until_rate_C != 0
        has_current_mA = self.until_current_mA is not None and self.until_current_mA != 0
        if not (has_time_s or has_rate_C or has_current_mA):
            msg = "Either until_time_s, until_rate_C, or until_current_mA must be set and non-zero."
            raise ValueError(msg)
        return self


class Loop(BaseTechnique):
    """Loop technique."""

    name: Literal["loop"] = "loop"
    start_step: Annotated[int | str, Field()] = Field(default=1)
    cycle_count: int = Field(gt=0)
    model_config = {"extra": "forbid"}

    @field_validator("start_step")
    @classmethod
    def validate_start_step(cls, v: int | str) -> int | str:
        """Ensure start_step is a positive integer or a string."""
        if isinstance(v, int) and v <= 0:
            msg = "Start step must be positive integer or a string"
            raise ValueError(msg)
        if isinstance(v, str) and v.strip() == "":
            msg = "Start step cannot be empty"
            raise ValueError(msg)
        return v


class Tag(BaseTechnique):
    """Tag technique."""

    name: str = Field(default="tag", frozen=True)
    tag: str = Field(default="")

    model_config = {"extra": "forbid"}


AnyTechnique = BaseTechnique | ConstantCurrent | ConstantVoltage | OpenCircuitVoltage | Loop | Tag


# --- Main Protocol Model ---
class Protocol(BaseModel):
    """Protocol model which can be converted to various formats."""

    sample: SampleParams = Field(default_factory=SampleParams)
    measurement: MeasurementParams
    safety: SafetyParams
    method: Sequence[AnyTechnique] = Field(min_length=1)  # Ensure at least one step

    model_config = {"extra": "forbid"}

    # Only checked when outputting
    def _validate_capacity_c_rates(self) -> None:
        """Ensure if using C-rate steps, a capacity is set."""
        if not self.sample.capacity_mAh and any(
            getattr(s, "rate_C", None) or getattr(s, "until_rate_C", None) for s in self.method
        ):
            msg = "Sample capacity must be set if using C-rate steps."
            raise ValueError(msg)

    @model_validator(mode="after")
    def _validate_loops_and_tags(self) -> Self:
        """Ensure that if a loop uses a string, it is a valid tag."""
        loop_tags = {
            i: step.start_step
            for i, step in enumerate(self.method)
            if isinstance(step, Loop) and isinstance(step.start_step, str)
        }
        loop_idx = {
            i: step.start_step
            for i, step in enumerate(self.method)
            if isinstance(step, Loop) and isinstance(step.start_step, int)
        }
        tags = {i: step.tag for i, step in enumerate(self.method) if isinstance(step, Tag)}

        # Cannot have duplicate tags
        tag_list = list(tags.values())
        if len(tag_list) != len(set(tag_list)):
            duplicate_tags = {"'" + tag + "'" for tag in tag_list if tag_list.count(tag) > 1}
            msg = "Duplicate tags: " + ", ".join(duplicate_tags)
            raise ValueError(msg)

        tags_rev = {v: k for k, v in tags.items()}  # to map from tag to index

        # indexed loops cannot go on itself or forwards
        for i, loop_start in loop_idx.items():
            if loop_start >= i:
                msg = f"Loop start index {loop_start} cannot be on or after the loop index {i}."
                raise ValueError(msg)

        # Loops cannot go forwards to tags, or back one index to a tag
        for i, loop_tag in loop_tags.items():
            if loop_tag not in tags_rev:
                msg = f"Tag '{loop_tag}' is missing."
                raise ValueError(msg)
            # loop_tag is in tags, ensure i is larger than the tag index
            tag_i = tags_rev[loop_tag]
            if i <= tag_i:
                msg = f"Loops must go backwards, '{loop_tag}' goes forwards ({i}->{tag_i})."
                raise ValueError(msg)
            if i == tag_i + 1:
                msg = f"Loop '{loop_tag}' cannot start immediately after its tag."
                raise ValueError(msg)
        return self

    def tag_to_indices(self) -> None:
        """Convert tag steps into indices to be processed later."""
        # In a protocol the steps are 1-indexed and tags should be ignored
        # The loop function should point to the index of the step AFTER the corresponding tag
        indices = [0] * len(self.method)
        tags = {}
        methods_to_remove = []
        j = 0
        for i, step in enumerate(self.method):
            if isinstance(step, Tag):
                indices[i] = j + 1
                tags[step.tag] = j + 1
                # drop this step from the list
                methods_to_remove.append(i)
            elif isinstance(step, BaseTechnique):
                j += 1
                indices[i] = j
                if isinstance(step, Loop):
                    if isinstance(step.start_step, str):
                        # If the start step is a string, it should be a tag, go to the tag index
                        try:
                            step.start_step = tags[step.start_step]
                        except KeyError as e:
                            msg = f"Loop step with tag {step.start_step} does not have a corresponding tag step."
                            raise ValueError(msg) from e
                    else:
                        # If the start step is an int, it should be the NEW index of the step
                        step.start_step = indices[step.start_step - 1]
            else:
                methods_to_remove.append(i)
        # Remove tags and other invalid steps
        self.method = [step for i, step in enumerate(self.method) if i not in methods_to_remove]

    def to_neware_xml(
        self,
        save_path: Path | None = None,
        sample_name: str | None = None,
        capacity_mAh: Decimal | float | None = None,
    ) -> str:
        """Convert the protocol to Neware XML format."""
        # Allow overwriting name and capacity
        if sample_name:
            self.sample.name = sample_name
        if capacity_mAh:
            self.sample.capacity_mAh = Decimal(capacity_mAh)

        # Make sure sample name is set
        if not self.sample.name or self.sample.name == "$NAME":
            msg = "If using blank sample name or $NAME placeholder, a sample name must be provided in this function."
            raise ValueError(msg)

        # Make sure capacity is set if using C-rate steps
        self._validate_capacity_c_rates()

        # Remove tags and convert to indices
        self.tag_to_indices()

        # Create XML structure
        root = ET.Element("root")
        config = ET.SubElement(
            root,
            "config",
            type="Step File",
            version="17",
            client_version="BTS Client 8.0.0.478(2024.06.24)(R3)",
            date=datetime.now().strftime("%Y%m%d%H%M%S"),
            Guid=str(uuid.uuid4()),
        )
        head_info = ET.SubElement(config, "Head_Info")
        ET.SubElement(head_info, "Operate", Value="66")
        ET.SubElement(head_info, "Scale", Value="1")
        ET.SubElement(head_info, "Start_Step", Value="1", Hide_Ctrl_Step="0")
        ET.SubElement(head_info, "Creator", Value="aurora_cycler_manager.unicycler")
        ET.SubElement(head_info, "Remark", Value=self.sample.name)
        # 103, non C-rate mode, seems to give more precise values vs 105
        ET.SubElement(head_info, "RateType", Value="103")
        if self.sample.capacity_mAh:
            ET.SubElement(head_info, "MultCap", Value=f"{self.sample.capacity_mAh * 3600:f}")

        whole_prt = ET.SubElement(config, "Whole_Prt")
        protect = ET.SubElement(whole_prt, "Protect")
        main_protect = ET.SubElement(protect, "Main")
        volt = ET.SubElement(main_protect, "Volt")
        if self.safety.max_voltage_V:
            ET.SubElement(volt, "Upper", Value=f"{self.safety.max_voltage_V * 10000:f}")
        if self.safety.min_voltage_V:
            ET.SubElement(volt, "Lower", Value=f"{self.safety.min_voltage_V * 10000:f}")
        curr = ET.SubElement(main_protect, "Curr")
        if self.safety.max_current_mA:
            ET.SubElement(curr, "Upper", Value=f"{self.safety.max_current_mA:f}")
        if self.safety.min_current_mA:
            ET.SubElement(curr, "Lower", Value=f"{self.safety.min_current_mA:f}")
        if self.safety.delay_s:
            ET.SubElement(main_protect, "Delay_Time", Value=f"{self.safety.delay_s * 1000:f}")
        cap = ET.SubElement(main_protect, "Cap")
        if self.safety.max_capacity_mAh:
            ET.SubElement(cap, "Upper", Value=f"{self.safety.max_capacity_mAh * 3600:f}")

        record = ET.SubElement(whole_prt, "Record")
        main_record = ET.SubElement(record, "Main")
        if self.measurement.time_s:
            ET.SubElement(main_record, "Time", Value=f"{self.measurement.time_s * 1000:f}")
        if self.measurement.voltage_V:
            ET.SubElement(main_record, "Volt", Value=f"{self.measurement.voltage_V * 10000:f}")
        if self.measurement.current_mA:
            ET.SubElement(main_record, "Curr", Value=f"{self.measurement.current_mA:f}")

        step_info = ET.SubElement(config, "Step_Info", Num=str(len(self.method) + 1))  # +1 for end step

        def _step_to_element(step: AnyTechnique, step_num: int, parent: ET.Element) -> None:
            """Create XML subelement from protocol technique."""
            if isinstance(step, ConstantCurrent):
                if step.rate_C is not None and step.rate_C != 0:
                    step_type = "1" if step.rate_C > 0 else "2"
                elif step.current_mA is not None and step.current_mA != 0:
                    step_type = "1" if step.current_mA > 0 else "2"

                step_element = ET.SubElement(parent, f"Step{step_num}", Step_ID=str(step_num), Step_Type=step_type)
                limit = ET.SubElement(step_element, "Limit")
                main = ET.SubElement(limit, "Main")
                if step.rate_C is not None:
                    ET.SubElement(main, "Rate", Value=f"{abs(step.rate_C):f}")
                    ET.SubElement(main, "Curr", Value=f"{abs(step.rate_C) * self.sample.capacity_mAh:f}")
                elif step.current_mA is not None:
                    ET.SubElement(main, "Curr", Value=f"{abs(step.current_mA):f}")
                if step.until_time_s is not None:
                    ET.SubElement(main, "Time", Value=f"{step.until_time_s * 1000:f}")
                if step.until_voltage_V is not None:
                    ET.SubElement(main, "Stop_Volt", Value=f"{step.until_voltage_V * 10000:f}")

            elif isinstance(step, ConstantVoltage):
                if step.until_rate_C is not None and step.until_rate_C != 0:
                    step_type = "3" if step.until_rate_C > 0 else "19"
                elif step.until_current_mA is not None and step.until_current_mA != 0:
                    step_type = "3" if step.until_current_mA > 0 else "19"
                else:
                    step_type = "3"  # If it can't be figured out, default to charge
                step_element = ET.SubElement(parent, f"Step{step_num}", Step_ID=str(step_num), Step_Type=step_type)
                limit = ET.SubElement(step_element, "Limit")
                main = ET.SubElement(limit, "Main")
                ET.SubElement(main, "Volt", Value=f"{step.voltage_V * 10000:f}")
                if step.until_time_s is not None:
                    ET.SubElement(main, "Time", Value=f"{step.until_time_s * 1000:f}")
                if step.until_rate_C is not None:
                    ET.SubElement(main, "Stop_Rate", Value=f"{abs(step.until_rate_C):f}")
                    ET.SubElement(main, "Stop_Curr", Value=f"{abs(step.until_rate_C) * self.sample.capacity_mAh:f}")
                elif step.until_current_mA is not None:
                    ET.SubElement(main, "Stop_Curr", Value=f"{abs(step.until_current_mA):f}")

            elif isinstance(step, OpenCircuitVoltage):
                step_element = ET.SubElement(parent, f"Step{step_num}", Step_ID=str(step_num), Step_Type="4")
                limit = ET.SubElement(step_element, "Limit")
                main = ET.SubElement(limit, "Main")
                ET.SubElement(main, "Time", Value=f"{step.until_time_s * 1000:f}")

            elif isinstance(step, Loop):
                step_element = ET.SubElement(parent, f"Step{step_num}", Step_ID=str(step_num), Step_Type="5")
                limit = ET.SubElement(step_element, "Limit")
                other = ET.SubElement(limit, "Other")
                ET.SubElement(other, "Start_Step", Value=str(step.start_step))
                ET.SubElement(other, "Cycle_Count", Value=str(step.cycle_count))

            else:
                msg = f"to_neware_xml does not support step type: {step.name}"
                raise TypeError(msg)

        for i, technique in enumerate(self.method):
            step_num = i + 1
            _step_to_element(technique, step_num, step_info)

        # Add an end step
        step_num = len(self.method) + 1
        ET.SubElement(step_info, f"Step{step_num}", Step_ID=str(step_num), Step_Type="6")

        smbus = ET.SubElement(config, "SMBUS")
        ET.SubElement(smbus, "SMBUS_Info", Num="0", AdjacentInterval="0")

        # Convert to string and prettify it
        pretty_xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")  # noqa: S318
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with save_path.open("w", encoding="utf-8") as f:
                f.write(pretty_xml_string)
        return pretty_xml_string

    def to_tomato_mpg2(
        self,
        save_path: Path | None = None,
        tomato_output: Path = Path("C:/tomato_data/"),
        sample_name: str | None = None,
        capacity_mAh: Decimal | float | None = None,
    ) -> str:
        """Convert protocol to tomato 0.2.3 + MPG2 compatible JSON format."""
        # Allow overwriting name and capacity
        if sample_name:
            self.sample.name = sample_name
        if capacity_mAh:
            self.sample.capacity_mAh = Decimal(capacity_mAh)

        # Make sure sample name is set
        if not self.sample.name or self.sample.name == "$NAME":
            msg = "If using blank sample name or $NAME placeholder, a sample name must be provided in this function."
            raise ValueError(msg)

        # Make sure capacity is set if using C-rate steps
        self._validate_capacity_c_rates()

        # Remove tags and convert to indices
        self.tag_to_indices()

        # Create JSON structure
        tomato_dict: dict = {
            "version": "0.1",
            "sample": {},
            "method": [],
            "tomato": {
                "unlock_when_done": True,
                "verbosity": "DEBUG",
                "output": {
                    "path": str(tomato_output),
                    "prefix": self.sample.name,
                },
            },
        }
        # tomato -> MPG2 does not support safety parameters, they are set in the instrument
        tomato_dict["sample"]["name"] = self.sample.name
        tomato_dict["sample"]["capacity_mAh"] = self.sample.capacity_mAh
        for step in self.method:
            tomato_step: dict = {}
            tomato_step["device"] = "MPG2"
            tomato_step["technique"] = step.name
            if step.name in ["constant_current", "constant_voltage", "open_circuit_voltage"]:
                if self.measurement.time_s:
                    tomato_step["measure_every_dt"] = self.measurement.time_s
                if self.measurement.current_mA:
                    tomato_step["measure_every_dI"] = self.measurement.current_mA
                if self.measurement.voltage_V:
                    tomato_step["measure_every_dE"] = self.measurement.voltage_V
                tomato_step["I_range"] = "10 mA"
                tomato_step["E_range"] = "+-5.0 V"

            if isinstance(step, OpenCircuitVoltage):
                tomato_step["time"] = step.until_time_s

            elif isinstance(step, ConstantCurrent):
                if step.rate_C:
                    if step.rate_C > 0:
                        charging = True
                        tomato_step["current"] = str(step.rate_C) + "C"
                    else:
                        charging = False
                        tomato_step["current"] = str(abs(step.rate_C)) + "D"
                elif step.current_mA:
                    if step.current_mA > 0:
                        charging = True
                        tomato_step["current"] = step.current_mA / 1000
                    else:
                        charging = False
                        tomato_step["current"] = step.current_mA / 1000
                if step.until_time_s:
                    tomato_step["time"] = step.until_time_s
                if step.until_voltage_V:
                    if charging:
                        tomato_step["limit_voltage_max"] = step.until_voltage_V
                    else:
                        tomato_step["limit_voltage_min"] = step.until_voltage_V

            elif isinstance(step, ConstantVoltage):
                tomato_step["voltage"] = step.voltage_V
                if step.until_time_s:
                    tomato_step["time"] = step.until_time_s
                if step.until_rate_C:
                    if step.until_rate_C > 0:
                        tomato_step["limit_current_min"] = str(step.until_rate_C) + "C"
                    else:
                        tomato_step["limit_current_max"] = str(abs(step.until_rate_C)) + "D"

            elif isinstance(step, Loop):
                tomato_step["goto"] = step.start_step - 1  # 0-indexed in mpr
                tomato_step["n_gotos"] = step.cycle_count - 1  # gotos is one less than cycles

            else:
                msg = f"to_tomato_mpg2 does not support step type: {step.name}"
                raise TypeError(msg)

            tomato_dict["method"].append(tomato_step)

        def _json_serialize(obj: object) -> float:
            """Serialize Decimal objects."""
            if isinstance(obj, Decimal):
                return float(obj)
            msg = f"Type {type(obj)} not serializable"
            raise TypeError(msg)

        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with save_path.open("w", encoding="utf-8") as f:
                json.dump(tomato_dict, f, indent=4, default=_json_serialize)
        return json.dumps(tomato_dict, indent=4, default=_json_serialize)

    def to_pybamm_experiment(self) -> list[str]:
        """Convert protocol to PyBaMM experiment format."""
        # A PyBaMM experiment doesn't need capacity or sample name
        # Don't need to validate capacity if using C-rate steps

        # Remove tags and convert to indices
        self.tag_to_indices()

        pybamm_experiment: list[str] = []
        loops: dict[int, dict] = {}
        for i, step in enumerate(self.method):
            step_str = ""
            if isinstance(step, ConstantCurrent):
                if step.rate_C:
                    if step.rate_C > 0:
                        step_str += f"Charge at {step.rate_C}C"
                    else:
                        step_str += f"Discharge at {abs(step.rate_C)}C"
                elif step.current_mA:
                    if step.current_mA > 0:
                        step_str += f"Charge at {step.current_mA} mA"
                    else:
                        step_str += f"Discharge at {abs(step.current_mA)} mA"
                if step.until_time_s:
                    if step.until_time_s % 3600 == 0:
                        step_str += f" for {int(step.until_time_s / 3600)} hours"
                    elif step.until_time_s % 60 == 0:
                        step_str += f" for {int(step.until_time_s / 60)} minutes"
                    else:
                        step_str += f" for {step.until_time_s} seconds"
                if step.until_voltage_V:
                    step_str += f" until {step.until_voltage_V} V"

            elif isinstance(step, ConstantVoltage):
                step_str += f"Hold at {step.voltage_V} V"
                conditions = []
                if step.until_time_s:
                    if step.until_time_s % 3600 == 0:
                        step_str += f" for {int(step.until_time_s / 3600)} hours"
                    elif step.until_time_s % 60 == 0:
                        step_str += f" for {int(step.until_time_s / 60)} minutes"
                    else:
                        conditions.append(f"for {step.until_time_s} seconds")
                if step.until_rate_C:
                    conditions.append(f"until {step.until_rate_C}C")
                if step.until_current_mA:
                    conditions.append(f" until {step.until_current_mA} mA")
                if conditions:
                    step_str += " " + " or ".join(conditions)

            elif isinstance(step, OpenCircuitVoltage):
                step_str += f"Rest for {step.until_time_s} seconds"

            elif isinstance(step, Loop):
                # The string from this will get dropped later
                loops[i] = {"goto": step.start_step - 1, "n": step.cycle_count, "n_done": 0}

            else:
                msg = f"to_pybamm_experiment does not support step type: {step.name}"
                raise TypeError(msg)

            pybamm_experiment.append(step_str)

        exploded_steps = []
        i = 0
        total_itr = 0
        while i < len(pybamm_experiment):
            exploded_steps.append(i)
            if i in loops and loops[i]["n_done"] < loops[i]["n"]:
                # check if it passes over a different loop, if so reset its count
                for j in loops:  # noqa: PLC0206
                    if j < i and j >= loops[i]["goto"]:
                        loops[j]["n_done"] = 0
                loops[i]["n_done"] += 1
                i = loops[i]["goto"]
            else:
                i += 1
            total_itr += 1
            if total_itr > 10000:
                msg = "Over 10000 steps in protocol to_pybamm_experiment(), likely a loop definition error."
                raise RuntimeError(msg)

        # remove all loop steps from the list
        cleaned_exploded_steps = [i for i in exploded_steps if i not in loops]
        # change from list of indices to list of strings
        return [pybamm_experiment[i] for i in cleaned_exploded_steps]

    def to_eclab_settings(
        self,
        save_path: Path | None = None,
        sample_name: str | None = None,
        capacity_mAh: Decimal | float | None = None,
    ) -> str:
        """Make one giant technique for the entire protocol."""
        # Allow overwriting name and capacity
        if sample_name:
            self.sample.name = sample_name
        if capacity_mAh:
            self.sample.capacity_mAh = Decimal(capacity_mAh)

        # Make sure sample name is set
        if not self.sample.name or self.sample.name == "$NAME":
            msg = "If using blank sample name or $NAME placeholder, a sample name must be provided in this function."
            raise ValueError(msg)

        # Make sure capacity is set if using C-rate steps
        self._validate_capacity_c_rates()

        # Remove tags and convert to indices
        self.tag_to_indices()

        header = [
            "EC-LAB SETTING FILE",
            "",
            "Number of linked techniques : 1",
            "Device : MPG-2",
            "CE vs. WE compliance from -10 V to 10 V",
            "Electrode connection : standard",
            "Potential control : Ewe",
            "Ewe ctrl range : min = 0.00 V, max = 5.00 V",
            "Safety Limits :",
            "	Do not start on E overload",
            f"Comments : {self.sample.name}",
            "Cycle Definition : Charge/Discharge alternance",
            "Turn to OCV between techniques",
            "",
            "Technique : 1",
            "Modulo Bat",
        ]

        # Find the maximum current to determine the I range - it is not straightforward to switch this during a run
        # so we use the range that covers all currents
        currents_mA = [
            float(s.rate_C) * float(self.sample.capacity_mAh)
            if s.rate_C and self.sample.capacity_mAh
            else float(s.current_mA)
            if s.current_mA
            else 0
            for s in self.method
            if isinstance(s, (ConstantCurrent))
        ]
        max_current_mA = max(currents_mA) if currents_mA else 0
        if max_current_mA < 1:
            I_range = "1 mA"
        elif max_current_mA < 10:
            I_range = "10 mA"
        elif max_current_mA < 100:
            I_range = "100 mA"
        else:
            msg = "Not allowed to apply more than 100 mA"
            raise ValueError(msg)

        default_step = {
            "Ns": "",
            "ctrl_type": "",
            "Apply I/C": "I",
            "current/potential": "current",
            "ctrl1_val": "",
            "ctrl1_val_unit": "",
            "ctrl1_val_vs": "",
            "ctrl2_val": "",
            "ctrl2_val_unit": "",
            "ctrl2_val_vs": "",
            "ctrl3_val": "",
            "ctrl3_val_unit": "",
            "ctrl3_val_vs": "",
            "N": "0.00",
            "charge/discharge": "Charge",
            "charge/discharge_1": "Charge",
            "Apply I/C_1": "I",
            "N1": "0.00",
            "ctrl4_val": "",
            "ctrl4_val_unit": "",
            "ctrl5_val": "",
            "ctrl5_val_unit": "",
            "ctrl_tM": "0",
            "ctrl_seq": "0",
            "ctrl_repeat": "0",
            "ctrl_trigger": "Falling Edge",
            "ctrl_TO_t": "0.000",
            "ctrl_TO_t_unit": "d",
            "ctrl_Nd": "6",
            "ctrl_Na": "2",
            "ctrl_corr": "0",
            "lim_nb": "0",
            "lim1_type": "Time",
            "lim1_comp": ">",
            "lim1_Q": "",
            "lim1_value": "0.000",
            "lim1_value_unit": "s",
            "lim1_action": "Next sequence",
            "lim1_seq": "",
            "lim2_type": "",
            "lim2_comp": "",
            "lim2_Q": "",
            "lim2_value": "",
            "lim2_value_unit": "",
            "lim2_action": "Next sequence",
            "lim2_seq": "",
            "rec_nb": "0",
            "rec1_type": "",
            "rec1_value": "",
            "rec1_value_unit": "",
            "rec2_type": "",
            "rec2_value": "",
            "rec2_value_unit": "",
            "E range min (V)": "0.000",
            "E range max (V)": "5.000",
            "I Range": I_range,
            "I Range min": "Unset",
            "I Range max": "Unset",
            "I Range init": "Unset",
            "auto rest": "0",
            "Bandwidth": "5",
        }

        # Make a list of dicts, one for each step
        step_dicts = []
        for i, step in enumerate(self.method):
            step_dict = default_step.copy()
            step_dict.update(
                {
                    "Ns": str(i),
                    "lim1_seq": str(i + 1),
                    "lim2_seq": str(i + 1),
                },
            )
            if isinstance(step, OpenCircuitVoltage):
                step_dict.update(
                    {
                        "ctrl_type": "Rest",
                        "lim_nb": "1",
                        "lim1_type": "Time",
                        "lim1_comp": ">",
                        "lim1_value": f"{step.until_time_s:.3f}",
                        "lim1_value_unit": "s",
                        "rec_nb": "1",
                        "rec1_type": "Time",
                        "rec1_value": f"{self.measurement.time_s or 0:.3f}",
                        "rec1_value_unit": "s",
                    },
                )

            elif isinstance(step, ConstantCurrent):
                if step.rate_C and self.sample.capacity_mAh:
                    current_mA = step.rate_C * self.sample.capacity_mAh
                elif step.current_mA:
                    current_mA = step.current_mA
                else:
                    msg = "Either rate_C or current_mA must be set for ConstantCurrent step."
                    raise ValueError(msg)

                if abs(current_mA) < 1:
                    step_dict.update(
                        {
                            "ctrl_type": "CC",
                            "ctrl1_val": f"{current_mA:.3f}",
                            "ctrl1_val_unit": "µA",
                            "ctrl1_val_vs": "<None>",
                        },
                    )
                else:
                    step_dict.update(
                        {
                            "ctrl_type": "CC",
                            "ctrl1_val": f"{current_mA:.3f}",
                            "ctrl1_val_unit": "mA",
                            "ctrl1_val_vs": "<None>",
                        },
                    )

                # Add limit details
                lim_num = 0
                if step.until_time_s:
                    lim_num += 1
                    step_dict.update(
                        {
                            f"lim{lim_num}_type": "Time",
                            f"lim{lim_num}_comp": ">",
                            f"lim{lim_num}_value": f"{step.until_time_s:.3f}",
                            f"lim{lim_num}_value_unit": "s",
                        },
                    )
                if step.until_voltage_V:
                    lim_num += 1
                    comp = ">" if current_mA > 0 else "<"
                    step_dict.update(
                        {
                            f"lim{lim_num}_type": "Ewe",
                            f"lim{lim_num}_comp": comp,
                            f"lim{lim_num}_value": f"{step.until_voltage_V:.3f}",
                            f"lim{lim_num}_value_unit": "V",
                        },
                    )
                step_dict.update(
                    {
                        "lim_nb": str(lim_num),
                    },
                )

                # Add record details
                rec_num = 0
                if self.measurement.time_s:
                    rec_num += 1
                    step_dict.update(
                        {
                            f"rec{rec_num}_type": "Time",
                            f"rec{rec_num}_value": f"{self.measurement.time_s:.3f}",
                            f"rec{rec_num}_value_unit": "s",
                        },
                    )
                if self.measurement.voltage_V:
                    rec_num += 1
                    step_dict.update(
                        {
                            f"rec{rec_num}_type": "Ewe",
                            f"rec{rec_num}_value": f"{self.measurement.voltage_V:.3f}",
                            f"rec{rec_num}_value_unit": "V",
                        },
                    )
                step_dict.update(
                    {
                        "rec_nb": str(rec_num),
                    },
                )

            elif isinstance(step, ConstantVoltage):
                step_dict.update(
                    {
                        "ctrl_type": "CV",
                        "ctrl1_val": f"{step.voltage_V:.3f}",
                        "ctrl1_val_unit": "V",
                        "ctrl1_val_vs": "Ref",
                    },
                )

                # Add limit details
                lim_num = 0
                if step.until_time_s:
                    lim_num += 1
                    step_dict.update(
                        {
                            f"lim{lim_num}_type": "Time",
                            f"lim{lim_num}_comp": ">",
                            f"lim{lim_num}_value": f"{step.until_time_s:.3f}",
                            f"lim{lim_num}_value_unit": "s",
                        },
                    )
                if step.until_rate_C and self.sample.capacity_mAh:
                    until_mA = step.until_rate_C * self.sample.capacity_mAh
                elif step.until_current_mA:
                    until_mA = step.until_current_mA
                else:
                    until_mA = None
                if until_mA:
                    lim_num += 1
                    step_dict.update(
                        {
                            f"lim{lim_num}_type": "|I|",
                            f"lim{lim_num}_comp": "<",
                            f"lim{lim_num}_value": f"{abs(until_mA):.3f}",
                            f"lim{lim_num}_value_unit": "mA",
                        },
                    )
                step_dict.update(
                    {
                        "lim_nb": str(lim_num),
                    },
                )

                # Add record details
                rec_num = 0
                if self.measurement.time_s:
                    rec_num += 1
                    step_dict.update(
                        {
                            f"rec{rec_num}_type": "Time",
                            f"rec{rec_num}_value": f"{self.measurement.time_s:.3f}",
                            f"rec{rec_num}_value_unit": "s",
                        },
                    )
                if self.measurement.current_mA:
                    rec_num += 1
                    step_dict.update(
                        {
                            f"rec{rec_num}_type": "I",
                            f"rec{rec_num}_value": f"{self.measurement.current_mA:.3f}",
                            f"rec{rec_num}_value_unit": "mA",
                        },
                    )
                step_dict.update(
                    {
                        "rec_nb": str(rec_num),
                    },
                )

            elif isinstance(step, Loop):
                step_dict.update(
                    {
                        "ctrl_type": "Loop",
                        "ctrl_seq": str(step.start_step - 1),  # 0-indexed here
                        "ctrl_repeat": str(step.cycle_count - 1),  # cycles is one less than n_gotos
                    },
                )

            else:
                msg = f"to_eclab_settings does not support step type: {step.name}"
                raise NotImplementedError(msg)

            step_dicts.append(step_dict)

        # Transform list of dicts into list of strings, each row is one key and all values of each step
        # All elements must be 20 characters wide
        rows = []
        for row_header in default_step:
            row_data = [step[row_header] for step in step_dicts]
            rows.append(row_header.ljust(20) + "".join(d.ljust(20) for d in row_data))

        settings_string = "\n".join([*header, *rows, ""])

        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with save_path.open("w", encoding="utf-8") as f:
                f.write(settings_string)

        return settings_string


def from_dict(data: dict, sample_name: str | None = None, sample_capacity_mAh: float | None = None) -> Protocol:
    """Create a Protocol instance from a dictionary."""
    # If values given then overwrite
    data.setdefault("sample", {})
    if sample_name:
        data["sample"]["name"] = sample_name
    if sample_capacity_mAh:
        data["sample"]["capacity_mAh"] = sample_capacity_mAh
    return Protocol(**data)


def from_json(json_file: Path, sample_name: str | None = None, sample_capacity_mAh: float | None = None) -> Protocol:
    """Create a Protocol instance from a JSON file."""
    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return from_dict(data, sample_name, sample_capacity_mAh)
