from myhdl import Signal, intbv, ResetSignal


class FlowControlInterface:
    def __init__(self):
        self.pausereq = Signal(bool(0))  # Pause Request
        self.pauseval = Signal(intbv(0)[16:])  # Pause Value


class HostManagementInterface():
    """ Host - Management Interface.

    Attributes:
        clk (1 Bit) - Reference Clock for Management/Configuration
            Operations.(>10MHz)
        opcode (2 Bits) - Define Operation for MDIO Interface. Bit 1 also
            used as control signal for configuration data transfer.
        regaddr (10 Bits) - Address of Register to be accessed. According to
            Table 8.2, Page 27, Xilinx UG 144 doc.
        wrdata (32 bits) - Data write.
        rddata (32 bits) - Data read.
        miimsel (1 bit) - Set by Host. When High MDIO interface Accessed,
            Else Configuration registers.
        hostreq (1 Bit) - Set by Host to Indicate ongoing MDIO transaction.
        miimrdy (1 Bit) - Set by MDIO Interface to indicate ready for
            new transaction.

    """

    def __init__(self):
        self.clk = Signal(bool(0))
        self.opcode = Signal(intbv(0)[2:])
        self.regaddress = Signal(intbv(0)[10:])
        self.wrdata = Signal(intbv(0)[32:])
        self.rddata = Signal(intbv(0)[32:])
        self.miimsel = Signal(bool(1))
        self.hostreq = Signal(bool(0))
        self.miimrdy = Signal(bool(1))

    def writeconfig(self, addr, data):
        """Transactor for writing to configuration registers.

        Writes the data over the configuration register present at given
        address.

        Args:
            addr (10 Bits) - Address of the Configuration Register
                to be written.
            data (32 bits) - The value of the register to be written.

        Note:
            Refer Xilinx User Guide 144(1-GEMAC), Table 8-2 through 8-12,
            Pg 77-83, for list of addresses and interpretation of data.

        """
        self.miimsel.next = 0
        self.opcode.next = 0
        self.regaddress.next = intbv(addr)[10:]
        self.wrdata.next = intbv(data)[32:]
        yield self.clk.posedge
        self.miimsel.next = 1
        self.regaddress.next = 0
        self.wrdata.next = 0

    def readconfig(self, addr):
        """Transactor for reading the configuration registers.

        Writes the value of configuration register, corresponding to the
        address provided, over the 'rddata'.

        Args:
            addr (10 Bits) - Address of the Configuration Register to be read.

        Note:
            Refer Xilinx User Guide 144(1-GEMAC), Table 8-2 through 8-12,
            Pg 77-83, for list of addresses and interpretation of data.

        """
        self.miimsel.next = 0
        self.opcode.next = 0b10
        self.regaddress.next = intbv(addr)[10:]
        yield self.clk.posedge
        self.miimsel.next = 1
        self.opcode.next = 0
        self.regaddress.next = 0
        yield self.clk.posedge

    def writeaddrtable(self, loc, addr):
        """ Transactor for adding/editing an MAC address in the address table.

        Writes the given address at the given location in the address table
        which shall be used by address filter.

        Args:
            loc (2 bits) - index of Address table in the range 0-3.
            addr(48 bits) - the MAC address to be written.

        """
        yield self.writeconfig(0x388, intbv(addr)[32:])
        yield self.writeconfig(0x38C,
                               ((intbv(loc)[2:] << 16) | intbv(addr)[48:32]))

    def readaddrtable(self, loc):
        """ Transactor for accessomg an MAC address in the address table.

        Access the MAC address at the given location in the address table.
        The address appears on 'rddata' over two consecutive cycles as below.
        MAC Address = {rddata2[16:], rddata1[32:]} where 'rddata1' and
        'rddata2' are value at rddata at 1st and 2nd cycle respectively.

        Args:
            loc (2 bits) - index of Address table in the range 0-3.
            addr (48 bits) - the MAC address to be written.

        """
        yield self.writeconfig(0x38C, ((1 << 23) | (intbv(loc)[2:] << 16)))
        yield self.clk.posedge

    def mdiowriteop(self, opcode, regaddress, data, block=True):
        """Transactor for initiating an MDIO Write Operation.

        Initiates the MDIO write operation over the 'MDIOInterface'.
        The completion of the operation is signaled by posedge of 'miimrdy'.

        Args:
            opcode (2 bits) - Takes value 00(set address) and 01(write).
            regaddress (10 bits) - The first 5 bits should correspond to PHY
                address and the latter 5 bits to regaddress of the PHY.
            data (16 bits) -
            block (Optional[boolean]) - Waits for the operation for completing
                before returning if True, returns immediately after initiating
                the operation otherwise. Defaults to True.

        """
        if not self.miimrdy:
            yield self.miimrdy.posedge
        self.miimsel.next = 1
        self.hostreq.next = 1
        self.opcode.next = opcode[2:]
        self.regaddress.next = regaddress[10:]
        self.wrdata.next = data[16:]
        yield self.clk.posedge
        self.hostreq.next = 0
        self.opcode.next = 0
        self.regaddress.next = 0
        self.wrdata.next = 0
        if block:
            yield self.miimrdy.posedge

    def mdioreadop(self, opcode, regaddress, block=True):
        """ Transactor for initiating an MDIO Read Operation.

        Initiates the MDIO read operation over the 'MDIOInterface'.
        The completion of the operation is signaled by posedge of 'miimrdy'
        after which the data can be read from lower 16 bits of 'rddata'.

        Args:
            opcode (2 bits) - Takes value 10(read increment) and 11(read).
            regaddress (10 bits) - The first 5 bits should correspond to PHY
                address and the latter 5 bits to regaddress of the PHY.
            block (Optional[boolean]) - Waits for the operation for completing
                before returning if True, returns immediately after initiating
                the operation otherwise. Defaults to True.

        """
        if not self.miimrdy:
            yield self.miimrdy.posedge
        self.miimsel.next = 1
        self.hostreq.next = 1
        self.opcode.next = opcode[2:]
        self.regaddress.next = regaddress[10:]
        yield self.clk.posedge
        self.hostreq.next = 0
        self.opcode.next = 0
        self.regaddress.next = 0
        if block:
            yield self.miimrdy.posedge


class MDIOInterface:
    """ Management Data Input-Output Interface.

    Attributes:
        mdc - Management Clock, programmable frequency derived from host_clk.
        mdioIn - Input data signal from PHY for its configuration and
            status.(TriStateBuffer Connected)
        mdioOut - Output data signal from PHY for its configuration and
            status.(TriStateBuffer Connected)
        mdioTri - TriState Control for Signals - Low Indicating mdioOut to be
            asserted to the MDIO bus.

    """
    def __init__(self):
        self.mdc = Signal(bool(0))
        self.tri = Signal(bool(0))
        self.inn = Signal(bool(0))
        self.out = Signal(bool(0))


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
        self.clk = Signal(bool(0))
        self.data = Signal(intbv(0)[8:])  # Receive Data
        self.dv = Signal(bool(0))  # Receive Data Valid
        self.good = Signal(bool(0))  # Receive Good Frame
        self.bad = Signal(bool(0))  # Receive Bad Frame
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
    """ Transmit Engine - CLient FIFO Interface

    Attributes:
        clk (1 bit) - Clock from client used for all transmit operations.
        data (8 bits) - Transmit Data
        dv (1 bit) - Data valid bit
        ifgdelay (16 bits) - InterFrameGap Delay between two Transmit Frames.
        ack (1 bit) - Acknowledge bit driven by engine to indicate start
            transmitting frames.
        underrun (1 bit) - Driven by Client to stop transmitting current frame.
        collision (1 bit) - 
        retrasmit (1 bit) - 
    """
    def __init__(self):
        # Client Transmitter Interface
        self.clk = Signal(bool(0))
        self.data = Signal(intbv(0)[8:])  # Transmit Data
        self.dv = Signal(bool(0))  # Transmit Data Valid
        self.ifgdelay = Signal(intbv(0)[16:])  # Transmit InterFrameGap Delay
        self.ack = Signal(bool(0))  # Transmit Acknowledge
        self.underrun = Signal(bool(0))  # Transmit Underrun
        self.collision = Signal(bool(0))
        self.retransmit = Signal(bool(0))

    def tx(self, datastream):
        self.data.next = datastream[0]
        self.dv.next = True
        yield self.ack.posedge
        for i in range(1, len(datastream)):
            yield self.clk.posedge
            self.data.next = datastream[i]
        yield self.clk.posedge
        self.dv.next = False
        yield self.clk.posedge


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


class ClientInterface:
    def __init__(self):
        self.rx = RxFIFOClientInterface()
        self.tx = TxFIFOClientInterface()
