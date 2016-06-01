from myhdl import block, instances


@block
def rxEngine(rxclk, rxd2client, rxd2engine, rxder):

    """
    *Receiver Engine*
    -- Accepts Ethernet frame data from the GMII Block, removes the preamble field at the start of the frame, 
       removes padding bytes and Frame Check Sequence. It performs error detection on the received frame using 
       information such as the frame check sequence field, received GMII error codes, and legal frame size 
       boundaries.

    gmiiRxClk - Reference Clk for Receive Operations
    rxData2Client - Receive Data Channel to Client
    rxData2Engine - Receive Data Channel from GMII
    rxDataError - Set High by the Engine at the end of the frame if any Error is detected. Set Low otherwise. To Client.

    """

    return instances()