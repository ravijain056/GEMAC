from myhdl import block

@block
def mdio(hostClk, hostOpcode, hostAddr, hostWriteData, hostReadData, hostMIIM_sel, hostReq, hostMIIM_rdy
         mdc, mdioIn, mdioOut, mdioTri):
    
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
    #Configuration Registers
    ReceiverConfig_0 = Signal(intbv(0)[32:0])
    ReceiverConfig_1 = Signal(intbv(0)[32:0])
    TransmitterConfig = Signal(intbv(0)[32:0])
    FlowControlConfig = Signal(intbv(0)[32:0])
    ManagementConfig = Signal(intbv(0)[32:0])
    UniCastAddress_0 = Signal(intbv(0)[32:0])
    UniCastAddress_1 = Signal(intbv(0)[32:0])
    AddressTableConfig_0 = Signal(intbv(0)[32:0])
    AddressTableConfig_1 = Signal(intbv(0)[32:0])
    AddressFilterMode = Signal(intbv(0)[32:0])
    
    return instances()
