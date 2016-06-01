from myhdl import Signal, intbv


class flowControlInterface:

    def __init__(self):

        self.pausereq = Signal(bool(0))  # Pause Request
        self.pauseval = Signal(intbv(0)[16:])  # Pause Value


class managementInterface():

    def __init__(self):

        # Client Management Interface
        self.hostclk = Signal(bool(0))  # Host Clock
        self.opcode = Signal(intbv(0)[2:])  # host Opcode
        self.regaddress = Signal(intbv(0)[10:])  # Configuration Register Address
        self.wrdata = Signal(intbv(0)[32:])  # Write Data
        self.rddata = Signal(intbv(0)[32:])  # Read Data
        self.miimsel = Signal(bool(0))  # MIIM select
        self.hostreq = Signal(bool(0))  # host Request
        self.miimrdy = Signal(bool(0))  # hostMIIM_ready


class mdioInterface:

    def __init__(self):

        # MDIO PHY Interface
        self.mdc = Signal(bool(0))  # Management Clock derived from Host Clock
        self.mdioIn = Signal(bool(0))
        self.mdioOut = Signal(bool(0))
        self.mdioTri = Signal(bool(0))


class phyInterface:

    def __init__(self):

        # GMII PHY Transmitter Interface
        self.txd = Signal(intbv(0)[8:])  # Transmit Data
        self.txen = Signal(bool(0))  # Transmit Enable
        self.txer = Signal(bool(0))  # Transmit Error

        # GMII PHY Receiver Interface
        self.rxclk = Signal(bool(0))  # Receive Clock
        self.rxd = Signal(intbv(0)[8:])  # Receive Data
        self.rxdv = Signal(bool(0))  # Receive Data Valid
        self.rxer = Signal(bool(0))  # Receive Error


class rxClientInterface:

    def __init__(self):

        self.rxd = Signal(intbv(0)[8:])  # Receive Data
        self.rxdv = Signal(bool(0))  # Receive Data Valid
        self.rxgood = Signal(bool(0))  # Receive Good Frame
        self.rxbad = Signal(bool(0))  # Receive Bad Frame


class txClientInterface:

    def __init__(self):

        # Client Transmitter Interface
        self.gtxclk = Signal(bool(0))
        self.txd = Signal(intbv(0)[8:])  # Transmit Data
        self.txdv = Signal(bool(0))  # Transmit Data Valid
        self.txifgdelay = Signal(intbv(0)[16:])  # Transmit InterFrameGap Delay
        self.txack = Signal(bool(0))  # Transmit Acknowledge 
        self.txunderrun = Signal(bool(0))  # Transmit Underrun
