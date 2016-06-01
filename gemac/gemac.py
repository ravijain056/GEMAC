from myhdl import block, Signal, intbv, instances
from .client import client
from .txEngine import txEngine
from .rxEngine import rxEngine
from .gmii import gmii
from .flowControl import flowControl
from .mdio import mdio


@block
def gemac(txclient_interface, rxclient_interface, phy_interface,
          flow_interface, management_interface, mdio_interface, reset):

    txpause = Signal(bool(0))  # Transmit Pause Frame
    rxder = Signal(bool(0))  # Receive Data Error
    txd2engine = Signal(intbv(0)[8:])
    txd2gmii = Signal(intbv(0)[8:])
    rxd2engine = Signal(intbv(0)[8:])
    rxd2client = Signal(intbv(0)[8:])
    sampled_pauseval = Signal(intbv(0)[16:])

    clientInst = client(txclient_interface, txd2engine,
                        rxclient_interface, rxd2client, rxder)

    txEngineInst = txEngine(txclient_interface.gtxclk, txd2engine, txd2gmii,
                            txpause, sampled_pauseval)

    rxEngineInst = rxEngine(phy_interface.rxclk, rxd2client,
                            rxd2engine, rxder)

    flowControlInst = flowControl(flow_interface, txpause, sampled_pauseval)

    gmiiInst = gmii(phy_interface, txd2gmii, rxd2engine,
                    txclient_interface.gtxclk)

    mdioInst = mdio(management_interface, mdio_interface)

    return instances()
