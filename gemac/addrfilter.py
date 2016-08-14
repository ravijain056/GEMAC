from myhdl import Signal, intbv, block, always_seq
from myhdl._always_comb import always_comb


@block
def addrfilter(clk, rxdata, addr, go, match, reset):

    curbyte = Signal(intbv(0, min=0, max=8))

    @always_comb
    def assign():
        match.next = curbyte == 6

    @always_seq(clk.posedge, reset)
    def filterlogic():
        if go and rxdata == addr[48:40]:
            curbyte.next = 1
        elif curbyte == 1 and rxdata == addr[40:32]:
            curbyte.next = 2
        elif curbyte == 2 and rxdata == addr[32:24]:
            curbyte.next = 3
        elif curbyte == 3 and rxdata == addr[24:16]:
            curbyte.next = 4
        elif curbyte == 4 and rxdata == addr[16:8]:
            curbyte.next = 5
        elif curbyte == 5 and rxdata == addr[8:]:
            curbyte.next = 6
        elif not curbyte == 6:
            curbyte.next = 7

    return filterlogic, assign
