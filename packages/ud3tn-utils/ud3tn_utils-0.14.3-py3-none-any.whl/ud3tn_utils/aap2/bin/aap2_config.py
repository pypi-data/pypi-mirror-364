#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause OR Apache-2.0
# encoding: utf-8

import argparse
import logging

from ud3tn_utils.aap2 import (
    AAP2TCPClient,
    AAP2UnixClient,
    AuthType,
    BundleADU,
    BundleADUFlags,
    ResponseStatus,
)
from ud3tn_utils.config import (
    JSONConfigMessage as ConfigMessage,
    make_contact,
    RouterCommand,
)
from ud3tn_utils.aap2.bin.helpers import (
    add_common_parser_arguments,
    argparse_non_empty_str,
    get_config_eid,
    get_secret_from_args,
    initialize_logger,
)
from pyd3tn.eid import validate_eid


logger = logging.getLogger(__name__)


def main():
    import sys

    parser = argparse.ArgumentParser(
        description="configure a contact via uD3TN's AAP 2.0 interface",
    )
    add_common_parser_arguments(parser)
    parser.add_argument(
        "--dest_eid",
        type=argparse_non_empty_str,
        default=None,
        help="the EID of the node to which the configuration belongs",
    )
    parser.add_argument(
        "eid",
        type=argparse_non_empty_str,
        nargs="?",
        default=None,
        help="the EID of the node to which the contact exists",
    )
    parser.add_argument(
        "cla_address",
        type=argparse_non_empty_str,
        nargs="?",
        default=None,
        help="the CLA address of the node",
    )
    parser.add_argument(
        "-s", "--schedule",
        nargs=3,
        type=int,
        metavar=("start_offset", "duration", "bitrate"),
        action="append",
        default=[],
        help="schedule a contact relative to the current time",
    )
    parser.add_argument(
        "-r", "--reaches",
        type=argparse_non_empty_str,
        action="append",
        default=[],
        help="specify an EID reachable via the node",
    )
    parser.add_argument(
        "-d", "--delete",
        action="store_true",
        help="perform a DELETE instead of an ADD operation",
    )
    parser.add_argument(
        "-q", "--query",
        action="store_true",
        help="perform a QUERY instead of an ADD operation",
    )
    args = parser.parse_args()
    global logger
    logger = initialize_logger(args.verbosity)

    if not args.query and not args.delete:
        if not args.schedule:
            logger.fatal("At least one -s/--schedule argument must be given!")
            sys.exit(1)
        if not args.cla_address:
            logger.fatal("A CLA address must be given!")
            sys.exit(1)
    else:
        if args.query and args.delete:
            logger.fatal("--query and --delete are mutually exclusive!")
            sys.exit(1)
    if not args.query and not args.eid:
        logger.fatal("An EID must be given!")
        sys.exit(1)
    for eid in [args.eid, args.dest_eid]:
        if eid:
            validate_eid(eid)
    for eid in args.reaches:
        validate_eid(eid)

    msg = bytes(ConfigMessage(
        args.eid,
        args.cla_address,
        contacts=[
            make_contact(*contact)
            for contact in args.schedule
        ],
        reachable_eids=args.reaches,
        type=(
            RouterCommand.DELETE if args.delete
            else (
                RouterCommand.QUERY if args.query
                else RouterCommand.ADD
            )
        ),
    ))

    logger.debug("> %s", msg)

    if args.tcp:
        aap2_client = AAP2TCPClient(address=args.tcp)
    else:
        aap2_client = AAP2UnixClient(address=args.socket)
    with aap2_client:
        secret = aap2_client.configure(
            args.agentid,
            subscribe=False,
            secret=get_secret_from_args(args),
            auth_type=AuthType.AUTH_TYPE_BUNDLE_DISPATCH,
        )
        logger.info("Assigned agent secret: '%s'", secret)
        dest_eid = args.dest_eid or aap2_client.node_eid
        aap2_client.send_adu(
            BundleADU(
                dst_eid=get_config_eid(dest_eid),
                payload_length=len(msg),
                adu_flags=[BundleADUFlags.BUNDLE_ADU_WITH_BDM_AUTH],
            ),
            msg,
        )
        response = aap2_client.receive_response()
        if response.response_status != ResponseStatus.RESPONSE_STATUS_SUCCESS:
            logger.warning(
                "µD3TN responded with unexpected status: %s (%d)",
                aap2_client.response_status_name(response.response_status),
                response.response_status,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
