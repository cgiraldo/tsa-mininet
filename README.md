#tsa-mininet
##TSA: Integrating Wireless Terminals into Globally Optimal Software-Defined Networks

This repository provides the code to reproduce the experiments of the paper titled *TSA: Integrating Wireless Terminals into Globally Optimal Software-Defined Networks*.

It uses Mininet to emulate a mmWave access network. Wireless links are modeled with a dynamic link bandwidth assignment (see `wireless.py`).

Software-Defined Access Network Selection is achieved by incorporating a virtual switch inside the wireless terminal. This switch is connected to the four closer Access Points (see `tsanet.py`). The Access Network Selection is performed by programming the virtual switch with the OpenFlow protocol (see `selection_algorithm.py` and `fill_rt.py`).

###Prerequisites

The evaluation was performed with:

* A Core i7-4510U with 8GB of RAM laptop.
* Ubuntu 14.04.
* Python 2.7.6.
* [Mininet 2.2.0](https://github.com/mininet/mininet/tree/2.2.0).

### Running the simulations

The steps to get similar graphs to the ones published in the paper (it may slightly vary since mininet is emulation) are:

1. `sudo ./run.sh`: it may take several hours since the simulations are repeated 20 times with different random seeds in order to estimate confidence intervals.

2. `./process_output.sh`: this script estimates the confidence intervals and generates two graphs:

       * output/test1.pdf
       * output/test2.pdf
