# GEMAC

[![Build Status](https://travis-ci.org/ravijain056/GEMAC.svg?branch=master)](https://travis-ci.org/ravijain056/GEMAC)
[![Code Health](https://landscape.io/github/ravijain056/GEMAC/master/landscape.svg?style=flat)](https://landscape.io/github/ravijain056/GEMAC/master)
[![Coverage Status](https://coveralls.io/repos/github/ravijain056/GEMAC/badge.svg?branch=master)](https://coveralls.io/github/ravijain056/GEMAC?branch=master)

GEMAC implementation and tools.



#Introduction
This repository hosts the MyHDL implementation of GEMAC which implements the MAC Sublayer in accordance with IEEE 802.3 2005 standard.
This work was started under Google summer of Code Program 2016 and is a Work in Progress.

# Pre-requisites:
1. Python 3.5
2. MyHDL(>=1.0dev)
3. Icarus Verilog

Note: The install scripts under '/scripts/ci/' can be used to install MyHDL and Verilog.

#Getting Started
- Clone the repository and perform the setup by executing the following command after navigating to the project folder.
    >> python setup.py install
- To run the tests enter the following commands
    >> cd test/
    >> py.test


#Using Models
- To be updated..

#Developers Applcation Notes

Xilinx User Guide for 1-GEMAC (UG144) is used as a major reference.
http://www.xilinx.com/support/documentation/ip_documentation/gig_eth_mac_ug144.pdf
The Design chosen to develop is GEMAC Core with Management Interface and Address Filter.
Major deviations from the userguide design are
- No use of statistics vectors.
- Use of Big Endian Format as opposed to Little Endian Format to store MAC Addresses.

For more details on the development,  one can follow the link: https://ravijain056.wordpress.com/category/myhdl/ , or contact me on ravijain056@gmail.com