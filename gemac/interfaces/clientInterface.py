from myhdl import Signal, intbv


class clientInterface:

    def __init__(self):

        # Client Transmitter Interface
        gtxclk = Signal(bool(0))
        txd = Signal(intbv(0)[8:])  # Transmit Data
        txdv = Signal(bool(0))  # Transmit Data Valid
        txifgdelay = Signal(intbv(0)[16:])  # Transmit InterFrameGap Delay
        txack = Signal(bool(0))  # Transmit Acknowledge 
        txunderrun = Signal(bool(0))  # Transmit Underrun

        # Client Receiver Interface
        rxd = Signal(intbv(0)[8:])  # Receive Data
        rxdv = Signal(bool(0))  # Receive Data Valid
        rxgood = Signal(bool(0))  # Receive Good Frame
        rxbadWWW = Signal(bool(0))  # Receive Bad Frame
