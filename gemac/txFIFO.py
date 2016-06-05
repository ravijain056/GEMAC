from myhdl import block, instances


@block
def txFIFO(txlocallink_interface, txclient_interface,
           fifosize=20, framesize=160):

    """
        FIFO Size - Default - 20 (Temporary) - N0. of frames.
        Frame Size - Default = 160 (Temporary) - No. of bytes.
    """

    return instances()
