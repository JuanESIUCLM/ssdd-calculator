"""Calculator implementation."""

import RemoteCalculator

class Calculator(RemoteCalculator.Calculator):
    """Implementation of the RemoteCalculator.Calculator interface."""

    def sum(self, a, b, current=None):
        return a + b

    def sub(self, a, b, current=None):
        return a - b

    def mult(self, a, b, current=None):
        return a * b

    def div(self, a, b, current=None):
        if b == 0:
            raise RemoteCalculator.ZeroDivisionError()
        return a / b