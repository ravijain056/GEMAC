from myhdl import Signal, intbv


class flowControlInterface:

    def __init__(self):

        pausereq = Signal(bool(0))  # Pause Request
        pauseval = Signal(intbv(0)[16:])  # Pause Value
