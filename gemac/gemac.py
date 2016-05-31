from myhdl import block, Signal, intbv, instances
from gemac import client, txEngine, rxEngine, flowControl, gmii, mdio


@block
def gemac(client_interface, phy_interface, flow_interface,
          management_interface, mdio_interface, reset):

    txpause = Signal(bool(0))  # Transmit Pause Framse
    rxder = Signal(bool(0))  # Receive Data Error
    txd2engine = Signal(intbv(0)[8:])
    txd2gmii = Signal(intbv(0)[8:])
    rxd2engine = Signal(intbv(0)[8:])
    rxd2client = Signal(intbv(0)[8:])
    sampled_pauseval = Signal(intbv(0)[16:])

    clientInst = client(client_interface, txd2engine,
                        rxd2client, rxder)

    txEngineInst = txEngine(client_interface.gtxclk, txd2engine, txd2gmii,
                            txpause, sampled_pauseval)

    rxEngineInst = rxEngine(phy_interface.rxclk, rxd2client,
                            rxd2engine, rxder)

    flowControlInst = flowControl(flow_interface, txpause, sampled_pauseval)

    gmiiInst = gmii(phy_interface, txd2gmii, rxd2engine,
                    client_interface.gtxclk)

    mdioInst = mdio(management_interface, mdio_interface)

    return instances()
