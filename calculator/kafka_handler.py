"""Kafka handler for the remote calculator service using Ice and Confluent Kafka."""

import json
import logging
import sys
import Ice
from confluent_kafka import Consumer, Producer

from calculator import RemoteCalculator

KAFKA_BROKER = "localhost:9092"
REQUEST_TOPIC = "calculator-requests"
RESPONSE_TOPIC = "calculator-responses"
ICE_CALCULATOR_PROXY = "calculator:tcp -h 127.0.0.1 -p 10000"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kafka_handler")

def get_calculator_proxy(communicator):
    """Get the Ice proxy for the remote calculator service."""
    base = communicator.stringToProxy(ICE_CALCULATOR_PROXY)
    return RemoteCalculator.CalculatorPrx.checkedCast(base)

def validate_request(msg):
    """Validate the incoming request message."""
    result = None
    error = None
    try:
        data = json.loads(msg)
        if not isinstance(data, dict):
            error = "format error"
        elif "id" not in data or "operation" not in data or "args" not in data:
            error = "format error"
        elif not isinstance(data["id"], str):
            error = "format error"
        elif data["operation"] not in ("sum", "sub", "mult", "div"):
            error = "operation not found"
        else:
            args = data["args"]
            if not isinstance(args, dict) or "op1" not in args or "op2" not in args:
                error = "format error"
            else:
                op1 = args["op1"]
                op2 = args["op2"]
                if not (isinstance(op1, (int, float)) and isinstance(op2, (int, float))):
                    error = "format error"
                else:
                    result = {
                        "id": data["id"],
                        "operation": data["operation"],
                        "op1": float(op1),
                        "op2": float(op2)
                    }
    except Exception:
        error = "format error"
    if result is not None:
        return result, None
    return None, error

def process_message(request_json, calculator, producer):
    """Process the incoming Kafka message and perform the requested operation."""
    result = None
    req, error = validate_request(request_json)
    response = {}

    if req is None:
        # Try to extract id for error response
        try:
            data = json.loads(request_json)
            response["id"] = data.get("id", "unknown")
        except Exception:
            response["id"] = "unknown"
        response["status"] = False
        response["error"] = error
    else:
        response["id"] = req["id"]
        try:
            if req["operation"] == "sum":
                result = calculator.sum(req["op1"], req["op2"])
            elif req["operation"] == "sub":
                result = calculator.sub(req["op1"], req["op2"])
            elif req["operation"] == "mult":
                result = calculator.mult(req["op1"], req["op2"])
            elif req["operation"] == "div":
                try:
                    result = calculator.div(req["op1"], req["op2"])
                except RemoteCalculator.ZeroDivisionError:
                    response["status"] = False
                    response["error"] = "division by zero"
                    producer.produce(RESPONSE_TOPIC, json.dumps(response).encode("utf-8"))
                    producer.flush()
                    return
            response["status"] = True
            response["result"] = result
        except Exception as e:
            response["status"] = False
            response["error"] = str(e)

    producer.produce(RESPONSE_TOPIC, json.dumps(response).encode("utf-8"))
    producer.flush()

def main():
    """Main function to run the Kafka handler."""
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "calculator-group",
        "auto.offset.reset": "earliest"
    })
    producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    consumer.subscribe([REQUEST_TOPIC])

    communicator = Ice.initialize(sys.argv)
    calculator = get_calculator_proxy(communicator)
    if not calculator:
        logger.error("Could not connect to remote calculator service.")
        sys.exit(1)

    logger.info("Kafka handler started. Waiting for messages...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error("Kafka error: %s", msg.error())
                continue

            request_json = msg.value().decode("utf-8")
            process_message(request_json, calculator, producer)

    except KeyboardInterrupt:
        logger.info("Kafka handler stopped by user.")
    finally:
        consumer.close()
        communicator.destroy()

if __name__ == "__main__":
    main()
