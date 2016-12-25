from myhdl import block, always_seq, Signal, intbv, always_comb, enum

flowstate = enum('IDLE', 'PAUSED')


@block
def flowcontrol(flowintf, txflowintf, rxflowintf, flowconfig, reset):

    """
    *Flow Control*

    """
    pausereq = Signal(bool(0))
    pausetime = Signal(intbv(0)[16:])
    curtime = Signal(intbv(0)[16:])
    index = Signal(intbv(0, min=0, max=64))
    state = Signal(flowstate.IDLE)

    @always_comb
    def assign():
        rxflowintf.rxflowen.next = flowconfig[29]

    @always_seq(txflowintf.clk.posedge, reset)
    def samplepauseval():
        txflowen = flowconfig[30]
        if flowintf.pausereq and txflowen:
            txflowintf.pausereq.next = True
            txflowintf.pauseval.next = flowintf.pauseval
            txflowintf.macaddr.next = rxflowintf.macaddr
        else:
            txflowintf.pausereq.next = False

    @always_seq(rxflowintf.clk.posedge, reset)
    def pauseapplyreq():
        if rxflowintf.pausereq:
            pausereq.next = True
            pausetime.next = rxflowintf.pauseval
        if state == flowstate.PAUSED:
            pausereq.next = False

    @always_seq(txflowintf.clk.posedge, reset)
    def applypause():
        if state == flowstate.IDLE:
            if pausereq:
                txflowintf.pauseapply = True
                state.next = flowstate.PAUSED
                curtime.next = 0
                index.next = 0

        elif state == flowstate.PAUSED:
            if(curtime < pausetime):
                if index == 63:
                    index.next = 0
                    curtime.next = curtime + 1
                else:
                    index.next = index + 1
            elif curtime == pausetime:
                txflowintf.pauseapply = False
                state.next = flowstate.IDLE

    return assign, samplepauseval, pauseapplyreq, applypause
