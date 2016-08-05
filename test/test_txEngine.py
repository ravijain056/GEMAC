from myhdl import block, instance, delay, ResetSignal, Signal, intbv,\
    StopSimulation, now
from myhdl.conversion import verify
from gemac.intrafaces import TxGMII_Interface, TxFlowInterface
from gemac.txEngine import txengine
from gemac.interfaces import TxFIFOClientInterface
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
    txclientintf = TxFIFOClientInterface()
    txgmii_intf = TxGMII_Interface()
    txflowintf = TxFlowInterface()
    txconfig = Signal(intbv(0)[32:])
    reset = ResetSignal(1, active=0, async=True)

    @block
    def testbench():
        dutinst = txengine(txclientintf, txgmii_intf, txflowintf,
                           txconfig, reset)

        @instance
        def hostclkdriver():
            while True:
                txclientintf.clk.next = \
                    not txclientintf.clk
                yield delay(5)

        @instance
        def resetonstart():
            reset.next = 0
            yield clkwait(txclientintf.clk, count=2)
            reset.next = 1
            yield clkwait(txclientintf.clk, count=2)

        return dutinst, hostclkdriver, resetonstart

    return testbench, txclientintf, txgmii_intf, txflowintf, txconfig


def test_inbandfcs(setuptb):
    tb, txclientintf, txgmii_intf, txflowintf, txconfig = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing Inter-FrameGap Delay %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(txclientintf.clk, count=10)
            txconfig.next = 0x30000000
            yield clkwait(txclientintf.clk, count=2)
            yield txclientintf.tx(datastream)

        @instance
        def tbcheck():
            yield clkwait(txclientintf.clk, count=10)
            yield txclientintf.ack.posedge
            yield clkwait(txclientintf.clk, count=2)
            for i in range(len(datastream)):
                yield txclientintf.clk.posedge
                assert txgmii_intf.data == datastream[i]

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=2000)
    testInst.quit_sim()


def test_crc32(setuptb):
    tb, txclientintf, txgmii_intf, txflowintf, txconfig = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing CRC-32 Calculation %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(txclientintf.clk, count=10)
            txconfig.next = 0x10000000
            yield clkwait(txclientintf.clk, count=2)
            yield txclientintf.tx(datastream)
            yield txclientintf.clk.posedge
            crc32 = 0
            for i in range(3, -1, -1):
                yield txclientintf.clk.posedge
                crc32 = (txgmii_intf.data << (i * 8)) | crc32
            assert crc32 == 0x28A1C270

        return tbinst, tbstim

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=2000)
    testInst.quit_sim()


def test_preamble(setuptb):
    tb, txclientintf, txgmii_intf, txflowintf, txconfig = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing Preamble Addition %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(txclientintf.clk, count=10)
            txconfig.next = 0x10000000
            yield clkwait(txclientintf.clk, count=2)
            yield txclientintf.tx(datastream)
            yield clkwait(txclientintf.clk, count=120)

        @instance
        def tbcheck():
            yield clkwait(txclientintf.clk, count=16)
            for _ in range(7):
                assert txgmii_intf.data == 0x55
                yield txclientintf.clk.posedge
            assert txgmii_intf.data == 0xD5

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=2000)
    testInst.quit_sim()


def test_ifgdelay(setuptb):
    tb, txclientintf, txgmii_intf, txflowintf, txconfig = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing Transmit Normal %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(txclientintf.clk, count=10)
            txconfig.next = 0x32000000
            txclientintf.ifgdelay.next = 20
            yield clkwait(txclientintf.clk, count=2)
            yield txclientintf.tx(datastream)
            yield txclientintf.tx(datastream)

        @instance
        def tbcheck():
            yield clkwait(txclientintf.clk, count=14)
            yield txclientintf.dv.negedge
            count = 0
            while not txclientintf.data == 0xAA:
                count += 1
                yield txclientintf.clk.posedge
            assert count == 20

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=3000)
    testInst.quit_sim()


def test_padding(setuptb):
    tb, txclientintf, txgmii_intf, txflowintf, txconfig = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing padding %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(txclientintf.clk, count=10)
            txconfig.next = 0x10000000
            yield clkwait(txclientintf.clk, count=2)
            yield txclientintf.tx(datastream[:20])

        @instance
        def tbcheck():
            yield clkwait(txclientintf.clk, count=14)
            yield txclientintf.dv.negedge
            yield clkwait(txclientintf.clk, count=2)
            count = 0
            while txgmii_intf.dv:
                yield txclientintf.clk.posedge
                count += 1
            assert count + 20 == 64

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=2000)
    testInst.quit_sim()


def test_maxframesize(setuptb):
    tb, txclientintf, txgmii_intf, txflowintf, txconfig = setuptb
    datastream = [randrange(256) for _ in range(1600)]

    @block
    def test():
        tbinst = tb()
        print("Testing Max Permitted Length Restriction %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(txclientintf.clk, count=10)
            txconfig.next = 0x10000000
            yield clkwait(txclientintf.clk, count=2)
            yield txclientintf.tx(datastream)

        @instance
        def tbcheck():
            yield clkwait(txclientintf.clk, count=10)
            yield txgmii_intf.dv.posedge
            erred = False
            while(txgmii_intf.dv):
                yield txclientintf.clk.posedge
                if (txgmii_intf.err):
                    erred = True
            assert erred

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=20000)
    testInst.quit_sim()


def test_jumboframe(setuptb):
    tb, txclientintf, txgmii_intf, txflowintf, txconfig = setuptb
    datastream = [randrange(256) for _ in range(1700)]

    @block
    def test():
        tbinst = tb()
        print("Testing Jumbo Frames %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(txclientintf.clk, count=10)
            txconfig.next = 0x50000000
            yield clkwait(txclientintf.clk, count=2)
            yield txclientintf.tx(datastream)

        @instance
        def tbcheck():
            yield clkwait(txclientintf.clk, count=20)
            yield txgmii_intf.dv.negedge
            assert not txgmii_intf.err

        return tbinst, tbstim, tbcheck

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=20000)
    testInst.quit_sim()


def test_convertible():

    @block
    def test():
        txclientintf = TxFIFOClientInterface()
        txgmii_intf = TxGMII_Interface()
        txflowintf = TxFlowInterface()
        txconfig = Signal(intbv(0)[32:])
        reset = ResetSignal(1, active=0, async=True)
        dutinst = txengine(txclientintf, txgmii_intf, txflowintf,
                           txconfig, reset)
        print("Testing Convertibility %s" % dutinst)

        @instance
        def hostclkdriver():
            txclientintf.clk.next = 0
            while True:
                yield delay(5)
                txclientintf.clk.next = not txclientintf.clk

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
