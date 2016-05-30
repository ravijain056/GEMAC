from myhdl import block, Signal, intbv
from gemac import client, txEngine, rxEngine, flowControl, gmii, mdio

@block
def gemac(
        # Client Transmitter Interface
        gtxClk, txData, txDataValid, txIFG_delay, tx_ack, tx_underrun,
        # Client Receiver Interface
        rxData, rxDataValid, rxGoodFrame, rxBadFrame,
        # Flow Control Interface
        pauseReq, pauseVal,
        # Client Management Interface
        hostClk, hostOpcode, hostAddr, hostWriteData, hostReadData,
        hostMIIM_sel, hostReq, hostMIIM_rdy,
        # Asynchronous reset signal
        reset,
        # GMII PHY Transmitter Interface
        gmiiTxd, gmiiTxEn, gmiiTxEr,
        # GMII PHY Receiver Interface
        gmiiRxClk, gmiiRxd, gmiiRxDv, gmiiRxEr,
        # MDIO PHY Interface
        mdc, mdioIn, mdioOut, mdioTri):

    transmitPauseFrame = Signal(bool(0))
    rxDataError = Signal(bool(0))
    txData2Engine = Signal(intbv(0)[8:])
    txData2GMII = Signal(intbv(0)[8:])
    rxData2Engine = Signal(intbv(0)[8:])
    rxData2Client = Signal(intbv(0)[8:])
    sampledPauseVal = Signal(intbv(0)[16:])

    clientInst = client(gtxClk, txData, txDataValid, txIFG_delay,
                        tx_ack, tx_underrun, txData2Engine,
                        gmiiRxClk, rxData, rxDataValid, rxGoodFrame,
                        rxBadFrame, rxData2Client, rxDataError)

    txEngineInst = txEngine(gtxClk, txData2Engine, txData2GMII,
                            transmitPauseFrame, sampledPauseVal)

    rxEngineInst = rxEngine(gmiiRxClk, rxData2Client,
                            rxData2Engine, rxDataError)

    flowControlInst = flowControl(pauseReq, pauseVal,
                                  transmitPauseFrame, sampledPauseVal)

    gmiiInst = gmii(txData2GMII, rxData2Engine,
                    gtxClk, gmiiTxd, gmiiTxEn, gmiiTxEr,
                    gmiiRxClk, gmiiRxd, gmiiRxDv, gmiiRxEr)

    mdioInst = mdio(hostClk, hostOpcode, hostAddr, hostWriteData, hostReadData,
                    hostMIIM_sel, hostReq, hostMIIM_rdy,
                    mdc, mdioIn, mdioOut, mdioTri)


    return clientInst, txEngineInst, rxEngineInst, gmiiInst, mdioInst, flowControlInst
