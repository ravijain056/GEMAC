from gemac.interfaces import HostManagementInterface, MDIOInterface
from gemac.management import management
from myhdl import instance, delay, block, intbv, now


def test_readwriteconfig():

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
    testInst.config_sim(trace=True)
    testInst.run_sim(duration=300)
    testInst.quit_sim
