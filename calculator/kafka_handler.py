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

def get_calculator_proxy():
    with Ice.initialize(sys.argv) as communicator:
        base = communicator.stringToProxy(ICE_CALCULATOR_PROXY)
        return RemoteCalculator.CalculatorPrx.checkedCast(base)

def validate_request(msg):
    try:
        data = json.loads(msg)
        if not isinstance(data, dict):
            return None, "format error"
        if "id" not in data or "operation" not in data or "args" not in data:
            return None, "format error"
        if not isinstance(data["id"], str):
            return None, "format error"
        if data["operation"] not in ("sum", "sub", "mult", "div"):
            return None, "operation not found"
        args = data["args"]
        if not isinstance(args, dict) or "op1" not in args or "op2" not in args:
            return None, "format error"
        op1 = args["op1"]
        op2 = args["op2"]
        if not (isinstance(op1, (int, float)) and isinstance(op2, (int, float))):
            return None, "format error"
        return {
            "id": data["id"],
            "operation": data["operation"],
            "op1": float(op1),
            "op2": float(op2)
        }, None
    except Exception:
        return None, "format error"

def main():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "calculator-group",
        "auto.offset.reset": "earliest"
    })
    producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    consumer.subscribe([REQUEST_TOPIC])

    calculator = get_calculator_proxy()
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
                logger.error(f"Kafka error: {msg.error()}")
                continue

            request_json = msg.value().decode("utf-8")
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
                            continue
                    response["status"] = True
                    response["result"] = result
                except Exception as e:
                    response["status"] = False
                    response["error"] = str(e)

            producer.produce(RESPONSE_TOPIC, json.dumps(response).encode("utf-8"))
            producer.flush()
    except KeyboardInterrupt:
        logger.info("Kafka handler stopped by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()