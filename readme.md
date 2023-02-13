# Welcome to The University of Utah's C/Id methodology software suite
The **C/ID API** is a Python3 based software suite that aids analog integrated circuit (IC) designers in realizing their circuit designs in fast time scales with accurate scripting capabilities in a technology agnostic fashion. This API affords an IC designer to accurately model and create technology agnostic design scripts and equations to greatly reduce the amount of SPICE simulations conventionally needed in analog IC design and design migration.

The **C/Id** methodology is very similar to the **gm/Id** methodology but with a few key differences. One of the large differences is in characterizations of technologies. C/Id uses a current source based testbench with only one current source as opposed to voltage source based testbenches as in gm/Id for technology characterizations. Another large difference is in how lookup tables are stored. Since only one current source is needed to characterize a technology, this means that only a 1-D lookup table is needed as opposed to a 4-D lookup table as in gm/ID.

 **This API supports lookups for C/Id, gm/Id & Inversion Coefficent (IC)**

Both the C/Id and gm/Id methodologies use lookup tables to store characterization results and produce SPICE accurate lookups. C/Id also has the ability to do all lookups in the same fashion and function that gm/Id is capable of but with more ratio aware lookups.

For now the C/Id software only supports Cadence/Spectre simulator for characterizations using the Spectre Measurement Description Language (MDL) for technology characterization.

# Installation
Installation procedures are found in the docs directory in the file installation_guide.pdf
# Technology Characterization
All FET technologies can be characterized with this testbench.
![cid_testbench](images/cid_testbench.png)

 The value of the ideal current source that connects the PFET and NFET drains together is swept and DC operating points for each device are saved and extracted with each DC operating point for lookup table generation. The Spectre MDL scripts provided in this repo create CSV files for lookup tables. The software takes care of translating the CSV files into the API. This characterization should be done for all lengths of transistor under interested or for a good span of lengths available in a given PDK. This charactetrization only needs to be done once per PDK.

 This testbench provides less complexity than the generally accepted gm/Id lookup table generation that use 3 voltage sources for both NFET and PFET devices.

 API uses Pandas DataFrames for storing tables and doing lookups.


# API Design Example

# Files and Directories Description

# Getting Started

# Naming Conventions

All lookups with the C/Id API use the same lookup names for model parameters across all technologies. This enables uniform design scripts across all technologies. The following is the list of currently supported lookups

- "kgm" - ratio of  transconductance divided by its drain current
- "kcgd" - ratio of gate drain capacitance divided by drain current
- "kcgs" - ratio of  gate source capacitance divided by drain current
- "kcds" - ratio of drain source capacitance divided by drain current
- "kcss" - ratio of total capacitance at source node divided by drain current
- "kcgg" - ratio of total capacitance at gate node divided by drain current
- "kcdd"- ratio of total capacitance at drain node divided by drain current
- "kcdb" - ratio of drain bulk capacitance divided by drain current
- "kcgb" - ratio of gate bulk capacitance divided by drain current
- "kcsb" - ratio of source bulk capacitance divided by drain current
- "cgd, cgs, cds, css, cgg, cdd", kcdb, kcgb, kcsb- capacitances seen at each node following convention above
- "gm" - transconductance
- "vth" - voltage threshold
- "rds" - drain source resistance (reciprocal of gds)
- "gds" - drain source conductance (reciprocal of rds)
- "ids" - drain source current
- "vds" - drain source voltage
- "ft" - transit frequency (gm/(2*pi*cgg))
- "wt" - transit frequency in radians/sec (gm/cgg)
- "va" - early voltage
- "ro" - output resistance
- "ic" - inversion coefficient
- "n" - subthreshold slope factor