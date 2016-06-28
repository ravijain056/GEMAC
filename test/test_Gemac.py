from gemac.gemac import gemac
from gemac.interfaces import PHYInterface, FlowControlInterface,\
    HostManagementInterface, MDIOInterface, ClientInterface
from myhdl import ResetSignal, block
import pytest


def clkwait(clk, count=1):
    while count:
        yield clk.posedge
        count -= 1


@pytest.fixture()
def setuptb():
    clientintf = ClientInterface()
    phyintf = PHYInterface()
    flowintf = FlowControlInterface()
    hostintf = HostManagementInterface()
    mdiointf = MDIOInterface()
    reset = ResetSignal(0, active=0, async=True)

    @block
    def testbench():
        gemacinst = gemac(clientintf, phyintf, flowintf, hostintf,
                          mdiointf, reset)
        return gemacinst

    return testbench


def test_nothing(setuptb):
    tbinst = setuptb()
    print("Testing Nothing %s" % tbinst)
    assert True
