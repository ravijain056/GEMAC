from myhdl import block, always_seq, Signal, intbv


@block
def delayline(clk, din, dout, en, reset, delay=6):
    """ Delay line.

    Outputs the data on din on dout after 'delay' clock cycles when it is enabled,
    otherwise outputs Zero.

    Args:
        clk (1-bit Signal) - System Clock
        din (8-bits Signal) - Input DataBus
        dout (8-bits Signal) - Output DataBus
        en (1-bit Signal) - Enable Flag for signaling to take the input.
        reset (RsetSignal) - System reset
        delay (Default=6) - No. of Clock Cycles after which the input should occur on output bus.
    """

    line = [Signal(intbv(0, min=din.min, max=din.max)) for _ in range(delay-1)]

    @always_seq(clk.posedge, reset)
    def delaylogic():
        if en:
            line[0].next = din
        else:
            line[0].next = 0
        for i in range(delay-2):
            line[i+1].next = line[i]
        dout.next = line[delay-2]

    return delaylogic
