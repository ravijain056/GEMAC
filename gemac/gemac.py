from myhdl import block, Signal, intbv
from gemac.txEngine import txengine
from gemac.rxEngine import rxengine
from .gmii import gmii
from .flowControl import flowcontrol
from .management import management
from .intrafaces import RxGMII_Interface, TxFlowInterface, TxGMII_Interface
from gemac.intrafaces import RxFlowInterface

rx0, rx1, tx, flow, managementreg, ucast0, \
    ucast1, addrtable0, addrtable1, addrfiltermode, reserved = range(11)
""" Indexing of configuration Registers"""


@block
def gemac(clientintf, phyintf, flowintf, hostintf, mdiointf, reset):
    txgmii_intf = TxGMII_Interface()
    rxgmii_intf = RxGMII_Interface()
    txflowintf = TxFlowInterface()
    rxflowintf = RxFlowInterface()

    configregs = [Signal(intbv(0)[32:]) for _ in range(10)]
    addrtable = [Signal(intbv(0)[48:]) for _ in range(4)]

    txengineinst = txengine(clientintf.tx, txgmii_intf, txflowintf,
                            configregs[tx], reset)

    rxengineinst = rxengine(clientintf.rx, rxgmii_intf, rxflowintf, configregs[rx0],
                            configregs[rx1], configregs[addrfiltermode],
                            addrtable, reset)

    flowcntrlinst = flowcontrol(flowintf, txflowintf, rxflowintf,
                                configregs[flow], reset)

    gmiiInst = gmii(txgmii_intf, rxgmii_intf, phyintf, reset)

    managementinst = management(hostintf, mdiointf, configregs,
                                addrtable, reset)

    return txengineinst, rxengineinst, flowcntrlinst, gmiiInst, managementinst
