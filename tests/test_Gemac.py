from gemac.gemac import gemac
from gemac.interfaces import phyInterface, flowControlInterface,\
    managementInterface, txFIFOClientInterface, rxFIFOClientInterface,\
    mdioInterface
from myhdl import ResetSignal


class TestGemacCore:

    def setup_method(self, method):

        txclient_interface = txFIFOClientInterface()
        rxclient_interface = rxFIFOClientInterface()
        phy_interface = phyInterface()
        flow_interface = flowControlInterface()
        management_interface = managementInterface()
        mdio_interface = mdioInterface()
        reset = ResetSignal(0, active=0, async=True)
        gemacInst = gemac(txclient_interface, rxclient_interface,
                          phy_interface, flow_interface, management_interface,
                          mdio_interface, reset)
        print("Testing %s" % gemacInst)

    def test_nothing(self):
        assert True
