from myhdl import Signal


class mdioInterface:

    def __init__(self):

        # MDIO PHY Interface
        mdc = Signal(bool(0))  # Management Clock derived from Host Clock
        mdioIn = Signal(bool(0))
        mdioOut = Signal(bool(0))
        mdioTri = Signal(bool(0))
