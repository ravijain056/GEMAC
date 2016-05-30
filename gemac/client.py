from myhdl import block, instances


@block
def client(gtxClk, txData, txDataValid, txIFG_delay,
           tx_ack, tx_underrun, txData2Engine,
           gmiiRxClk, rxData, rxDataValid, rxGoodFrame,
           rxBadFrame, rxData2Client, rxDataError):

    """
    *Client Side Interface*

    gtxClk - Reference Clk for transmit Operations from Host
    txData (8 bits) - Transmit Data Channel from Host
    txDataValid - Control Signal From Host - High When the Frame Data is being transmitted, Low otherwise.
    txIFG_delay(8 bits) - InterFrameGap Delay 
    tx_ack - Control Signal From Client To Host - To indicate host to start transmitting Frame Data.
    tx_underrun - Signal From Host - To force the core to drop the current frame being transmitted.
    txData2Engine - Transmit Data Channel to Engine

    gmiiRxClk - Reference Clk for receive operations from PHY 
    rxData (8 bits) - Receive Data Channel to Host
    rxDataValid - Control Signal from GMII - High When the Frame Data is being transmitted, Low otherwise.
    rxGoodFrame - Control Signal from RxEngine - To indicate proper reception
    rxBadFrame - Control Signal from RxEngine - To indicate improper reception and the received data required to be dropped
    rxData2Client - Receive Data Channel From Engine 

    """

    return instances()