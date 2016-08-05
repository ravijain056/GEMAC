from myhdl import Signal, intbv


class TxGMII_Interface:
    def __init__(self):
        self.clk = Signal(bool(0))
        self.data = Signal(intbv(0)[8:])
        self.dv = Signal(bool(0))
        self.err = Signal(bool(0))


class RxGMII_Interface:
    def __init__(self):
        self.clk = Signal(bool(0))
        self.data = Signal(intbv(0)[8:])
        self.dv = Signal(bool(0))
        self.err = Signal(bool(0))


class TxFlowInterface:
    def __init__(self):
        self.clk = Signal(bool(0))
        self.pausereq = Signal(bool(0))
        self.pauseval = Signal(intbv(0)[16:])
        self.pauseapply = Signal(bool(0))
        self.ispaused = Signal(bool(0))
        self.macaddr = Signal(intbv(0)[48:])


class RxFlowInterface:
    def __init__(self):
        self.clk = Signal(bool(0))
        self.rxflowen = Signal(bool(0))
        self.macaddr = Signal(intbv(0)[48:])
        self.pausereq = Signal(bool(0))
        self.pauseval = Signal(intbv(0)[16:])
