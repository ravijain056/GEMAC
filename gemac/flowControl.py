from myhdl import block

@block
def flowControl(pauseReq, pauseVal, transmitPauseFrame, sampledPauseVal):
    
    """
    *Flow Control*
    
    pauseReq - Control Signal From Host/Client to initate Pause Control Frame
    pauseVal(16 bits) - The Pause Value
    transmitPauseFrame - Control Signal to indicate pending Pause request to Transmit Engine.
    sampledPauseVal(16 bits) - Most Recent Sampled Pause Value 
    
    """
    
    return instances()
