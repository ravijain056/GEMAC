from myhdl import block, Signal, intbv, always_seq, concat


rx0, rx1, tx, flow, managementreg, ucast0, \
    ucast1, addrtable0, addrtable1, addrfiltermode, reserved = range(11)


class mdioData:
    def __init__(self):
        self.hostclk_count = Signal(intbv(0)[5:])  # Used to drive mdc
        self.wrdata = Signal(intbv(0)[32:])
        self.rddata = Signal(intbv(0)[16:])
        self.rdindex = Signal(intbv(17, min=0, max=18))  # in index during rdop
        self.wrindex = Signal(intbv(64, min=0, max=65))
        self.wrdone = Signal(bool(0))
        self.done = Signal(bool(0))

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
def management(hostintf, mdiointf, reset):

    configregisters = [Signal(intbv(0)[32:]) for _ in range(10)]
    addresstable = [Signal(intbv(0)[48:]) for _ in range(4)]
    addrtableread = Signal(bool(0))
    addrtablelocation = Signal(intbv(0)[2:])
    mdiodata = mdioData()

    def getregindex(addr):
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

    @always_seq(hostintf.clk.posedge, reset=reset)
    def readData():

        if (not hostintf.miimsel) and hostintf.regaddress[9]:
            regindex = getregindex(hostintf.regaddress)

            if regindex != reserved and hostintf.opcode[1]:  # ReadConfig
                hostintf.rddata.next = configregisters[regindex]

            if regindex == addrtable1 and not hostintf.opcode[1] and \
                    hostintf.wrdata[23]:  # Address Table Read 0
                loc = hostintf.wrdata[18:16]
                addrtablelocation.next = loc
                hostintf.rddata.next = addresstable[loc][32:0]
                addrtableread.next = True

        if not hostintf.miimrdy and mdiodata.done:  # MDIO Read
            hostintf.rddata.next = mdiodata.rddata[16:]

        if addrtableread:  # Address Table Read 1
            addrtableread.next = False
            hostintf.rddata.next = addresstable[addrtablelocation][48:32]

    @always_seq(hostintf.clk.posedge, reset=reset)
    def writeConfig():

        if (not hostintf.miimsel) and hostintf.regaddress[9] and \
                (not hostintf.opcode[1]):
            regindex = getregindex(hostintf.regaddress)

            # Config Registers Write
            if regindex != reserved:
                configregisters[regindex].next = hostintf.wrdata

            # Address Table Write
            if regindex == addrtable1 and not hostintf.wrdata[23]:
                addresstable[hostintf.wrdata[18:16]].next = \
                    (hostintf.wrdata[16:0] << 32) | configregisters[addrtable0]

    @always_seq(hostintf.clk.posedge, reset=reset)
    def mdcdriver():
        clkDiv = configregisters[managementreg][5:]  # + 1 * 2
        if mdiodata.hostclk_count == clkDiv:
            mdiointf.mdc.next = not mdiointf.mdc
            mdiodata.hostclk_count.next = 0
        else:
            mdiodata.hostclk_count.next = mdiodata.hostclk_count + 1

    @always_seq(hostintf.clk.posedge, reset=reset)
    def mdioinitiate():
        if hostintf.hostreq and hostintf.miimsel and \
                hostintf.miimrdy:
            hostintf.miimrdy.next = False
            mdiointf.tri.next = False
            wrdata = concat(intbv(0b01)[2:], hostintf.opcode[2:],
                            hostintf.regaddress[10:], intbv(0b10)[2:],
                            hostintf.wrdata[16:])
            mdiodata.wrdata.next = wrdata[32:]
        if not hostintf.miimrdy:
            if mdiodata.wrdone:
                mdiointf.tri.next = True
            if mdiodata.done:
                hostintf.miimrdy.next = True

    @always_seq(mdiointf.mdc.posedge, reset=reset)
    def mdiooperation():
        mdioenable = configregisters[managementreg][5]
        if (not hostintf.miimrdy) and mdioenable:
            if not mdiointf.tri:
                mdiointf.out.next = 1 if mdiodata.wrindex > 31 \
                    else mdiodata.wrdata[mdiodata.wrindex]
                if mdiodata.wrindex == 0 or \
                        (mdiodata.wrindex == 18 and mdiodata.wrdata[29]):
                    mdiodata.wrdone.next = True
                    mdiodata.wrindex.next = 62
                    if not mdiodata.wrdata[29]:  # Write Operation Exit
                        mdiodata.done.next = True
                else:
                    mdiodata.wrindex.next = mdiodata.wrindex - 1
            else:  # Only in case of read operation
                if mdiodata.rdindex == 17:
                    mdiodata.rdindex.next = 16
                    mdiodata.rddata.next = 0
                elif mdiodata.rdindex == 16:  # mdiointf.inn should be 0
                    mdiodata.rdindex.next = 15
                else:
                    mdiodata.rddata.next = mdiodata.rddata | \
                        (mdiointf.inn << mdiodata.rdindex)
                    if mdiodata.rdindex == 0:
                        mdiodata.rdindex.next = 17
                        mdiodata.done.next = True
                    else:
                        mdiodata.rdindex.next = mdiodata.rdindex - 1
        else:
            mdiodata.wrdone.next = False
            mdiodata.done.next = False

    return readData, writeConfig, mdcdriver, mdioinitiate, mdiooperation
