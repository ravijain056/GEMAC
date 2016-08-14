from myhdl import block, always_seq, always_comb, Signal, intbv, enum, \
    ResetSignal
from gemac.crc32 import crc32

txstate = enum('IDLE', 'PREAMBLE', 'SFD', 'FIRSTBYTE', 'INFRAME', 'PADDING',
               'ERROR', 'CRC1', 'CRC2', 'CRC3', 'CRC4', 'SENDPAUSE')


@block
def txengine(txclientintf, txgmii_intf, txflowintf, txconfig, sysreset):
    """Transmit Engine.

    Accepts Ethernet frame data from the Client Transmitter interface,
    adds preamble to the start of the frame, add padding bytes and frame
    check sequence. It ensures that the inter-frame spacing between successive
    frames is at least the minimum specified. The frame is then converted
    into a format that is compatible with the GMII and sent to the GMII Block.

    Args:
        txclientintf (TxClientFIFO) - transmit streaming data interface from transmit FIFO.
        txgmii_intf (TxGMII_Interface) - transmit streaming data interface to GMII.
        flow_intf (TxFlowInterface) - transmit flow control interface.
        txconfig (Signal/intbv)(32 bit) - configregisters - Transmitter configuration word.
            See Xilinx_UG144 pdf, Table 8.5, Pg-80 for detailed description.
        reset - System reset
    """

    state = Signal(txstate.IDLE)
    curbyte = Signal(intbv(1, min=0, max=10000))
    pausereq = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)
    ifgwait = Signal(intbv(0)[16:])
    data = Signal(intbv(0)[8:])
    dv = Signal(bool(0))

    clearcrc = Signal(bool(0))
    calccrc = Signal(bool(0))
    crcout = Signal(intbv(0xFFFFFFFF)[32:])

    crc32inst = crc32(txclientintf.clk, clearcrc, calccrc, data, crcout, reset)

    @always_comb
    def assign():
        txgmii_intf.clk.next = txclientintf.clk
        txflowintf.clk.next = txclientintf.clk
        txclientintf.ack.next = state == txstate.FIRSTBYTE
        txgmii_intf.err.next = state == txstate.ERROR
        txflowintf.ispaused.next = state == txstate.IDLE
        clearcrc.next = state == txstate.IDLE
        fcsen = txconfig[29]
        calccrc.next = ((state == txstate.INFRAME or
                        state == txstate.PADDING) and
                        not fcsen) or state == txstate.SENDPAUSE
        reseten = txconfig[31]
        reset.next = sysreset or not reseten

    @always_seq(txclientintf.clk.posedge, reset)
    def curbyteinc():
        """ Index Incrementer """
        if state == txstate.IDLE:
            curbyte.next = 1
        else:
            curbyte.next = curbyte + 1

    @always_seq(txclientintf.clk.posedge, reset)
    def pausecntrl():
        """ Pause request sampler. """
        if txflowintf.pausereq:
            pausereq.next = 1
        elif state == txstate.SENDPAUSE:
            pausereq.next = 0

    @always_seq(txclientintf.clk.posedge, reset)
    def transmitter():
        """ Transmitter logic """
        txen = txconfig[28]
        if txclientintf.underrun:
            state.next = txstate.ERROR

        elif (state == txstate.IDLE) and txen:
            data.next = 0x00
            dv.next = False
            txgmii_intf.data.next = 0x00
            txgmii_intf.dv.next = False
            if ifgwait > 0:
                ifgwait.next = ifgwait - 1
            elif pausereq or (not txflowintf.pauseapply and txclientintf.dv):
                state.next = txstate.PREAMBLE

        elif state == txstate.PREAMBLE:
            data.next = 0x55
            dv.next = True
            txgmii_intf.data.next = data
            txgmii_intf.dv.next = dv
            if curbyte == 7:
                state.next = txstate.SFD

        elif state == txstate.SFD:
            data.next = 0xD5
            txgmii_intf.data.next = data
            if pausereq:
                state.next = txstate.SENDPAUSE
            else:
                state.next = txstate.FIRSTBYTE

        elif state == txstate.FIRSTBYTE:
            ifgen = txconfig[25]
            ifgwait.next = txclientintf.ifgdelay if ifgen else 12
            data.next = txclientintf.data
            txgmii_intf.data.next = data
            state.next = txstate.INFRAME

        elif state == txstate.INFRAME:
            data.next = txclientintf.data
            txgmii_intf.data.next = data
            if not txclientintf.dv:
                jumboen = txconfig[30]
                fcsen = txconfig[29]
                vlanen = txconfig[27]
                if curbyte > (1526 + vlanen * 4) and not jumboen:
                    state.next = txstate.ERROR
                elif fcsen:
                    state.next = txstate.IDLE
                elif curbyte < 68:
                    state.next = txstate.PADDING
                else:
                    state.next = txstate.CRC1

        elif state == txstate.PADDING:
            if curbyte == 68:
                state.next = txstate.CRC1

        elif state == txstate.CRC1:
            txgmii_intf.data.next = crcout[8:]
            state.next = txstate.CRC2

        elif state == txstate.CRC2:
            txgmii_intf.data.next = crcout[16:8]
            state.next = txstate.CRC3

        elif state == txstate.CRC3:
            txgmii_intf.data.next = crcout[24:16]
            state.next = txstate.CRC4

        elif state == txstate.CRC4:
            txgmii_intf.data.next = crcout[32:24]
            state.next = txstate.IDLE

        elif state == txstate.ERROR:
            state.next = txstate.IDLE

        elif state == txstate.SENDPAUSE:
            mcastaddr = 0x0180C2000001
            txgmii_intf.data.next = data
            if curbyte == 9:
                data.next = mcastaddr[48:40]
            elif curbyte == 10:
                data.next = mcastaddr[40:32]
            elif curbyte == 11:
                data.next = mcastaddr[32:24]
            elif curbyte == 12:
                data.next = mcastaddr[24:16]
            elif curbyte == 13:
                data.next = mcastaddr[16:8]
            elif curbyte == 14:
                data.next = mcastaddr[8:]
            elif curbyte == 15:
                data.next = txflowintf.macaddr[8:]
            elif curbyte == 16:
                data.next = txflowintf.macaddr[16:8]
            elif curbyte == 17:
                data.next = txflowintf.macaddr[24:16]
            elif curbyte == 18:
                data.next = txflowintf.macaddr[32:24]
            elif curbyte == 19:
                data.next = txflowintf.macaddr[40:32]
            elif curbyte == 20:
                data.next = txflowintf.macaddr[48:40]
            elif curbyte == 21:
                data.next = 0x88  # MAC control Frame
            elif curbyte == 22:
                data.next = 0x08
            elif curbyte == 23:
                data.next = 0x00  # Pause Opcode
            elif curbyte == 24:
                data.next = 0x01
            elif curbyte == 25:
                data.next = txflowintf.pauseval[16:8]
            elif curbyte == 26:
                data.next = txflowintf.pauseval[8:]
            else:
                state.next = txstate.PADDING

    return assign, pausecntrl, curbyteinc, transmitter, crc32inst
