from myhdl import Signal, intbv


class phyInterface:

    def __init__(self):

        # GMII PHY Transmitter Interface
        txd = Signal(intbv(0)[8:])  # Transmit Data
        txen = Signal(bool(0))  # Transmit Enable
        txer = Signal(bool(0))  # Transmit Error

        # GMII PHY Receiver Interface
        rxclk = Signal(bool(0))  # Receive Clock
        rxd = Signal(intbv(0)[8:])  # Receive Data
        rxdv = Signal(bool(0))  # Receive Data Valid
        rxer = Signal(bool(0))  # Receive Error
        