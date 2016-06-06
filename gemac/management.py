from myhdl import block, Signal, intbv, always_seq, always_comb
from myhdl._ShadowSignal import TristateSignal


rx0, rx1, tx, flow, managementreg, ucast0, \
    ucast1, addrtable0, addrtable1, addrfiltermode = range(10)
hostclk_count = 0


class mdioData:
    def __init__(self, opcode, hostaddr, wrdata):
        self.pre = intbv(0xFFFFFFFF)[32:]
        self.st = intbv(0b01)[2:]
        self.op = opcode[2:]
        self.phyadd = hostaddr[10:5]
        self.regadd = hostaddr[5:]
        self.wrdata = wrdata[16:]


@block
def management(host_interface, mdio_interface):

    """
    Management Data - Input Output Interface.

    hostClk - Reference Clk for Management/Configuration Operations. >10MHz
    hostOpcode (2 Bits) - Define Operation for MDIO Interface. Bit 1 also
        used as control signal for configuration data transfer.
    hostAddr (10 Bits) - Address of Register to be accessed. According to
        Table 8.2, Page 27, Xilinx UG 144 doc.
    hostWriteData (32 bits) - Data write.
    hostReadData (32 bits) - Data read.
    hostMIIM_sel - Set by Host. When High MDIO interface Accessed,
        Else Configuration registers.
    hostReq - Set by Host to Indicate ongoing MDIO transaction.
    hostMIIM_rdy - Set by MDIO Interface to indicate ready for new transaction.

    mdc - Management Clock: programmable frequency derived from host_clk.
    mdioIn - Input data signal from PHY for its configuration and
        status.(TriStateBuffer Connected)
    mdioOut - Output data signal from PHY for its configuration and
        status.(TriStateBuffer Connected)
    mdioTri - TriState Control for Signals - Low Indicating mdioOut to be
        asserted to the MDIO bus.

    """

    mdioout = Signal(bool(0))
    # mdioin = Signal(bool(0))
    mdioin = TristateSignal(bool(0))
    mdioindriver = mdioin.driver()
    mdiotri = Signal(bool(0))
    mdio_interface.mdiodriver = mdio_interface.mdioio.driver()

    configregisters = [Signal(intbv(0)[32:0]) for _ in range(10)]

    def getregisternumber(addr):
        if addr >= 0x200 and addr <= 0x23F:
            return rx0
        elif addr >= 0x240 and addr <= 0x27F:
            return rx1
        elif addr >= 0x280 and addr <= 0x2BF:
            return tx
        elif addr >= 0x2C0 and addr <= 0x2FF:
            return flow
        elif addr >= 0x340 and addr <= 0x37F:
            return managementreg
        elif addr >= 0x380 and addr <= 0x383:
            return ucast0
        elif addr >= 0x384 and addr <= 0x387:
            return ucast1
        elif addr >= 0x388 and addr <= 0x38B:
            return addrtable0
        elif addr >= 0x38C and addr <= 0x38F:
            return addrtable1
        elif addr >= 0x390 and addr <= 0x393:
            return addrfiltermode
        else:
            raise Exception

    @always_seq(host_interface.clk.posedge, reset=None)
    def readConfig():
        if((not host_interface.miimsel) and host_interface.regaddress[9] and
                host_interface.opcode[1]):
            host_interface.rddata.next = \
                configregisters[getregisternumber(host_interface.regaddress)]

    @always_seq(host_interface.clk.posedge, reset=None)
    def writeConfig():
        if((not host_interface.miimsel) and host_interface.regaddress[9] and
                (not host_interface.opcode[1])):
            configregisters[getregisternumber(host_interface.regaddress)]\
                .next = host_interface.wrdata

    # @TODO: Address Table Read.

    @always_comb
    def mdiodriver():
        mdio_interface.mdiodriver.next = mdioout if mdiotri else None
        mdioindriver.next = mdio_interface.mdioio if not mdiotri else None
        # mdioin.next = False if mdio_interface.mdioio is None else mdio_interface.mdioio

    @always_seq(host_interface.clk.posedge, reset=None)
    def mdcdriver():
        global hostclk_count
        clkDiv = (configregisters[managementreg][5:] + 1)  # * 2
        hostclk_count += 1
        if hostclk_count == clkDiv:
            mdio_interface.mdc.next = not mdio_interface.mdc
            hostclk_count = 0

    # May req to recheck trigerring signal according to Page 87, Xilinx UG144
    @always_seq(host_interface.clk.posedge, reset=None)
    def mdioinitiate():
        if host_interface.hostreq and host_interface.miimsel:
            host_interface.miimrdy.next = 0
            mdiodata = mdioData(host_interface.opcode,
                                host_interface.regaddress,
                                host_interface.wrdata)
            # yield host_interface.clk.posedge
            if host_interface.opcode[1]:  # Read Operation
                host_interface.rddata.next = mdioread(mdiodata)
            elif not host_interface.opcode[1]:  # Write Operation
                mdiowrite(mdiodata)
            host_interface.miimrdy.next = 1

    def mdiostream(datalist):
        yield host_interface.clk.posedge
        mdiotri.next = 1
        yield mdio_interface.mdc.posedge
        for data in datalist:
            for i in reversed(range(len(data))):
                mdioout.next = data[i]
                yield mdio_interface.mdc.posedge
        mdiotri.next = 0

    def mdiowrite(mdiodata):
        mdiodata.ta = intbv(0b10)[2:]
        mdiostream([mdiodata.pre, mdiodata.st, mdiodata.op, mdiodata.phyadd,
                    mdiodata.regadd, mdiodata.ta, mdiodata.wrdata])
        host_interface.miimrdy.next = 1

    def mdioread(mdiodata):
        mdiostream([mdiodata.pre, mdiodata.st, mdiodata.op, mdiodata.phyadd,
                    mdiodata.regadd])
        yield mdio_interface.mdc.posedge
        yield mdio_interface.mdc.posedge  # Two turnaround bits
        host_interface.rddata.next = 0
        rddata = intbv(0)[16:]
        for i in reversed(range(len(rddata))):
            yield mdio_interface.mdc.posedge
            rddata[i] = mdioin
        return rddata

    return readConfig, writeConfig, mdiodriver, mdcdriver, mdioinitiate
