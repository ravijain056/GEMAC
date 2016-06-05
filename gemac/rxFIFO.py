from myhdl import block, instances


@block
def rxFIFO(rxlocallink_interface, rxclient_interface, flow_interface,
           highthres=0.75, lowthres=0.66, size=20):
    """
       Generates pause request when highthres% of the capacity is filled
       and resume request when the lowthres% of capacity is obtained again.

       Default Size is in frames.
    """

    return instances()
