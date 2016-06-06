from gemac.interfaces import HostManagementInterface, MDIOInterface
from gemac.management import management
from myhdl import instance, delay, block, intbv


def test_readwriteconfig():

    @block
    def writeconfig_operation():

        hostmanagement_interface = HostManagementInterface()
        mdio_interface = MDIOInterface()
        managementInst = management(hostmanagement_interface, mdio_interface)
        print("Testing Read/Write Configuration Register%s" % managementInst)

        @instance
        def write():
            yield clkWait(count=10)
            yield hostmanagement_interface.writeconfig(0x340, 0x12345678)
            yield clkWait(count=4)
            yield hostmanagement_interface.readconfig(0x340)
            assert hostmanagement_interface.rddata[32:] == intbv(0x12345678)

        @instance
        def hostclkdriver():
            while True:
                hostmanagement_interface.clk.next = \
                    not hostmanagement_interface.clk
                yield delay(5)

        def clkWait(count=1):
            while count:
                yield hostmanagement_interface.clk.posedge
                count -= 1

        return write, hostclkdriver, managementInst

    writeInst = writeconfig_operation()
    writeInst.config_sim(trace=True)
    writeInst.run_sim(duration=300)
