from myhdl import Signal, intbv


class managementInterface():

    def __init__(self):

        # Client Management Interface
        hostclk = Signal(bool(0))  # Host Clock
        opcode = Signal(intbv(0)[2:])  # host Opcode
        regaddress = Signal(intbv(0)[10:])  # Configuration Register Address
        wrdata = Signal(intbv(0)[32:])  # Write Data
        rddata = Signal(intbv(0)[32:])  # Read Data
        miimsel = Signal(bool(0))  # MIIM select
        hostreq = Signal(bool(0))  # host Request
        miimrdy = Signal(bool(0))  # hostMIIM_ready
