# SPDX-License-Identifier: BSD-3-Clause OR Apache-2.0
"""Helper functions for handling endpoint identifiers (EIDs)."""

import re


def get_node_id(eid: str) -> str:
    """Return the node ID belonging to a given EID.

    Returns:
        For ipn EIDs, this returns "ipn:N.0" whereas "N" is the node number.
        For dtn EIDs, "dtn://node/" is returned, wheras "node" is the node
        name. On error, a ValueError is raised.
    """
    if eid[0:6] == "dtn://":
        split_eid = eid.split("/")
        if len(split_eid) > 3 and split_eid[3].startswith("~"):
            raise ValueError("Non-singleton EID - no unique node ID present.")
        if len(split_eid[2]) == 0:
            raise ValueError("No node identifier present in EID.")
        return "dtn://" + split_eid[2] + "/"
    elif eid[0:4] == "ipn:":
        split_eid = eid.split(".")
        if (len(split_eid) != 2 or not split_eid[0][4:].isdigit() or
                not split_eid[1].isdigit()):
            raise ValueError("Invalid ipn EID format.")
        return split_eid[0] + ".0"
    elif eid == "dtn:none":
        return eid
    else:
        raise ValueError("Cannot determine the node prefix for the given EID.")


def test_get_node_id():
    import pytest
    assert "dtn://ud3tn/" == get_node_id("dtn://ud3tn/a")
    assert "dtn://ud3tn/" == get_node_id("dtn://ud3tn/a/")
    assert "dtn://ud3tn/" == get_node_id("dtn://ud3tn/a/b")
    assert "dtn://ud3tn/" == get_node_id("dtn://ud3tn/")
    assert "dtn://ud3tn/" == get_node_id("dtn://ud3tn")
    with pytest.raises(ValueError):
        get_node_id("dtn://ud3tn/~a")
    with pytest.raises(ValueError):
        get_node_id("dtn:///")
    with pytest.raises(ValueError):
        get_node_id("dtn:///A")
    with pytest.raises(ValueError):
        get_node_id("dtn://")
    assert "dtn:none" == get_node_id("dtn:none")
    assert "ipn:1.0" == get_node_id("ipn:1.0")
    assert "ipn:1.0" == get_node_id("ipn:1.1")
    assert "ipn:1.0" == get_node_id("ipn:1.42424242")
    with pytest.raises(ValueError):
        get_node_id("ipn:1:33")
    with pytest.raises(ValueError):
        get_node_id("ipn:1.")
    with pytest.raises(ValueError):
        get_node_id("ipn:1")
    with pytest.raises(ValueError):
        get_node_id("invalid:scheme")


def validate_eid(eid: str) -> str:
    """Checks if the node's EID follows the specific format.

    Returns:
        Verified valid EID. On error, a ValueError is raised.
    """
    # DTN Scheme.
    if eid[0:4] == "dtn:":
        return validate_dtn_eid(eid)
    # IPN scheme.
    elif eid[0:4] == "ipn:":
        return validate_ipn_eid(eid)
    else:
        raise ValueError("Invalid prefix for the given EID.")


def validate_dtn_eid(eid):
    # Minimum is dtn:none or dtn://C with C being a char.
    if len(eid) < 7:
        raise ValueError("Invalid EID length.")
    elif len(eid) == 8 and eid == "dtn:none":
        return eid
    elif eid[0:6] != "dtn://":
        raise ValueError("Invalid EID prefix for DTN scheme.")
    else:
        # Checking the part after "dtn://".
        node_name = eid[6:]

        # Splitting EID after first '/' in node name and demux parts.
        eid_parts = node_name.split('/', 1)
        node_name = eid_parts[0]
        demux = eid_parts[1] if len(eid_parts) > 1 else ''

        if len(node_name) == 0:
            raise ValueError("Invalid EID. Empty node name of EID.")

        allowed_chars = r'^[a-zA-Z0-9._-]+$'
        if not re.match(allowed_chars, node_name):
            raise ValueError("Invalid node name for DTN scheme.")

        if not all(0x21 <= ord(char) <= 0x7E for char in demux):
            raise ValueError("Invalid service name for DTN scheme.")
        return eid


def validate_ipn_eid(eid):
    node_name = eid[4:]

    eid_parts = node_name.split('.')
    if len(eid_parts) == 2:
        node_num, service = eid_parts
        alloc_id = "0"
    elif len(eid_parts) == 3:
        alloc_id, node_num, service = eid_parts
    else:
        raise ValueError(
            "Invalid number of EID components. "
            "Give EID doesn't comply with format: "
            "ipn:[<allocator-identifier>.]<node-number>.<service-number>")

    allowed_chars = r'^[0-9]+$'
    if not re.match(allowed_chars, alloc_id):
        raise ValueError("Invalid allocator identifier for IPN scheme.")
    if not re.match(allowed_chars, node_num):
        raise ValueError("Invalid node name for IPN scheme.")
    if not re.match(allowed_chars, service):
        raise ValueError("Invalid service name for IPN scheme.")
    return eid


def test_validate_eid():
    import pytest
    assert "dtn://ud3tn/a" == validate_eid("dtn://ud3tn/a")
    assert "dtn://ud3tn/a/" == validate_eid("dtn://ud3tn/a/")
    assert "dtn://ud3tn/a/b" == validate_eid("dtn://ud3tn/a/b")
    assert "dtn://ud3tn/" == validate_eid("dtn://ud3tn/")
    with pytest.raises(ValueError):
        validate_eid("dtn:///")
    with pytest.raises(ValueError):
        validate_eid("dtn:///A")
    with pytest.raises(ValueError):
        validate_eid("dtn://")
    assert "dtn:none" == validate_eid("dtn:none")
    assert "ipn:1.0" == validate_eid("ipn:1.0")
    assert "ipn:1.1" == validate_eid("ipn:1.1")
    assert "ipn:1.42424242" == validate_eid("ipn:1.42424242")
    assert "ipn:123456.100.0" == validate_eid("ipn:123456.100.0")
    assert "ipn:1.2.0" == validate_eid("ipn:1.2.0")
    assert "ipn:0.0.0" == validate_eid("ipn:0.0.0")
    assert "ipn:18446744073709551615.123" == validate_eid(
        "ipn:18446744073709551615.123"
    )
    assert "ipn:999999999999.888888888888.777777777777" == validate_eid(
        "ipn:999999999999.888888888888.777777777777"
    )
    with pytest.raises(ValueError):
        validate_eid("ipn:0.1.")
    with pytest.raises(ValueError):
        validate_eid("ipn:1.2.3.4")
    with pytest.raises(ValueError):
        validate_eid("ipn:1:33")
    with pytest.raises(ValueError):
        validate_eid("ipn:1.")
    with pytest.raises(ValueError):
        validate_eid("ipn:1")
    with pytest.raises(ValueError):
        validate_eid("invalid:scheme")
