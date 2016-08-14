# -*- coding: utf-8 -*-

from myhdl import block, Signal, intbv, always_seq, concat

rx0, rx1, tx, flow, managementreg, ucast0, \
    ucast1, addrtable0, addrtable1, addrfiltermode, reserved = range(11)
""" Indexing of configuration Registers"""


class mdioData:
    """ Collection of Signals required for MDIO transaction."""
    def __init__(self):
        self.hostclk_count = Signal(intbv(0)[5:])
        """ Used To drive mdc from hostclk. """

        self.wrdata = Signal(intbv(0)[32:])
        self.rddata = Signal(intbv(0)[16:])
        """ Used to store data to be read/write from the host interface. """

        self.rdindex = Signal(intbv(17, min=0, max=18))
        self.wrindex = Signal(intbv(62, min=0, max=63))
        """ Used for indexing the MDIO transactoins. """

        self.wrdone = Signal(bool(0))
        self.done = Signal(bool(0))
        """ Used to Signal completion of MDIO transactions. """


@block
def management(hostintf, mdiointf, configregs, addrtable, reset):
    """ Management Block.

    Responsible for host interaction for read/write of configuration registers,
    Address Table and conversion of Host transactions to MDIO MII transactions.

    Args:
        hostintf - Instance of 'HostManagementInterface' class in interfaces.
        mdiointf - Instance of 'MDIOInterface' class in interfaces.
        configregs - List of 10 32-bits wide Configuration Registers.
        addrtable - List of 4 48-bits wide MAC Addresses to be used by
            Address Filter.
        reset: Asynchronous reset Signal from Host

    Attributes:
        addrtableread - Signal used for address table read operation.
        addrtablelocation - Sampled value of address table location while
            accessing it.
        mdiodata - Collection of Signals used for performing MDIO operations.

    Note:
        Designed according to usage described in Xilinx User Guide
        144(1-GEMAC), Pg 77-89.

    """
    addrtableread = Signal(bool(0))
    addrtablelocation = Signal(intbv(0)[2:])
    mdiodata = mdioData()

    def getregindex(addr):
        """Task/Function to get index of configuration registers.

        Args:
            addr (10 bits) - The register address.

        Returns:
            int: Configuration Register index.

        """
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
        """Process block to drive 'hostintf.rddata'

        Drives rddata in case of access of Configuration Registers/Address
        Table or on completion of MDIO Read operation.

        """
        if (not hostintf.miimsel) and hostintf.regaddress[9]:
            regindex = getregindex(hostintf.regaddress)

            if regindex != reserved and hostintf.opcode[1]:  # ReadConfig
                hostintf.rddata.next = configregs[regindex]

            if regindex == addrtable1 and not hostintf.opcode[1] and \
                    hostintf.wrdata[23]:  # Address Table Read 0
                loc = hostintf.wrdata[18:16]
                addrtablelocation.next = loc
                hostintf.rddata.next = addrtable[loc][32:0]
                addrtableread.next = True

        if not hostintf.miimrdy and mdiodata.done:  # MDIO Read
            hostintf.rddata.next = mdiodata.rddata[16:]

        if addrtableread:  # Address Table Read 1
            addrtableread.next = False
            hostintf.rddata.next = addrtable[addrtablelocation][48:32]

    @always_seq(hostintf.clk.posedge, reset=reset)
    def writeConfig():
        """Process to write into configuration registers and address table."""
        if (not hostintf.miimsel) and hostintf.regaddress[9] and \
                (not hostintf.opcode[1]):
            regindex = getregindex(hostintf.regaddress)

            # WriteConfig
            if regindex != reserved:
                configregs[regindex].next = hostintf.wrdata

            # Address Table Write
            if regindex == addrtable1 and not hostintf.wrdata[23]:
                addrtable[hostintf.wrdata[18:16]].next = \
                    (hostintf.wrdata[16:0] << 32) | configregs[addrtable0]

        # Reverting resets
        if configregs[rx1][31]:
            configregs[rx1].next = configregs[tx] & 0x7FFFFFFF
        if configregs[tx][31]:
            configregs[tx].next = configregs[tx] & 0x7FFFFFFF


    @always_seq(hostintf.clk.posedge, reset=reset)
    def mdcdriver():
        """Process to drive 'mdiointf.mdc' from 'hostintf.clk'."""
        clkDiv = configregs[managementreg][5:]  # + 1 * 2
        if mdiodata.hostclk_count == clkDiv:
            mdiointf.mdc.next = not mdiointf.mdc
            mdiodata.hostclk_count.next = 0
        else:
            mdiodata.hostclk_count.next = mdiodata.hostclk_count + 1

    @always_seq(hostintf.clk.posedge, reset=reset)
    def mdioinitiate():
        """Process to initiate and terminate MDIO operation."""
        if hostintf.hostreq and hostintf.miimsel and hostintf.miimrdy:
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
        """Process to perform the MDIO Read/Write Operation.

        Drives the 'MDIOInterface' signals in accordance with the operation
        to be performed (read/write). Basically converts parallel data to
        serial data over 'mdiointf.out' (write) and vice-versa (read).

        """
        mdioenable = configregs[managementreg][5]
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
