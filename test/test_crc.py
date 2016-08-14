from myhdl import block, instance, delay, ResetSignal, Signal, intbv, \
    StopSimulation, now
from myhdl.conversion import verify
from gemac.crc32 import crc32
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
    clk = Signal(bool(0))
    clear = Signal(bool(0))
    calc = Signal(bool(0))
    data = Signal(intbv(0)[8:])
    crcout = Signal(intbv(0)[32:])
    reset = ResetSignal(1, active=0, async=True)

    @block
    def testbench():
        dutinst = crc32(clk, clear, calc, data, crcout, reset)

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

    return testbench, clk, clear, calc, data, crcout


def test_crc32(setuptb):
    tb, clk, clear, calc, data, crcout = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing CRC-32 Calculation %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(clk, count=10)
            clear.next = True
            yield clk.posedge
            clear.next = False
            yield clk.posedge
            assert crcout == 0x00000000
            calc.next = True
            for d in datastream:
                data.next = d
                yield clk.posedge
            data.next = 0x70
            yield clk.posedge
            assert crcout == 0x28A1C270
            data.next = 0xC2
            yield clk.posedge
            data.next = 0xA1
            yield clk.posedge
            data.next = 0x28
            yield clk.posedge
            calc.next = False
            yield clk.posedge
            assert crcout == 0x2144DF1C

        return tbinst, tbstim

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=2000)
    testInst.quit_sim()


def test_matchcrc32(setuptb):
    tb, clk, clear, calc, data, crcout = setuptb
    datastream = [randrange(256) for _ in range(100)]

    @block
    def test():
        tbinst = tb()
        print("Testing CRC-32 Receiver Matching %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(clk, count=10)
            clear.next = True
            yield clk.posedge
            clear.next = False
            yield clk.posedge
            assert crcout == 0x00000000
            for d in datastream:
                yield clk.posedge
                calc.next = True
                data.next = d
            yield clk.posedge
            calc.next = False
            yield clk.posedge
            calc.next = True
            a = Signal(crcout)
            data.next = a[8:]
            yield clk.posedge
            data.next = a[16:8]
            yield clk.posedge
            data.next = a[24:16]
            yield clk.posedge
            data.next = a[32:24]
            yield clk.posedge
            calc.next = False
            yield clk.posedge
            assert crcout == 0x2144DF1C

        return tbinst, tbstim

    testInst = test()
    testInst.config_sim(trace=True)
    testInst.run_sim(duration=2000)
    testInst.quit_sim()
