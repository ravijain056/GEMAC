from myhdl import Signal, intbv, ResetSignal, TristateSignal


class FlowControlInterface:
    def __init__(self):
        self.pausereq = Signal(bool(0))  # Pause Request
        self.pauseval = Signal(intbv(0)[16:])  # Pause Value


class HostManagementInterface():
    def __init__(self):
        # Client Management Interface
        self.clk = Signal(bool(0))  # Host Clock
        self.opcode = Signal(intbv(0)[2:])  # host Opcode
        self.regaddress = Signal(intbv(0)[10:])  # Configuration Register Addr
        self.wrdata = Signal(intbv(0)[32:])  # Write Data
        self.rddata = Signal(intbv(0)[32:])  # Read Data
        self.miimsel = Signal(bool(1))  # MIIM select
        self.hostreq = Signal(bool(0))  # host Request
        self.miimrdy = Signal(bool(1))  # hostMIIM_ready

    def idle(self):
        self.miimsel.next = 1

    def writeconfig(self, addr, data):
        self.miimsel.next = 0
        self.opcode.next = 0
        self.regaddress.next = intbv(addr)[10:]
        self.wrdata.next = intbv(data)[32:]

    def readconfig(self, addr):
        self.miimsel.next = 0
        self.opcode.next = 0b10
        self.regaddress.next = intbv(addr)[10:]


class MDIOInterface:
    def __init__(self):
        # MDIO PHY Interface
        self.mdc = Signal(bool(0))  # Management Clock derived from Host Clock
        self.mdioio = TristateSignal(bool(0))  # Driven by mdio(in, out, tri)


class PHYInterface:
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


class RxFIFOClientInterface:
    def __init__(self):
        self.rxclk = Signal(bool(0))
        self.reset = ResetSignal(0, active=0, async=False)
        self.clkenable = Signal(bool(0))
        self.rxd = Signal(intbv(0)[8:])  # Receive Data
        self.rxdv = Signal(bool(0))  # Receive Data Valid
        self.rxgood = Signal(bool(0))  # Receive Good Frame
        self.rxbad = Signal(bool(0))  # Receive Bad Frame
        self.overflow = Signal(bool(0))


class RxLocalLinkFIFOInterface:
    def __init__(self):
        self.rxclk = Signal(bool(0))
        self.reset = ResetSignal(0, active=0, async=False)
        self.rxd = Signal(intbv(0)[8:])
        self.sof = Signal(bool(0))
        self.eof = Signal(bool(0))
        self.src_rdy = Signal(bool(0))  # Source Ready
        self.dst_rdy = Signal(bool(0))  # Destination Ready
        self.fifostatus = Signal(bool(0))


class TxFIFOClientInterface:
    def __init__(self):
        # Client Transmitter Interface
        self.gtxclk = Signal(bool(0))
        self.txd = Signal(intbv(0)[8:])  # Transmit Data
        self.txdv = Signal(bool(0))  # Transmit Data Valid
        self.txifgdelay = Signal(intbv(0)[16:])  # Transmit InterFrameGap Delay
        self.txack = Signal(bool(0))  # Transmit Acknowledge
        self.txunderrun = Signal(bool(0))  # Transmit Underrun
        self.txcollision = Signal(bool(0))
        self.txretransmit = Signal(bool(0))


class TxLocalLinkFIFOInterface:
    def __init__(self):
        self.txclk = Signal(bool(0))
        self.reset = ResetSignal(0, active=0, async=False)
        self.txd = Signal(intbv(0)[8:])
        self.sof = Signal(bool(0))
        self.eof = Signal(bool(0))
        self.src_rdy = Signal(bool(0))  # Source Ready
        self.dst_rdy = Signal(bool(0))  # Destination Ready
        self.fifostatus = Signal(intbv(0)[4:])
        self.overflow = Signal(bool(0))
