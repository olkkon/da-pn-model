# What?

This is a simulation tool to simulate distributed algorithms in the port-numbered model (PN). The tool implements following features:

 - Customizable graph view: add, delete or color nodes, add edges between nodes
 - Supports both "normal" algorithms and those which use simulation on virtual network
 - Currently two algorithms implemented:
	 - Bipartite maximal matching on 2-colored, bipartite graphs
	 - Minimum vertex cover 3-approximation, simulates the algorithm above in a virtual network to obtain the result
- Round by round progress with intermediate states for all nodes
- Great abstraction level to allow further development of other algorithms



# How do I run it?

The tool is fully implemented in Python, version 3.9 preferred. Only one library is required, namely **pygame**. Install in bash as follows:

    python3 -m pip install -U pygame --user

Then you can run the tool in it's root folder:

    python3 playground.py

