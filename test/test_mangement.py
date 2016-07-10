from gemac.interfaces import HostManagementInterface, MDIOInterface
from gemac.management import management
from myhdl import instance, delay, block, intbv, now, StopSimulation, \
    ResetSignal, Signal
from myhdl.conversion import verify
import pytest


def clkwait(clk, count=1):
    while count:
        yield clk.posedge
        count -= 1


@pytest.fixture()
def setuptb():
    hostintf = HostManagementInterface()
    mdiointf = MDIOInterface()
    configregs = [Signal(intbv(0)[32:]) for _ in range(10)]
    addrtable = [Signal(intbv(0)[48:]) for _ in range(4)]
    reset = ResetSignal(1, active=0, async=True)

    @block
    def testbench():
        dutinst = management(hostintf, mdiointf, configregs, addrtable, reset)

        @instance
        def hostclkdriver():
            while True:
                hostintf.clk.next = \
                    not hostintf.clk
                yield delay(5)

        @instance
        def resetonstart():
            reset.next = 0
            yield clkwait(hostintf.clk, count=2)
            reset.next = 1
            yield clkwait(hostintf.clk, count=2)

        return dutinst, hostclkdriver, resetonstart

    return testbench, hostintf, mdiointf


def test_rwconfig(setuptb):
    tb, hostintf, mdiointf = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing Read/Write Configuration Register%s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(hostintf.clk, count=10)
            yield hostintf.writeconfig(0x239, 0x12345678)
            yield clkwait(hostintf.clk, count=4)
            yield hostintf.readconfig(0x239)
            assert hostintf.rddata[32:] == intbv(0x12345678)

        return tbstim, tbinst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=300)
    testInst.quit_sim()


def test_rwaddrtable(setuptb):
    tb, hostintf, mdiointf = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing Read/Write Address Table%s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(hostintf.clk, count=10)
            yield hostintf.writeaddrtable(1, 0xAA22BB55FF22)
            yield clkwait(hostintf.clk, count=4)
            yield hostintf.readaddrtable(1)
            readaddr = hostintf.rddata[32:]
            yield hostintf.clk.posedge
            readaddr = readaddr | (hostintf.rddata[16:] << 32)
            assert readaddr == 0xAA22BB55FF22

        return tbstim, tbinst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=500)
    testInst.quit_sim()


def test_mdioclkgen(setuptb):
    tb, hostintf, mdiointf = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing MDIO Clk Generator %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(hostintf.clk, count=20)
            yield hostintf.writeconfig(0x340, 0x00000002)
            yield mdiointf.mdc.posedge
            time_mdc = now()
            yield mdiointf.mdc.posedge
            time_mdc = now() - time_mdc
            yield hostintf.clk.posedge
            time_hostclk = now()
            yield hostintf.clk.posedge
            time_hostclk = now() - time_hostclk
            assert time_hostclk == time_mdc / 6

        return tbstim, tbinst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=300)
    testInst.quit_sim()


def test_mdiowrite(setuptb):
    tb, hostintf, mdiointf = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing MDIO Write Operation %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(hostintf.clk, count=10)
            # mdio enable, clkdiv =2+1*2=6
            yield hostintf.writeconfig(0x340, 0x00000022)
            yield mdiointf.mdc.posedge
            yield hostintf.mdiowriteop(intbv(0b01), intbv(0b1001100000),
                                       intbv(0xABCD), block=False)
            yield mdiointf.out.negedge
            wrindex = 32
            wrdata = intbv(0)[32:]
            while wrindex >= 0:
                wrdata[wrindex] = mdiointf.out
                wrindex -= 1
                yield mdiointf.mdc.posedge
            assert wrdata[32:] == 0x5982ABCD

        return tbstim, tbinst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=6000)
    testInst.quit_sim()


def test_mdioread(setuptb):
    tb, hostintf, mdiointf = setuptb

    @block
    def test():
        tbinst = tb()
        print("Testing MDIO Write Operation %s" % tbinst)

        @instance
        def tbstim():
            yield clkwait(hostintf.clk, count=10)
            # mdio enable, clkdiv =2+1*2=6
            yield hostintf.writeconfig(0x340, 0x00000022)
            yield mdiointf.mdc.posedge
            yield hostintf.mdioreadop(intbv(0b10), intbv(0b1001100000),
                                      block=False)
            yield mdiointf.out.negedge
            wrindex = 32
            wrdata = intbv(0)[32:]
            while wrindex >= 18:
                wrdata[wrindex] = mdiointf.out
                wrindex -= 1
                yield mdiointf.mdc.posedge
            assert wrdata[32:18] == 0x1A60
            mdiointf.inn.next = 0
            rdindex = 15
            while rdindex >= 0:
                yield mdiointf.mdc.posedge
                mdiointf.inn.next = not mdiointf.inn
                rdindex -= 1
            yield hostintf.miimrdy.posedge
            assert hostintf.rddata[16:] == 0x5555

        return tbstim, tbinst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=6000)
    testInst.quit_sim()


def test_convertible():

    @block
    def test():
        hostintf = HostManagementInterface()
        mdiointf = MDIOInterface()
        configregs = [Signal(intbv(0)[32:]) for _ in range(10)]
        addrtable = [Signal(intbv(0)[48:]) for _ in range(4)]
        reset = ResetSignal(1, active=0, async=True)
        dutInst = management(hostintf, mdiointf, configregs, addrtable, reset)
        print("Testing Convertibility %s" % dutInst)

        @instance
        def hostclkdriver():
            hostintf.clk.next = 0
            while True:
                yield delay(5)
                hostintf.clk.next = not hostintf.clk

        @instance
        def testlogic():
            reset.next = 0
            yield delay(15)
            reset.next = 1
            yield delay(20)
            print("Converted! %d" % now())
            raise StopSimulation

        return dutInst, testlogic, hostclkdriver

    testInst = test()
    verify.simulator = 'iverilog'
    assert testInst.verify_convert() == 0
