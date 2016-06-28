from myhdl import block, instance, delay, ResetSignal, Signal, intbv
from gemac.gemac import TxGMII_Interface, TxFlowInterface
from gemac.txEngine import txengine
from gemac.interfaces import TxFIFOClientInterface
import pytest


def clkwait(clk, count=1):
    while count:
        yield clk.posedge
        count -= 1


@pytest.fixture()
def setuptb():
    txclientintf = TxFIFOClientInterface()
    txgmii_intf = TxGMII_Interface()
    txflowintf = TxFlowInterface()
    txconfig = Signal(intbv(0)[32:])
    reset = ResetSignal(1, active=0, async=True)

    @block
    def testbench():
        dutinst = txengine(txclientintf, txgmii_intf, txflowintf,
                           txconfig, reset)

        @instance
        def hostclkdriver():
            while True:
                txclientintf.clk.next = \
                    not txclientintf.clk
                yield delay(5)

        @instance
        def resetonstart():
            reset.next = 0
            yield clkwait(txclientintf.clk, count=2)
            reset.next = 1
            yield clkwait(txclientintf.clk, count=2)

        return dutinst, hostclkdriver, resetonstart

    return testbench, txclientintf, txgmii_intf, txflowintf, txconfig


def test_txnormal():
    assert True
