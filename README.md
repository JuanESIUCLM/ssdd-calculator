# calculator repository

Extra SSDD laboratory 2024-2025

## Requirements

In order to use this software. It is needed:

- A version of python between 3.10 and 3.12.11
- Zero C ice (Python package: zeroc-ice)
- Apache Kafka (Server and command line utilities)
- Kafka for python (Python package: confluent-kafka)

## Installation

To locally install the package, just run

```
pip install .
```

Or, if you want to modify it during your development,

```
pip install -e .
```

## Configuration

To configure the server endpoint, you need to modify
the file `config/calculator.config` and change the existing line.

For example, if you want to make your server to listen always in the same TCP port, your file
should look like

```
calculator.Endpoints=tcp -p 10000
```

## Slice usage

The Slice file is provided inside the `calculator` directory. It is only loaded once when the `calculator`
package is loaded by Python. It makes your life much easier, as you don't need to load the Slice in every module
or submodule that you define.

The code loading the Slice is inside the `__init__.py` file.


## How to use

1. Start Kafka broker. Open a terminal and run:
    "kafka-server-start.sh config/server.properties"

2. Create topics (This is only needed to be done once). Open another terminal and run:
    "kafka-topics.sh --bootstrap-server localhost:9092 --create --topic calculator-requests"
    "kafka-topics.sh --bootstrap-server localhost:9092 --create --topic calculator-responses"

3. Start calculator server. Open another terminal and run:
    "ssdd-calculator --Ice.Config=config/calculator.config"

4. Start Kafka handler. Open another terminal and run:
    "ssdd-kafka-handler"

5. Start kafka console producer. Open another terminal and run:
    "kafka-console-producer.sh --bootstrap-server localhost:9092 --topic calculator-requests"

6. Start kafka console consumer. Open another terminal and run:
    "kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic calculator-responses --from-beginning"

7. Go back to the console producer terminal and write any message in the correct format. Here are some examples:
    "{"id": "test1", "operation": "sum", "args": {"op1": 2, "op2": 3}}"
    "{"id": "test3", "operation": "div", "args": {"op1": 1, "op2": 0}}"

9. The console consumer will respond the messagges on it's own terminal. The response will be something like this:
    "{"id": "test1", "status": true, "result": 5.0}"



