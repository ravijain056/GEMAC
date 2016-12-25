from myhdl import block, Signal, intbv, ResetSignal, instance, delay
from gemac.delayline import delayline
from random import randrange
import pytest


def clkwait(clk, count=1):
    while count:
        yield clk.posedge
        count -= 1


@pytest.fixture()
def setuptb():
    clk = Signal(bool(0))
    din = Signal(intbv(0)[8:])
    dout = Signal(intbv(0)[8:])
    en = Signal(bool(0))
    reset = ResetSignal(1, active=0, async=True)

    @block
    def testbench():
        dutinst = delayline(clk, din, dout, en, reset)

        @instance
        def hostclkdriver():
            while True:
                clk.next = not clk
                yield delay(5)

        @instance
        def resetonstart():
            reset.next = 0
            yield clkwait(clk, count=2)
            reset.next = 1
            yield clkwait(clk, count=2)

        return dutinst, hostclkdriver, resetonstart

    return testbench, clk, din, dout, en, reset


def test_delayline(setuptb):
    tb, clk, din, dout, en, reset = setuptb
    dstream = [randrange(256) for _ in range(10)]

    @block
    def test():
        tbinst = tb()

        @instance
        def tbstim():
            yield clkwait(clk, count=10)
            en.next = True
            for data in dstream:
                din.next = data
                yield clk.posedge

        @instance
        def tbcheck():
            yield clkwait(clk, count=17)
            for data in dstream:
                assert dout == data
                yield clk.posedge

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=500)
    testInst.quit_sim()


def test_resetdelayline(setuptb):
    tb, clk, din, dout, en, reset = setuptb
    dstream = [randrange(256) for _ in range(6)]

    @block
    def test():
        tbinst = tb()

        @instance
        def tbstim():
            yield clkwait(clk, count=10)
            en.next = True
            for data in dstream:
                din.next = data
                yield clk.posedge
            yield clk.posedge
            reset.next = False
            yield clk.posedge
            reset.next = True
            for data in dstream:
                din.next = data
                yield clk.posedge

        @instance
        def tbcheck():
            yield clkwait(clk, count=17)
            assert dout == dstream[0]
            yield clkwait(clk, count=8)
            for data in dstream:
                assert dout == data
                yield clk.posedge

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=500)
    testInst.quit_sim()
