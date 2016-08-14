from myhdl import block, always_seq, Signal, intbv


@block
def delayline(clk, din, dout, en, reset, delay=6):

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
