from myhdl import Signal, intbv, block, enum, always_comb, always_seq, concat, ResetSignal
from .delayline import delayline
from .crc32 import crc32
from .addrfilter import addrfilter

rxstate = enum('IDLE', 'PREAMBLE', 'FILTER', 'PAUSE', 'PASS', 'GOODFRAME', 'BADFRAME')


@block
def rxengine(rxclientintf, rxgmii_intf, rxflowintf, rxconfig0, rxconfig1,
             filterconfig, addrtable, sysreset):

    """ Receiver Engine.

    Accepts Ethernet frame data from the GMII Block, removes the preamble field
    at the start of the frame, removes padding bytes and Frame Check Sequence.
    It performs BADFRAME detection on the received frame using information such
    as the frame check sequence field, received GMII BADFRAME codes, and legal
    frame size boundaries.

    """

    state = Signal(rxstate.IDLE)
    curbyte = Signal(intbv(1, min=0, max=10000))
    reset = ResetSignal(0, active=0, async=True)
    clearcrc = Signal(bool(0))
    calccrc = Signal(bool(0))
    matchcrc = Signal(bool(0))
    crcout = Signal(intbv(0xFFFFFFFF)[32:])
    crc32inst = crc32(rxgmii_intf.clk, clearcrc, calccrc, rxgmii_intf.data,
                      crcout, reset)

    dlinst = delayline(rxgmii_intf.clk, rxgmii_intf.data, rxclientintf.data,
                       True, reset, delay=6)

    gofilt = Signal(bool(0))
    isucast = Signal(bool(0))
    isucast1 = Signal(bool(0))
    isucast2 = Signal(bool(0))
    ismcast1 = Signal(bool(0))
    ismcast2 = Signal(bool(0))
    isbcast = Signal(bool(0))
    ispause = Signal(bool(0))

    afinst0 = addrfilter(rxgmii_intf.clk, rxgmii_intf.data, rxflowintf.macaddr,
                         gofilt, isucast, reset)
    afinst1 = addrfilter(rxgmii_intf.clk, rxgmii_intf.data, addrtable[0],
                         gofilt, isucast1, reset)
    afinst2 = addrfilter(rxgmii_intf.clk, rxgmii_intf.data, addrtable[1],
                         gofilt, isucast2, reset)
    afinst3 = addrfilter(rxgmii_intf.clk, rxgmii_intf.data, addrtable[0],
                         gofilt, ismcast1, reset)
    afinst4 = addrfilter(rxgmii_intf.clk, rxgmii_intf.data, addrtable[1],
                         gofilt, ismcast2, reset)
    afinst5 = addrfilter(rxgmii_intf.clk, rxgmii_intf.data, 0x111111111111,
                         gofilt, isbcast, reset)
    afinst6 = addrfilter(rxgmii_intf.clk, rxgmii_intf.data, 0x0180C2000001,
                         gofilt, ispause, reset)

    @always_comb
    def assign():
        rxclientintf.clk.next = rxgmii_intf.clk.next
        clearcrc.next = state == rxstate.IDLE
        calccrc.next = (state == rxstate.FILTER or state == rxstate.PAUSE or state == rxstate.PASS)
        rxflowintf.macaddr.next = concat(rxconfig1[16:], rxconfig0)
        matchcrc.next = crcout == 0x2144DF1C
        reseten = rxconfig1[31]
        reset.next = sysreset or not reseten

    @always_seq(rxgmii_intf.clk.posedge, reset)
    def curbyteinc():
        """ Index Incrementer """
        if state == rxstate.IDLE or state == rxstate.PREAMBLE:
            curbyte.next = 1
        else:
            curbyte.next = curbyte + 1

    @always_seq(rxgmii_intf.clk.posedge, reset)
    def receiver():
        """ Receiver Logic """
        cntrlchecken = rxconfig1[24]
        lenchecken = not rxconfig1[25]
        vlanen = rxconfig1[27]
        rxen = rxconfig1[28]
        fcsen = rxconfig1[29]
        jumboen = rxconfig1[30]

        if rxen:
            if rxgmii_intf.err:
                state.next = rxstate.BADFRAME

            elif state == rxstate.IDLE:
                rxclientintf.data.next = 0x00
                rxclientintf.dv.next = False
                rxclientintf.bad.next = False
                rxclientintf.good.next = False
                rxflowintf.pausereq.next = False
                rxflowintf.pauseval.next = 0x0000
                if rxgmii_intf.dv:
                    if rxgmii_intf.data == 0x55:
                        state.next = rxstate.PREAMBLE
                    else:
                        state.next = rxstate.BADFRAME

            elif state == rxstate.PREAMBLE:
                if not rxgmii_intf.dv:
                    state.next = rxstate.BADFRAME
                elif rxgmii_intf.data == 0xD5:
                    state.next = rxstate.FILTER
                    gofilt.next = True
                elif rxgmii_intf.data != 0x55:
                    state.next = rxstate.BADFRAME

            elif state == rxstate.FILTER:
                gofilt.next = False
                if curbyte == 6:
                    if isucast or isucast1 or isucast2 or ismcast1 or ismcast2 or isbcast\
                            or ispause or filterconfig[31]:
                        rxclientintf.dv = True
                        if ispause and rxflowintf.rxflowen:
                            state.next = rxstate.PAUSE
                        else:
                            state.next = rxstate.PASS
                    else:
                        state.next = rxstate.IDLE

            elif state == rxstate.PAUSE:
                len.next = 46
                if (curbyte == 13 and rxgmii_intf.data != 0x88) or \
                        (curbyte == 14 and rxgmii_intf.data != 0x08) or \
                        (curbyte == 15 and rxgmii_intf.data != 0x00) or \
                        (curbyte == 16 and rxgmii_intf.data != 0x01):
                    if not cntrlchecken:
                        state = rxstate.PASS
                    else:
                        state = rxstate.GOODFRAME
                elif curbyte == 17:
                    rxflowintf.pauseval.next = rxgmii_intf.data << 8
                elif curbyte == 18:
                    rxflowintf.pauseval.next = concat(rxflowintf.pauseval[16:8], rxgmii_intf.data)
                elif not rxgmii_intf.dv:
                    state.next = rxstate.BADFRAME
                    if matchcrc and (not lenchecken or curbyte == 65):
                        rxflowintf.pausereq.next = True

            elif state == rxstate.PASS:
                if curbyte == 13:
                    len.next = rxgmii_intf.data << 8
                elif curbyte == 14:
                    len.next = concat(len[16:8], rxgmii_intf.data)
                elif len < (46 - 4*vlanen):
                    if curbyte == (len + 14 + 4*vlanen):
                        if not fcsen:
                            rxclientintf.dv.next = False
                        len.next = 46 - 4*vlanen
                elif not rxgmii_intf.dv:
                    if matchcrc and (not lenchecken or curbyte == (len + 14 + 4*vlanen + 4 + 1)):
                        state.next = rxstate.GOODFRAME
                    else:
                        state.next = rxstate.BADFRAME

            elif state == rxstate.GOODFRAME:
                if not fcsen and curbyte == (len + 14 + 4*vlanen + 6) or \
                        fcsen and curbyte == (len + 14 + 4*vlanen + 4 + 6):
                    rxclientintf.dv.next = False
                    rxclientintf.good = True
                    state.next = rxstate.IDLE

            elif state == rxstate.BADFRAME:
                rxclientintf.dv.next = False
                rxclientintf.bad.next = True
                state.next = rxstate.IDLE

    return assign, curbyteinc, receiver, crc32inst, dlinst, afinst1,\
        afinst2, afinst3, afinst4, afinst5, afinst6, afinst0
