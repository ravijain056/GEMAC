from gemac.interfaces import HostManagementInterface, MDIOInterface
from gemac.management import management
from myhdl import instance, delay, block, intbv, now, StopSimulation, \
    ResetSignal
from myhdl.conversion import verify


def test_rwconfig():

    @block
    def test():

        hostintf = HostManagementInterface()
        mdiointf = MDIOInterface()
        reset = ResetSignal(1, active=0, async=True)
        dutInst = management(hostintf, mdiointf, reset)
        print("Testing Read/Write Configuration Register%s" % dutInst)

        @instance
        def hostclkdriver():
            while True:
                hostintf.clk.next = \
                    not hostintf.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostintf.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)
            yield hostintf.writeconfig(0x239, 0x12345678)
            yield clkwait(count=4)
            yield hostintf.readconfig(0x239)
            assert hostintf.rddata[32:] == intbv(0x12345678)

        return testlogic, hostclkdriver, dutInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=300)
    testInst.quit_sim()


def test_rwaddrtable():

    @block
    def test():
        hostintf = HostManagementInterface()
        mdiointf = MDIOInterface()
        reset = ResetSignal(1, active=0, async=True)
        dutInst = management(hostintf, mdiointf, reset)
        print("Testing Read/Write Address Table%s" % dutInst)

        @instance
        def hostclkdriver():
            while True:
                hostintf.clk.next = not hostintf.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostintf.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)
            yield hostintf.writeaddrtable(1, 0xAA22BB55FF22)
            yield clkwait(count=4)
            yield hostintf.readaddrtable(1)
            readaddr = hostintf.rddata[32:]
            yield hostintf.clk.posedge
            readaddr = readaddr | (hostintf.rddata[16:] << 32)
            assert readaddr == 0xAA22BB55FF22

        return testlogic, hostclkdriver, dutInst

    testInst = test()
    testInst.config_sim(trace=True)
    testInst.run_sim(duration=500)
    testInst.quit_sim()


def test_mdioclkgen():

    @block
    def test():
        hostintf = HostManagementInterface()
        mdiointf = MDIOInterface()
        reset = ResetSignal(1, active=0, async=True)
        dutInst = management(hostintf, mdiointf, reset)
        print("Testing MDIO Clk Generator %s" % dutInst)

        @instance
        def hostclkdriver():
            while True:
                hostintf.clk.next = \
                    not hostintf.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostintf.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=20)
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

        return testlogic, hostclkdriver, dutInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=300)
    testInst.quit_sim()


def test_mdiowrite():

    @block
    def test():

        hostintf = HostManagementInterface()
        mdiointf = MDIOInterface()
        reset = ResetSignal(1, active=0, async=True)
        dutInst = management(hostintf, mdiointf, reset)
        print("Testing MDIO Write Operation %s" % dutInst)

        @instance
        def hostclkdriver():
            while True:
                hostintf.clk.next = \
                    not hostintf.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostintf.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)  # mdio enable, clkdiv =2+1*2=6
            yield hostintf.writeconfig(0x340, 0x00000022)
            yield mdiointf.mdc.posedge
            yield hostintf.\
                mdiowriteop(intbv(0b01), intbv(0b1001100000),
                            intbv(0xABCD), block=False)
            yield mdiointf.out.negedge
            wrindex = 32
            wrdata = intbv(0)[32:]
            while wrindex >= 0:
                wrdata[wrindex] = mdiointf.out
                wrindex -= 1
                yield mdiointf.mdc.posedge
            assert wrdata[32:] == 0x5982ABCD

        return testlogic, hostclkdriver, dutInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=6000)
    testInst.quit_sim()


def test_mdioread():

    @block
    def test():

        hostintf = HostManagementInterface()
        mdiointf = MDIOInterface()
        reset = ResetSignal(1, active=0, async=True)
        dutInst = management(hostintf, mdiointf, reset)
        print("Testing MDIO Write Operation %s" % dutInst)

        @instance
        def hostclkdriver():
            while True:
                hostintf.clk.next = \
                    not hostintf.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostintf.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)  # mdio enable, clkdiv =2+1*2=6
            yield hostintf.writeconfig(0x340, 0x00000022)
            yield mdiointf.mdc.posedge
            yield hostintf.\
                mdioreadop(intbv(0b10), intbv(0b1001100000), block=False)
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

        return testlogic, hostclkdriver, dutInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=6000)
    testInst.quit_sim()


def test_convertible():

    @block
    def test():
        hostintf = HostManagementInterface()
        mdiointf = MDIOInterface()
        reset = ResetSignal(1, active=0, async=True)
        dutInst = management(hostintf, mdiointf, reset)
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
