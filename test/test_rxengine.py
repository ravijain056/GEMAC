from myhdl import block, instance, delay, ResetSignal, Signal, intbv,\
    StopSimulation, now
from myhdl.conversion import verify
from gemac.intrafaces import RxGMII_Interface, RxFlowInterface
from gemac.rxEngine import rxengine
from gemac.interfaces import RxFIFOClientInterface
from random import randrange
import pytest


datastream = [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
              0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0]


def clkwait(clk, count=1):
    while count:
        yield clk.posedge
        count -= 1


@pytest.fixture()
def setuptb():
    rxclientintf = RxFIFOClientInterface()
    rxgmii_intf = RxGMII_Interface()
    rxflowintf = RxFlowInterface()
    rxconfig0 = Signal(intbv(0)[32:])
    rxconfig1 = Signal(intbv(0)[32:])
    filterconfig = Signal(intbv(0)[32:])
    addrtable = [Signal(intbv(0)[48:]) for _ in range(4)]
    reset = ResetSignal(1, active=0, async=True)

    @block
    def testbench():
        dutinst = rxengine(rxclientintf, rxgmii_intf, rxflowintf, rxconfig0, rxconfig1, filterconfig, addrtable, reset)

        @instance
        def hostclkdriver():
            while True:
                rxclientintf.clk.next = not rxclientintf.clk
                yield delay(5)

        @instance
        def resetonstart():
            reset.next = 0
            yield clkwait(rxclientintf.clk, count=2)
            reset.next = 1
            yield clkwait(rxclientintf.clk, count=2)

        return dutinst, hostclkdriver, resetonstart

    return testbench, rxclientintf, rxgmii_intf, rxflowintf, rxconfig0, rxconfig1, filterconfig, addrtable


def test_convertible():

    @block
    def test():
        rxclientintf = RxFIFOClientInterface()
        rxgmii_intf = RxGMII_Interface()
        rxflowintf = RxFlowInterface()
        rxconfig0 = Signal(intbv(0)[32:])
        rxconfig1 = Signal(intbv(0)[32:])
        filterconfig = Signal(intbv(0)[32:])
        addrtable = [Signal(intbv(0)[48:]) for _ in range(4)]
        reset = ResetSignal(1, active=0, async=True)
        dutinst = rxengine(rxclientintf, rxgmii_intf, rxflowintf, rxconfig0, rxconfig1, filterconfig, addrtable, reset)
        print("Testing Convertibility %s" % dutinst)

        @instance
        def hostclkdriver():
            rxclientintf.clk.next = 0
            while True:
                yield delay(5)
                rxclientintf.clk.next = not rxclientintf.clk

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
