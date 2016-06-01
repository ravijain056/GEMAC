from myhdl import Signal, intbv


class flowControlInterface:

    def __init__(self):

        pausereq = Signal(bool(0))  # Pause Request
        pauseval = Signal(intbv(0)[16:])  # Pause Value


class managementInterface():

    def __init__(self):

        # Client Management Interface
        hostclk = Signal(bool(0))  # Host Clock
        opcode = Signal(intbv(0)[2:])  # host Opcode
        regaddress = Signal(intbv(0)[10:])  # Configuration Register Address
        wrdata = Signal(intbv(0)[32:])  # Write Data
        rddata = Signal(intbv(0)[32:])  # Read Data
        miimsel = Signal(bool(0))  # MIIM select
        hostreq = Signal(bool(0))  # host Request
        miimrdy = Signal(bool(0))  # hostMIIM_ready


class mdioInterface:

    def __init__(self):

        # MDIO PHY Interface
        mdc = Signal(bool(0))  # Management Clock derived from Host Clock
        mdioIn = Signal(bool(0))
        mdioOut = Signal(bool(0))
        mdioTri = Signal(bool(0))


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


class rxClientInterface:

    def __init__(self):

        rxd = Signal(intbv(0)[8:])  # Receive Data
        rxdv = Signal(bool(0))  # Receive Data Valid
        rxgood = Signal(bool(0))  # Receive Good Frame
        rxbad = Signal(bool(0))  # Receive Bad Frame


class txClientInterface:

    def __init__(self):

        # Client Transmitter Interface
        gtxclk = Signal(bool(0))
        txd = Signal(intbv(0)[8:])  # Transmit Data
        txdv = Signal(bool(0))  # Transmit Data Valid
        txifgdelay = Signal(intbv(0)[16:])  # Transmit InterFrameGap Delay
        txack = Signal(bool(0))  # Transmit Acknowledge 
        txunderrun = Signal(bool(0))  # Transmit Underrun
