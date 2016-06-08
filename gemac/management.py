from myhdl import block, Signal, intbv, always_seq


rx0, rx1, tx, flow, managementreg, ucast0, \
    ucast1, addrtable0, addrtable1, addrfiltermode, reserved = range(11)

# pre, st, op, phyaddr, regaddr, ta, wrdata, rddata, hostclk_count, \
#    rdindex, wrindex = range(11)


class mdioData:
    def __init__(self):
        self.pre = Signal(intbv(0xFFFFFFFF)[32:])
        self.st = Signal(intbv(0b01)[2:])
        self.op = Signal(intbv(0)[2:])
        self.phyaddr = Signal(intbv(0)[10:5])
        self.regaddr = Signal(intbv(0)[5:])
        self.ta = Signal(intbv(0b10)[2:])
        self.wrdata = Signal(intbv(0)[16:])
        self.rddata = Signal(intbv(0)[16:])
        self.hostclk_count = Signal(intbv(0)[5:])  # Used to drive mdc
        self.rdindex = Signal(intbv(17, min=0, max=18))  # in index during rdop
        self.wrindex = Signal(intbv(0, min=0, max=66))

    def mdioread(self, mdioin):
        if self.rdindex == 17:
            self.rdindex.next = 16
        if self.rdindex == 16 and mdioin is False:
            self.rdindex.next = 15
        else:
            self.rddata.next = self.rddata & (mdioin << self.rdindex)
            self.rdindex.next = self.rdindex - 1
            if self.rdindex == 0:
                self.rddata.next = 0
                self.rdindex.next = 17
                return True
        return False

    def next(self):
        self.wrindex.next = self.wrindex + 1
        if self.wrindex <= 31:
            return self.pre[self.wrindex]
        elif self.wrindex <= 33:
            return self.st[self.wrindex-32]
        elif self.wrindex <= 35:
            return self.op[self.wrindex-34]
        elif self.wrindex <= 40:
            return self.phyaddr[self.wrindex-36]
        elif self.wrindex <= 45:
            return self.regaddr[self.wrindex-41]
        elif (not self.op[1]) and self.wrindex <= 47:
            return self.ta[self.wrindex-46]
        elif (not self.op[1]) and self.wrindex <= 63:
            return self.wrdata[self.wrindex-48]
        else:
            self.wrindex.next = 0
            return None

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


@block
def management(host_interface, mdio_interface):

    configregisters = [Signal(intbv(0)[32:0]) for _ in range(10)]
    """
    mdiodata = [Signal(intbv(0xFFFFFFFF)[32:]),  # pre
                Signal(intbv(0b01)[2:]),         # st
                Signal(intbv(0)[2:]),            # op
                Signal(intbv(0)[5:]),            # phyaddr
                Signal(intbv(0)[5:]),            #
                Signal(intbv(0b10)[2:]),
                Signal(intbv(0)[16:]),
                Signal(intbv(0)[16:]),
                Signal(intbv(0)[16:]),
                Signal(intbv(0)[5:]),
                Signal(intbv(17, min=0, max=18)),
                Signal(intbv(0, min=0, max=66))]
    """
    mdiodata = mdioData()
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
            return reserved

    def storedata(opcode, hostaddr, wrdata):
        mdiodata.op.next = opcode[2:]
        mdiodata.phyaddr.next = hostaddr[10:5]
        mdiodata.regaddr.next = hostaddr[5:]
        mdiodata.wrdata.next = wrdata[16:]

    @always_seq(host_interface.clk.posedge, reset=None)
    def readConfig():
        if (not host_interface.miimsel) and host_interface.regaddress[9] and \
                host_interface.opcode[1]:
            regindex = getregisternumber(host_interface.regaddress)
            if regindex != reserved:
                host_interface.rddata.next = configregisters[regindex]

    @always_seq(host_interface.clk.posedge, reset=None)
    def writeConfig():
        if (not host_interface.miimsel) and host_interface.regaddress[9] and \
                (not host_interface.opcode[1]):
            regindex = getregisternumber(host_interface.regaddress)
            if regindex != reserved:
                configregisters[regindex].next = host_interface.wrdata

    # @TODO: Address Table Read.

    @always_seq(host_interface.clk.posedge, reset=None)
    def mdcdriver():
        clkDiv = configregisters[managementreg][5:]  # + 1 * 2
        if mdiodata.hostclk_count == clkDiv:
            mdio_interface.mdc.next = not mdio_interface.mdc
            mdiodata.hostclk_count.next = 0
        else:
            mdiodata.hostclk_count.next = mdiodata.hostclk_count + 1

    # May req to recheck trigerring signal according to Page 87, Xilinx UG144
    @always_seq(host_interface.clk.posedge, reset=None)
    def mdioinitiate():
        if host_interface.hostreq and host_interface.miimsel and \
                host_interface.miimrdy:
            host_interface.miimrdy.next = False
            mdio_interface.tri.next = False
            storedata(host_interface.opcode, host_interface.regaddress,
                      host_interface.wrdata)

    @always_seq(mdio_interface.mdc.posedge, reset=None)
    def mdiooperation():
        mdioenable = configregisters[managementreg][5]
        if (not host_interface.miimrdy) and mdioenable:
            if not mdio_interface.tri:
                if mdiodata.next() is None:
                    if mdiodata.op[1]:  # Read Operation
                        mdio_interface.tri.next = True
                    elif not mdiodata.op[1]:  # Write Operation
                        mdio_interface.tri.next = True
                        host_interface.miimrdy.next = True
                else:
                    mdio_interface.out.next = mdiodata.next()
            elif mdio_interface.tri:  # Only in case of read operation
                if mdiodata.mdioread(mdio_interface.inn):
                    host_interface.miimrdy.next = True
                    host_interface.rddata.next = mdiodata.rddata[16:]

    return readConfig, writeConfig, mdcdriver, mdioinitiate, mdiooperation
