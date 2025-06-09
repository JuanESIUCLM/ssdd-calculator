"""Calculator implementation."""

import RemoteCalculator

class Calculator(RemoteCalculator.Calculator):
    """Implementation of the RemoteCalculator.Calculator interface."""

    def sum(self, a, b, _current=None):
        """Add two numbers and return the result."""
        return a + b

    def sub(self, a, b, _current=None):
        """Subtract two numbers and return the result."""
        return a - b

    def mult(self, a, b, _current=None):
        """Multiply two numbers and return the result."""
        return a * b

    def div(self, a, b, _current=None):
        """Divide two numbers and return the result."""
        if b == 0:
            raise RemoteCalculator.ZeroDivisionError()
        return a / b
