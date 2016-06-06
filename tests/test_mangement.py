from gemac.interfaces import HostManagementInterface, MDIOInterface
from gemac.management import management
from myhdl import instance, delay, Simulation


def test_writeconfig():

    def writeconfig_operation(hostmanagement_interface):
        @instance
        def write():
            yield delay(100)
            yield hostmanagement_interface.writeconfig(0x340, 0x12345678)
            yield delay(20)
            yield hostmanagement_interface.idle()
            yield delay(40)
            yield hostmanagement_interface.readconfig(0x340)
            print("Read Data: %s" % hostmanagement_interface.rddata)
            assert hostmanagement_interface.rddata == 0x12345678

        @instance
        def hostclkdriver():
            while True:
                hostmanagement_interface.clk.next = not hostmanagement_interface.clk
                yield delay(5)

        return write, hostclkdriver

    hostmanagement_interface = HostManagementInterface()
    mdio_interface = MDIOInterface()
    managementInst = management(hostmanagement_interface, mdio_interface)
    print("Testing %s" % managementInst)

    writeInst = writeconfig_operation(hostmanagement_interface)

    sim = Simulation(managementInst, writeInst)
    sim.run(2000)
