import re

from datetime import datetime

from agentmemory.utils.dataclasses.default_factory_functions import current_iso_datetime, empty_dict, uuid


def test_current_iso_datetime():
    # Prepare & Execute
    iso_datetime_str = current_iso_datetime()

    # Check
    assert isinstance(iso_datetime_str, str)

    # Parse the ISO string and check for timezone info
    parsed_datetime = datetime.fromisoformat(iso_datetime_str)
    assert parsed_datetime.tzinfo is not None


def test_uuid():
    # Prepare & Execute
    generated_uuid = uuid()

    # Check
    assert isinstance(generated_uuid, str)
    assert len(generated_uuid) == 32
    # Check that the uuid is a 32-character lowercase hex string
    assert re.fullmatch(r"[0-9a-f]{32}", generated_uuid)


def test_empty_dict():
    # Prepare & Execute
    result_dict = empty_dict()

    # Check
    assert isinstance(result_dict, dict)
    assert result_dict == {}

    # Ensure a new instance is returned each time (not a singleton)
    assert result_dict is not empty_dict()
