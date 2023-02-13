# Welcome to The Unviersity of Utah's C/Id methodology software suite
The **C/ID API** is a Python3 based software suite that aids analog integrated circuit (IC) designers in realizing their circuit designs in fast time scales with accurate scripting capabilities in a technology agnostic fashion. This API affords an IC designer to accurately model and create technology agnostic design scripts and equations to greatly reduce the amount of SPICE simulations conventionally needed in analog IC design and design migration.

The **C/Id** methodology is very similar to the **gm/Id** methodology but with a few key differences. One of the large differences is in characterizations of technologies. C/Id uses a current source based testbench with only one current source as opposed to voltage source based testbenches as in gm/Id for technology characterizations. Another large difference is in how lookup tables are stored. Since only one current source is needed to characterize a technology, this means that only a 1-D lookup table is needed as opposed to a 4-D lookup table as in gm/ID.

 **This API supports lookups for C/Id, gm/Id & Inversion Coefficent (IC)**

Both the C/Id and gm/Id methodologies use lookup tables to store characterization results and produce SPICE accurate lookups. C/Id also has the ability to do all lookups in the same fashion and function that gm/Id is capable of.

For now the C/Id software only supports Cadence/Spectre simulator for characterizations using the Spectre Measurement Description Language (MDL) for technology characterization.

# Installation

# Technology Characterization

# Getting Started

# API Design Example
# Files and Directories Description



