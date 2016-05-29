from myhdl import block

@block
def gemac( 
        #Client Transmitter Interface
        gtxClk, txData, txDataValid, txIFG_delay, tx_ack, tx_underrun,
        #Client Receiver Interface
        rxData, rxDataValid, rxGoodFrame, rxBadFrame,
        #Flow Control Interface
        pauseReq, pauseVal,
        #Client Management Interface
        hostClk, hostOpcode, hostAddr, hostWriteData, hostReadData, hostMIIM_sel, hostReq, hostMIIM_rdy
        #Asyncronous reset signal
        reset,
        #GMII PHY Transmitter Interface
        gmiiTxd, gmiiTxEn, gmiiTxEr,
        #GMII PHY Receiver Interface
        gmiiRxClk, gmiiRxd, gmiiRxDv, gmiiRxEr,
        #MDIO PHY Interface
        mdc, mdioIn, mdioOut, mdioTri):
    
    
    
    return instances()