from myhdl import block, instances


@block
def txengine(txclientintf, txgmii_intf, txflowintf, txconfig, reset):
    """Transmit Engine.

    Accepts Ethernet frame data from the Client Transmitter interface,
    adds preamble to the start of the frame, add padding bytes and frame
    check sequence. It ensures that the inter-frame spacing between successive
    frames is at least the minimum specified. The frame is then converted
    into a format that is compatible with the GMII and sent to the GMII Block.

    Args:


    """

    return instances()
