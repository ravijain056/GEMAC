from myhdl import block, Signal, intbv, instances


@block
def mdio(management_interface, mdio_interface):

    """
    Management Data - Input Output Interface.

    hostClk - Reference Clk for Management/Configuration Operations. >10MHz
    hostOpcode (2 Bits) - Define Operation for MDIO Interface. Bit 1 also used as control signal for configuration data transfer. 
    hostAddr (10 Bits) - Address of Register to be accessed. According to Table 8.2, Page 27, Xilinx UG 144 doc.  
    hostWriteData (32 bits) - Data write. 
    hostReadData (32 bits) - Data read.
    hostMIIM_sel - Set by Host. When High MDIO interface Accessed, Else Configuration registers.
    hostReq - Set by Host to Indicate ongoing MDIO transaction.
    hostMIIM_rdy - Set by MDIO Interface to indicate ready for new transaction.

    mdc - Management Clock: programmable frequency derived from host_clk.
    mdioIn - Input data signal from PHY for its configuration and status.(TriStateBuffer Connected)
    mdioOut - Output data signal from PHY for its configuration and status.(TriStateBuffer Connected)
    mdioTri - TriState Control for Signals - Low Indicating mdioOut to be asserted to the MDIO bus.

    """
    # Configuration Registers
    rxconfig0 = Signal(intbv(0)[32:0])
    rxconfig1 = Signal(intbv(0)[32:0])
    txconfig = Signal(intbv(0)[32:0])
    flowconfig = Signal(intbv(0)[32:0])
    managementconfig = Signal(intbv(0)[32:0])
    ucast_addr0 = Signal(intbv(0)[32:0])
    ucast_addr1 = Signal(intbv(0)[32:0])
    addr_tableconfig0 = Signal(intbv(0)[32:0])
    addr_tableconfig1 = Signal(intbv(0)[32:0])
    addr_filtermode = Signal(intbv(0)[32:0])

    return instances()
