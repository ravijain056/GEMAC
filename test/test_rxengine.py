from myhdl import block, instance, delay, ResetSignal, Signal, intbv,\
    StopSimulation, now
from myhdl.conversion import verify
from gemac.intrafaces import RxGMII_Interface, RxFlowInterface
from gemac.rxEngine import rxengine
from gemac.interfaces import RxFIFOClientInterface
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
destaddr = [0xAB, 0xCD, 0x12, 0x34, 0x56, 0xEF]
srcaddr = [0x45, 0x6E, 0xFA, 0xBC, 0xD1, 0x23]
length = intbv(len(datastream))
crc = [0x70, 0xC2, 0xA1, 0x28]
pre = 0x55
sfd = 0xD5


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
                rxgmii_intf.clk.next = not rxgmii_intf.clk
                yield delay(5)

        @instance
        def resetonstart():
            reset.next = 0
            yield clkwait(rxgmii_intf.clk, count=2)
            reset.next = 1
            yield clkwait(rxgmii_intf.clk, count=2)

        return dutinst, hostclkdriver, resetonstart

    return testbench, rxclientintf, rxgmii_intf, rxflowintf, rxconfig0, rxconfig1, filterconfig, addrtable


def test_normalreceive(setuptb):
    tb, rxclientintf, rxgmii_intf, rxflowintf, rxconfig0, rxconfig1, filterconfig, addrtable = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing Normal Receive Operation %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(rxgmii_intf.clk, count=10)
            rxconfig1.next = 0x10000000
            filterconfig.next = 0x80000000
            rxgmii_intf.data.next = pre
            rxgmii_intf.dv.next = True
            yield clkwait(rxgmii_intf.clk, count=7)
            rxgmii_intf.data.next = sfd
            yield rxgmii_intf.clk.posedge
            for d in destaddr:
                rxgmii_intf.data.next = d
                yield rxgmii_intf.clk.posedge
            for d in srcaddr:
                rxgmii_intf.data.next = d
                yield rxgmii_intf.clk.posedge
            rxgmii_intf.data.next = length[16:8]
            yield rxgmii_intf.clk.posedge
            rxgmii_intf.data.next = length[8:]
            yield rxgmii_intf.clk.posedge
            for d in datastream:
                rxgmii_intf.data.next = d
                yield rxgmii_intf.clk.posedge
            for d in crc:
                rxgmii_intf.data.next = d
                yield rxgmii_intf.clk.posedge
            rxgmii_intf.data.next = 0x00
            rxgmii_intf.dv.next = False

        @instance
        def tbcheck():
            global runcheck
            runcheck = False
            yield clkwait(rxgmii_intf.clk, count=10)
            yield rxclientintf.dv.posedge
            yield rxgmii_intf.clk.posedge
            for d in destaddr:
                assert rxclientintf.data == d
                yield rxgmii_intf.clk.posedge
            for d in srcaddr:
                assert rxclientintf.data == d
                yield rxgmii_intf.clk.posedge
            assert rxclientintf.data == length[16:8]
            yield rxgmii_intf.clk.posedge
            assert rxclientintf.data == length[8:]
            yield rxgmii_intf.clk.posedge
            for d in datastream:
                assert rxclientintf.data == d
                yield rxgmii_intf.clk.posedge
            assert not rxclientintf.dv
            while not rxclientintf.bad:  # Wrong CRC
                yield rxgmii_intf.clk.posedge
            runcheck = True

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=5000)
    testInst.quit_sim()
    assert runcheck


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
            rxgmii_intf.clk.next = 0
            while True:
                yield delay(5)
                rxgmii_intf.clk.next = not rxgmii_intf.clk

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
