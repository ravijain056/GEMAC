from gemac.interfaces import HostManagementInterface, MDIOInterface
from gemac.management import management
from myhdl import instance, delay, block, intbv, now


def test_rwconfig():

    @block
    def test():

        hostmanagement_interface = HostManagementInterface()
        mdio_interface = MDIOInterface()
        managementInst = management(hostmanagement_interface, mdio_interface)
        print("Testing Read/Write Configuration Register%s" % managementInst)

        @instance
        def hostclkdriver():
            while True:
                hostmanagement_interface.clk.next = \
                    not hostmanagement_interface.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostmanagement_interface.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)
            yield hostmanagement_interface.writeconfig(0x239, 0x12345678)
            yield clkwait(count=4)
            yield hostmanagement_interface.readconfig(0x239)
            assert hostmanagement_interface.rddata[32:] == intbv(0x12345678)

        return testlogic, hostclkdriver, managementInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=300)
    testInst.quit_sim()


def test_rwaddrtable():

    @block
    def test():
        hostmanagement_interface = HostManagementInterface()
        mdio_interface = MDIOInterface()
        managementInst = management(hostmanagement_interface, mdio_interface)
        print("Testing Read/Write Address Table%s" % managementInst)

        @instance
        def hostclkdriver():
            while True:
                hostmanagement_interface.clk.next = \
                    not hostmanagement_interface.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostmanagement_interface.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)
            yield hostmanagement_interface.writeaddrtable(1, 0xAA22BB55FF22)
            yield clkwait(count=4)
            yield hostmanagement_interface.readaddrtable(1)
            readaddr = hostmanagement_interface.rddata[32:]
            yield hostmanagement_interface.clk.posedge
            readaddr = readaddr | (hostmanagement_interface.rddata[16:] << 32)
            assert readaddr == 0xAA22BB55FF22

        return testlogic, hostclkdriver, managementInst

    testInst = test()
    testInst.config_sim(trace=True)
    testInst.run_sim(duration=500)
    testInst.quit_sim()


def test_mdioclkgen():

    @block
    def test():
        hostmanagement_interface = HostManagementInterface()
        mdio_interface = MDIOInterface()
        managementInst = management(hostmanagement_interface, mdio_interface)
        print("Testing MDIO Clk Generator %s" % managementInst)

        @instance
        def hostclkdriver():
            while True:
                hostmanagement_interface.clk.next = \
                    not hostmanagement_interface.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostmanagement_interface.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=20)
            yield hostmanagement_interface.writeconfig(0x340, 0x00000002)
            yield mdio_interface.mdc.posedge
            time_mdc = now()
            yield mdio_interface.mdc.posedge
            time_mdc = now() - time_mdc
            yield hostmanagement_interface.clk.posedge
            time_hostclk = now()
            yield hostmanagement_interface.clk.posedge
            time_hostclk = now() - time_hostclk
            assert time_hostclk == time_mdc / 6

        return testlogic, hostclkdriver, managementInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=300)
    testInst.quit_sim()


def test_mdiowrite():

    @block
    def test():

        hostmanagement_interface = HostManagementInterface()
        mdio_interface = MDIOInterface()
        managementInst = management(hostmanagement_interface, mdio_interface)
        print("Testing MDIO Write Operation %s" % managementInst)

        @instance
        def hostclkdriver():
            while True:
                hostmanagement_interface.clk.next = \
                    not hostmanagement_interface.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostmanagement_interface.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)  # mdio enable, clkdiv =2+1*2=6
            yield hostmanagement_interface.writeconfig(0x340, 0x00000022)
            yield mdio_interface.mdc.posedge
            yield hostmanagement_interface.\
                mdiowriteop(intbv(0b01), intbv(0b1001100000),
                            intbv(0xABCD), block=False)
            yield mdio_interface.out.negedge
            wrindex = 32
            wrdata = intbv(0)[32:]
            while wrindex >= 0:
                wrdata[wrindex] = mdio_interface.out
                wrindex -= 1
                yield mdio_interface.mdc.posedge
            assert wrdata[32:] == 0x5982ABCD

        return testlogic, hostclkdriver, managementInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=6000)
    testInst.quit_sim()


def test_mdioread():

    @block
    def test():

        hostmanagement_interface = HostManagementInterface()
        mdio_interface = MDIOInterface()
        managementInst = management(hostmanagement_interface, mdio_interface)
        print("Testing MDIO Write Operation %s" % managementInst)

        @instance
        def hostclkdriver():
            while True:
                hostmanagement_interface.clk.next = \
                    not hostmanagement_interface.clk
                yield delay(5)

        def clkwait(count=1):
            while count:
                yield hostmanagement_interface.clk.posedge
                count -= 1

        @instance
        def testlogic():
            yield clkwait(count=10)  # mdio enable, clkdiv =2+1*2=6
            yield hostmanagement_interface.writeconfig(0x340, 0x00000022)
            yield mdio_interface.mdc.posedge
            yield hostmanagement_interface.\
                mdioreadop(intbv(0b10), intbv(0b1001100000), block=False)
            yield mdio_interface.out.negedge
            wrindex = 32
            wrdata = intbv(0)[32:]
            while wrindex >= 18:
                wrdata[wrindex] = mdio_interface.out
                wrindex -= 1
                yield mdio_interface.mdc.posedge
            assert wrdata[32:18] == 0x1A60
            mdio_interface.inn.next = 0
            rdindex = 15
            while rdindex >= 0:
                yield mdio_interface.mdc.posedge
                mdio_interface.inn.next = not mdio_interface.inn
                rdindex -= 1
            yield hostmanagement_interface.miimrdy.posedge
            assert hostmanagement_interface.rddata[16:] == 0x5555

        return testlogic, hostclkdriver, managementInst

    testInst = test()
    testInst.config_sim(trace=False)
    testInst.run_sim(duration=6000)
    testInst.quit_sim()


def test_convertible():

    hostmanagement_interface = HostManagementInterface()
    mdio_interface = MDIOInterface()
    managementInst = management(hostmanagement_interface, mdio_interface)
    print("Testing Convertibility %s" % managementInst)
    managementInst.convert(hdl='Verilog')
    managementInst.convert(hdl='VHDL')
