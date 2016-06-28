from myhdl import block, instances


@block
def rxEngine(rxclientintf, rxgmii_intf, reset):

    """ Receiver Engine.

    Accepts Ethernet frame data from the GMII Block, removes the preamble field
    at the start of the frame, removes padding bytes and Frame Check Sequence.
    It performs error detection on the received frame using information such
    as the frame check sequence field, received GMII error codes, and legal
    frame size boundaries.

    """

    return instances()
