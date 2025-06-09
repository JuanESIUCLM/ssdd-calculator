"""Module containing the handler functions for CLI commands."""

import logging
import os
import sys

from calculator.server import Server
from calculator import kafka_handler as kafka_handler_local

def calculator() -> None:
    """Handle for running the server for remote calculator."""
    logging.basicConfig(level=logging.DEBUG)

    cmd_name = os.path.basename(sys.argv[0])

    logger = logging.getLogger(cmd_name)
    logger.info("Running calculator server...")

    server = Server()
    sys.exit(server.main(sys.argv))

def kafka_handler() -> None:
    """Handle for running the Kafka operation handler."""
    sys.exit(kafka_handler_local.main())
