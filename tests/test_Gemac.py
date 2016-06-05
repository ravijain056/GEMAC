from gemac.gemac import gemac
from gemac.interfaces import PHYInterface, FlowControlInterface,\
    HostManagementInterface, TxFIFOClientInterface, RxFIFOClientInterface,\
    MDIOInterface
from myhdl import ResetSignal


class TestGemacCore:

    def setup_method(self, method):

        txclient_interface = TxFIFOClientInterface()
        rxclient_interface = RxFIFOClientInterface()
        phy_interface = PHYInterface()
        flow_interface = FlowControlInterface()
        hostmanagement_interface = HostManagementInterface()
        mdio_interface = MDIOInterface()
        reset = ResetSignal(0, active=0, async=True)
        gemacInst = gemac(txclient_interface, rxclient_interface,
                          phy_interface, flow_interface,
                          hostmanagement_interface, mdio_interface, reset)
        print("Testing %s" % gemacInst)

    def test_nothing(self):
        assert True
