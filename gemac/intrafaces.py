from myhdl import Signal, intbv


class TxGMII_Interface:
    def __init__(self):
        self.data = Signal(intbv(0)[8:])
        self.dv = Signal(bool(0))
        self.err = Signal(bool(0))


class RxGMII_Interface:
    def __init__(self):
        self.data = Signal(intbv(0)[8:])
        self.err = Signal(bool(0))


class TxFlowInterface:
    def __init__(self):
        self.txpause = Signal(bool(0))  # Transmit Pause Frame
        self.sampled_pauseval = Signal(intbv(0)[16:])
