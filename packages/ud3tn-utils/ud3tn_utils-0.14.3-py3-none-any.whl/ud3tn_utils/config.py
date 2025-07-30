# SPDX-License-Identifier: BSD-3-Clause OR Apache-2.0
import dataclasses
import enum
import json
import jsonschema
import time
import re

from datetime import datetime, timezone
from typing import Set, Tuple

UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
DTN_EPOCH = datetime(2000, 1, 1, tzinfo=timezone.utc)
UNIX_TO_DTN_OFFSET = (DTN_EPOCH - UNIX_EPOCH).total_seconds()
assert UNIX_TO_DTN_OFFSET == 946684800

# This is a quite permissive regex to check EIDs in configuration commands,
# just enforcing the general structure of <scheme>:<ssp> specified by RFC9171.
CONFIG_EID_VALIDATION_REGEX = r"^[a-zA-Z0-9]+:.+$"

# Schema for the new JSON format for configuration messages.
CONFIG_MSG_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "pattern": r"^(ADD|UPDATE|DELETE|QUERY)$",
        },
        "node_id": {
            "type": "string",
            "pattern": CONFIG_EID_VALIDATION_REGEX,
        },
        "cla_addr": {
            "type": "string",
            "minLength": 1,
        },
        "reachable_eids": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": CONFIG_EID_VALIDATION_REGEX,
            },
        },
        "contact_list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "integer", "minimum": 0},
                    "end": {"type": "integer", "minimum": 0},
                    "data_rate": {"type": "integer", "minimum": 0},
                    "reachable_eids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "pattern": CONFIG_EID_VALIDATION_REGEX,
                        },
                    },
                },
                "required": ["start", "end", "data_rate"],
            }
        },
    },
    "additionalProperties": False,
    "required": ["command", "node_id"],
}


def unix2dtn(unix_timestamp):
    """Converts a given Unix timestamp into a DTN timestamp

    Its inversion is :func:`dtn2unix`.

    Args:
        unix_timestamp: Unix timestamp
    Returns:
        numeric: DTN timestamp
    """
    return unix_timestamp - UNIX_TO_DTN_OFFSET


class RouterCommand(enum.IntEnum):
    """uD3TN Command Constants"""
    ADD = 1
    UPDATE = 2
    DELETE = 3
    QUERY = 4


@dataclasses.dataclass(frozen=True)
class Contact:
    """Dataclass holding uD3TN contact information

    Attrs:
        start (int): DTN timestamp when the contact starts
        end (int): DTN timestamp when the contact is over
        bitrate (int): Bitrate of the contact, in bytes per second
        reachable_eids (Set[str]): EIDs reachable during contact; not hashed
    """
    start: int
    end: int
    bitrate: int
    # The following fields are not part of the hash when stored in a set.
    reachable_eids: Set[str] = dataclasses.field(
        compare=False,
        default_factory=set,
    )

    def __repr__(self):
        return (
            f"<Contact start={self.start}, end={self.end}, "
            f"bitrate={self.bitrate}>"
        )

    def __str__(self):
        if self.reachable_eids:
            eid_list = "[" + ",".join(
                "(" + eid + ")" for eid in self.reachable_eids
            ) + "]"
            return f"{{{self.start},{self.end},{self.bitrate},{eid_list}}}"
        else:
            return f"{{{self.start},{self.end},{self.bitrate}}}"


def make_contact(start_offset, duration, bitrate, reachable_eids=None):
    """Create a :class:`Contact` tuple relative to the current time

    NOTE: The parameters of this function are also compatible with float-typed
          input arguments.

    Args:
        start_offset (int): Start point of the contact in seconds from now
        duration (int): Duration of the contact in seconds
        bitrate (int): Bitrate of the contact, in bytes per second
        reachable_eids (Set[str]): EIDs reachable during contact; not hashed
    Returns:
        Contact: contact tuple with DTN timestamps
    """
    cur_time = time.time()
    start = unix2dtn(cur_time + start_offset)

    if reachable_eids:
        return Contact(
            start=int(round(start)),
            end=int(round(start + duration)),
            bitrate=int(round(bitrate)),
            reachable_eids=set(reachable_eids),
        )
    else:
        return Contact(
            start=int(round(start)),
            end=int(round(start + duration)),
            bitrate=int(round(bitrate)),
        )


class ConfigMessage(object):
    """Base class for the uD3TN configuration messages, which can be processed
    by the config endpoint of its deterministic first-contact forwarding BDM
    (either integrated or external).

    Args:
        eid (Optional[str]): The endpoint identifier of a contact
        cla_address (Optional[str]): The Convergency Layer Adapter (CLA)
            address for the contact's EID
        reachable_eids (Iterable[str], optional): List of reachable EIDs via
            this contact
        contacts (Iterable[Contact], optional): List of contacts with the node
        type (RouterCommand, optional): Type of the configuration message (add,
            remove, ...)
    """

    def __init__(self, eid, cla_address, reachable_eids=None, contacts=None,
                 type=RouterCommand.ADD):
        self.eid = eid
        self.cla_address = cla_address
        self.reachable_eids = set(reachable_eids) if reachable_eids else set()
        self.contacts = set(contacts) if contacts else set()
        self.type = type

    def __repr__(self):
        return "<ConfigMessage {!r} {!r} reachable={} contacts={}>".format(
            self.eid, self.cla_address, self.reachable_eids, self.contacts
        )

    @staticmethod
    def parse(config_str: str, schema_validate: bool = True
              ) -> "LegacyConfigMessage":
        """Parse the provided configuration string representation,
        automatically decising whether it is a JSON or legacy representation.

        Args:
            config_str (str): The serialized string representation, obtained
                e.g. via str() applied on a LegacyConfigMessage or
                JSONConfigMessage object.

        Return:
            A ConfigMessage instance of the correct subclass representing the
            data parsed from config_str.
        """

        if config_str[0] == "{":
            return JSONConfigMessage.parse(config_str, schema_validate)
        else:
            return LegacyConfigMessage.parse(config_str)


class JSONConfigMessage(ConfigMessage):
    """uD3TN configuration message using the JSON encoding.

    NOTE: At the moment (v0.15.0), for this to be supported, the external
        (Python) forwarding module has to be used.
    """

    def __str__(self):
        ret_obj = {
            "command": {
                1: "ADD",
                2: "UPDATE",
                3: "DELETE",
                4: "QUERY",
            }[self.type],
            "node_id": self.eid,
        }

        if self.cla_address:
            ret_obj["cla_addr"] = self.cla_address

        if self.reachable_eids:
            ret_obj["reachable_eids"] = list(self.reachable_eids)

        if self.contacts:
            ret_obj["contact_list"] = [
                {
                    "start": c.start,
                    "end": c.end,
                    "data_rate": c.bitrate,
                    "reachable_eids": (
                        list(c.reachable_eids) if c.reachable_eids else []
                    ),
                }
                for c in self.contacts
            ]

        return json.dumps(ret_obj)

    def __bytes__(self):
        return str(self).encode('utf-8')

    def to_legacy_format(self) -> "LegacyConfigMessage":
        return LegacyConfigMessage(
            self.eid,
            self.cla_address,
            self.reachable_eids,
            self.contacts,
            type=self.type,
        )

    @staticmethod
    def parse(config_str: str, schema_validate: bool = True
              ) -> "JSONConfigMessage":
        """Parse the provided JSON configuration string representation.

        Args:
            config_str (str): The serialized string representation, obtained
                e.g. via str() applied on a JSONConfigMessage object.

        Return:
            A JSONConfigMessage instance representing the data parsed from
            config_str.
        """

        obj = json.loads(config_str)
        if schema_validate:
            jsonschema.validate(obj, CONFIG_MSG_JSON_SCHEMA)

        return JSONConfigMessage(
            obj["node_id"],
            obj["cla_addr"],
            obj.get("reachable_eids", []),
            [
                Contact(
                    start=c["start"],
                    end=c["end"],
                    bitrate=c["data_rate"],
                    reachable_eids=c.get("reachable_eids", None),
                )
                for c in obj.get("contact_list", [])
            ],
            type=RouterCommand({
                "ADD": 1,
                "UPDATE": 2,
                "DELETE": 3,
                "QUERY": 4,
            }[obj["command"]]),
        )


class LegacyConfigMessage(ConfigMessage):
    """uD3TN configuration message using the legacy custom format."""

    def __str__(self):
        # missing escaping has to be addressed in uD3TN
        for part in ({str(self.eid), str(self.cla_address)} |
                     self.reachable_eids):
            assert "(" not in part, "unsupported character in string"
            assert ")" not in part, "unsupported character in string"

        assert "," not in str(self.eid), "unsupported character in string"

        if self.reachable_eids:
            eid_list = "[" + ",".join(
                "(" + eid + ")" for eid in self.reachable_eids
            ) + "]"
        else:
            eid_list = ""

        if self.contacts:
            contact_list = (
                    "[" +
                    ",".join(
                        str(contact)
                        for contact in self.contacts
                    ) +
                    "]"
                )
        else:
            contact_list = ""

        if self.eid is None:
            return "{};".format(self.type)
        elif self.cla_address is None:
            return "{}({})::{}:{};".format(
                self.type,
                self.eid,
                eid_list,
                contact_list,
            )
        else:
            return "{}({}):({}):{}:{};".format(
                self.type,
                self.eid,
                self.cla_address,
                eid_list,
                contact_list,
            )

    def __bytes__(self):
        return str(self).encode('ascii')

    def to_json_format(self) -> JSONConfigMessage:
        return JSONConfigMessage(
            self.eid,
            self.cla_address,
            self.reachable_eids,
            self.contacts,
            type=self.type,
        )

    @staticmethod
    def parse(config_str: str):
        """Parse the provided configuration string representation.

        Args:
            config_str (str): The serialized string representation, obtained
                e.g. via str() applied on a LegacyConfigMessage object.

        Return:
            A LegacyConfigMessage instance representing the data parsed from
            config_str.
        """
        cmd_type, node_id, cla_addr, reachable_eids, contacts = _parse_config(
            config_str,
        )
        return LegacyConfigMessage(
            node_id,
            cla_addr,
            reachable_eids,
            contacts,
            type=RouterCommand(cmd_type),
        )


# Config Parser helper functions
CONFIG_PARSE_REGEX = re.compile(
    r"^(?P<cmd>[1-4])(\((?P<nodeid>[^\)]+)\))?(\:(\((?P<claaddr>[^\)]+)\))?"
    r"(\:(?P<eidlist>\[(\(([^\)]+)\),?)*\])?"
    r"(\:(?P<contactlist>\[(\{[0-9]+,[0-9]+,[0-9]+(,\[(\([^\)]+\),?)+\])?\}"
    r",?)*\])?)?)?)?;$"
)
EID_LIST_PARSE_REGEX = re.compile(
    r"^[\[,]\((?P<eid>[^\)]+)\)(?P<remainder>,\(.+\))?\]?$"
)
CONTACT_LIST_PARSE_REGEX = re.compile(
    r"^[\[,]\{(?P<start>[0-9]+),(?P<end>[0-9]+),(?P<datarate>[0-9]+)"
    r"(,(?P<eidlist>\[(\([^\)]+\),?)+\]))?\}(?P<remainder>,\{.+\})?\]?$"
)


def _parse_eid_list(eid_list: str) -> Set[str]:
    if eid_list is None:
        return set()
    match_obj = EID_LIST_PARSE_REGEX.match(eid_list)
    if match_obj is None:
        return set()
    if match_obj.group(2) is None:
        return {match_obj.group(1)}
    return {match_obj.group(1)} | _parse_eid_list(match_obj.group(2))


def _parse_contact_list(contact_list: str) -> Set[Contact]:
    if contact_list is None:
        return set()
    match_obj = CONTACT_LIST_PARSE_REGEX.match(contact_list)
    if match_obj is None:
        return set()
    contact = Contact(
        start=int(match_obj.group("start")),
        end=int(match_obj.group("end")),
        bitrate=int(match_obj.group("datarate")),
        reachable_eids=_parse_eid_list(match_obj.group("eidlist")),
    )
    if match_obj.group("remainder") is None:
        return {contact}
    return {contact} | _parse_contact_list(
        match_obj.group("remainder"),
    )


def _parse_config(config_str: str) -> Tuple[int, str, Set[str], Set[Contact]]:
    match_obj = CONFIG_PARSE_REGEX.match(config_str)
    if match_obj is None:
        raise ValueError("invalid config string")
    cmd_type = RouterCommand(int(match_obj.group("cmd")))
    node_id = match_obj.group("nodeid")
    if node_id is None and cmd_type != RouterCommand.QUERY:
        raise ValueError("an empty node ID is only valid for QUERY commands")
    return (
        cmd_type,
        node_id,
        match_obj.group("claaddr"),
        _parse_eid_list(match_obj.group("eidlist")),
        _parse_contact_list(match_obj.group("contactlist")),
    )


def test_parse_config():
    assert _parse_config(
        "1(dtn://ud3tn2.dtn/):(mtcp:127.0.0.1:4223)::["
        "{1401519306972,1401519316972,1200,[(dtn://89326/),(dtn://12349/)]},"
        "{1401519506972,1401519516972,1200,[(dtn://89326/),(dtn://12349/)]}];"
    ) == (
        1,
        "dtn://ud3tn2.dtn/",
        "mtcp:127.0.0.1:4223",
        set(),
        {
            Contact(
                start=1401519306972,
                end=1401519316972,
                bitrate=1200,
                reachable_eids={
                    "dtn://89326/",
                    "dtn://12349/",
                },
            ),
            Contact(
                start=1401519506972,
                end=1401519516972,
                bitrate=1200,
                reachable_eids={
                    "dtn://89326/",
                    "dtn://12349/",
                },
            ),
        },
    )
    assert _parse_config(
        "1(dtn://ud3tn2.dtn/)::[(dtn://18471/),(dtn://81491/)]:"
        "[{1401519406972,1401819306972,1200}];"
    ) == (
        1,
        "dtn://ud3tn2.dtn/",
        None,
        {"dtn://18471/", "dtn://81491/"},
        {
            Contact(
                start=1401519406972,
                end=1401819306972,
                bitrate=1200,
                reachable_eids=set(),
            ),
        },
    )
    assert _parse_config(
        "2(dtn://ud3tn2.dtn/):(mtcp:127.0.0.1:4223):"
        "[(dtn://89326/),(dtn://12349/)];"
    ) == (
        2,
        "dtn://ud3tn2.dtn/",
        "mtcp:127.0.0.1:4223",
        {"dtn://89326/", "dtn://12349/"},
        set(),
    )
    assert _parse_config(
        "2(dtn://ud3tn2.dtn/)::[]:[];"
    ) == (
        2,
        "dtn://ud3tn2.dtn/",
        None,
        set(),
        set(),
    )
    assert _parse_config(
        "2(ipn:1.0)::[];"
    ) == (
        2,
        "ipn:1.0",
        None,
        set(),
        set(),
    )
    assert _parse_config(
        "3(dtn://ud3tn2.dtn/);"
    ) == (
        3,
        "dtn://ud3tn2.dtn/",
        None,
        set(),
        set(),
    )
    assert _parse_config(
        "1(dtn://13714/):(tcpspp:):[(dtn://18471/),(dtn://81491/)]:;"
    ) == (
        1,
        "dtn://13714/",
        "tcpspp:",
        {"dtn://18471/", "dtn://81491/"},
        set(),
    )
    assert _parse_config(
        "4(dtn://ud3tn2.dtn/);"
    ) == (
        4,
        "dtn://ud3tn2.dtn/",
        None,
        set(),
        set(),
    )
    assert _parse_config(
        "4;"
    ) == (
        4,
        None,
        None,
        set(),
        set(),
    )


def test_parse_and_serialize():
    config_str1 = (
        "1(dtn://ud3tn2.dtn/):(mtcp:127.0.0.1:4223):[(ipn:1.0)]:["
        "{1401519306972,1401519316972,2400,[(dtn://89326/),(dtn://66553/)]},"
        "{1401519506972,1401519516972,1200,[(dtn://89326/),(dtn://12349/)]}];"
    )
    cm1 = ConfigMessage.parse(config_str1)
    assert isinstance(cm1, LegacyConfigMessage)
    # NOTE: We cannot `assert config_str1 == str(cm1)` here as the set
    # ordering may differ.
    cm2 = ConfigMessage.parse(str(cm1))
    assert isinstance(cm2, LegacyConfigMessage)
    assert cm1.type == cm2.type == 1
    assert cm1.eid == cm2.eid == "dtn://ud3tn2.dtn/"
    assert cm1.cla_address == cm2.cla_address == "mtcp:127.0.0.1:4223"
    assert cm1.reachable_eids == cm2.reachable_eids == {"ipn:1.0"}
    assert cm1.contacts == cm2.contacts
    # Test JSON conversion and serialization
    jo = cm1.to_json_format()
    assert isinstance(jo, JSONConfigMessage)
    jstr = str(jo)
    jo2 = ConfigMessage.parse(jstr, True)
    assert cm1.type == jo2.type == 1
    assert cm1.eid == jo2.eid == "dtn://ud3tn2.dtn/"
    assert cm1.cla_address == jo2.cla_address == "mtcp:127.0.0.1:4223"
    assert cm1.reachable_eids == jo2.reachable_eids == {"ipn:1.0"}
    assert cm1.contacts == jo2.contacts
    cm3 = jo2.to_legacy_format()
    assert isinstance(cm3, LegacyConfigMessage)
    assert cm1.type == cm3.type == 1
    assert cm1.eid == cm3.eid == "dtn://ud3tn2.dtn/"
    assert cm1.cla_address == cm3.cla_address == "mtcp:127.0.0.1:4223"
    assert cm1.reachable_eids == cm3.reachable_eids == {"ipn:1.0"}
    assert cm1.contacts == cm3.contacts
