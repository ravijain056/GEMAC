from myhdl import block

@block
def gmii(txData2GMII, rxData2Engine,
        gtxClk, gmiiTxd, gmiiTxEn, gmiiTxEr,
        gmiiRxClk, gmiiRxd, gmiiRxDv, gmiiRxEr):
    
    """
    *GMII - PHY Interface for 1 - Gigabit Ethernet operation*
    
    gtxClk - Reference Clk for transmit operation from Host
    txData2GMII - Data from Transmit Engine to be passed onto PHY 
    gmiiTxd - transmit Data to PHY
    gmiiTxEn - Control Signal to PHY
    gmiiTxEr - Control Signal to PHY
    
    gmiiRxClk - Reference Clk for receive operations from PHY 
    rxData2Engine - Data passed to Receive Engine 
    gmiiRxd - receive Data from PHY
    gmiiRxDv - Control Signal from PHY
    gmiiRxEr - Control Signal from PHY
    
    """

    return instances()