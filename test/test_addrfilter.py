from myhdl import block, instance, delay, ResetSignal, Signal, intbv,\
    StopSimulation, now
from myhdl.conversion import verify
from gemac.addrfilter import addrfilter
import pytest


def clkwait(clk, count=1):
    while count:
        yield clk.posedge
        count -= 1


@pytest.fixture()
def setuptb():
    clk = Signal(bool(0))
    rxdata = Signal(intbv(0)[8:])
    addr = Signal(intbv(0xABCD1234EF56))
    go = Signal(bool(0))
    match = Signal(bool(0))
    reset = ResetSignal(1, active=0, async=True)

    @block
    def testbench():
        dutinst = addrfilter(clk, rxdata, addr, go, match, reset)

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

    return testbench, clk, rxdata, addr, go, match


def test_match(setuptb):
    tb, clk, rxdata, addr, go, match = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing Address Filter %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(clk, count=10)
            go.next = True
            rxdata.next = addr[48:40]
            yield clk.posedge
            rxdata.next = addr[40:32]
            yield clk.posedge
            rxdata.next = addr[32:24]
            yield clk.posedge
            rxdata.next = addr[24:16]
            yield clk.posedge
            rxdata.next = addr[16:8]
            yield clk.posedge
            rxdata.next = addr[8:]
            yield clkwait(clk, count=2)
            assert match

        return tbinst, tbstim

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=200)
    testInst.quit_sim()


def test_convertible():

    @block
    def test():
        clk = Signal(bool(0))
        rxdata = Signal(intbv(0)[8:])
        addr = Signal(intbv(0)[48:])
        go = Signal(bool(0))
        match = Signal(bool(0))
        reset = ResetSignal(1, active=0, async=True)
        dutinst = addrfilter(clk, rxdata, addr, go, match, reset)
        print("Testing Convertibility %s" % dutinst)

        @instance
        def hostclkdriver():
            clk.next = 0
            while True:
                yield delay(5)
                clk.next = not clk

        @instance
        def testlogic():
            reset.next = 0
            yield delay(15)
            reset.next = 1
            yield delay(20)
            print("Converted! %d" % now())
            raise StopSimulation

        return dutinst, testlogic, hostclkdriver

    testInst = test()
    verify.simulator = 'iverilog'
    assert testInst.verify_convert() == 0

