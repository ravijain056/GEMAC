from myhdl import block, Signal, intbv, always_seq


rx0, rx1, tx, flow, management, ucast0, \
    ucast1, addrtable0, addrtable1, addrfiltermode = range(10)


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

    configregisters = [Signal(intbv(0))[32:0] for _ in range(10)]

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
            return management
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
                host_interface.opcode):
            host_interface.rddata.next = \
                configregisters[getregisternumber(host_interface.regaddress)]

    @always_seq(host_interface.clk.posedge, reset=None)
    def writeConfig():
        if((not host_interface.miimsel) and host_interface.regaddress[9] and
                (not host_interface.opcode)):
            configregisters[getregisternumber(host_interface.regaddress)]\
                .next = host_interface.wrdata

    # @TODO: Address Table Read.

    return readConfig, writeConfig
