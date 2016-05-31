from myhdl import block, instances


@block
def flowControl(flow_interface, transmitPauseFrame, sampledPauseVal):

    """
    *Flow Control*

    pauseReq - Control Signal From Host/Client to initate Pause Control Frame
    pauseVal(16 bits) - The Pause Value
    transmitPauseFrame - Control Signal to indicate pending Pause request to Transmit Engine.
    sampledPauseVal(16 bits) - Most Recent Sampled Pause Value 

    """

    return instances()
