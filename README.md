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

# How do I actually use the simulator?

Open the simulator. First you need to construct the graph, if you don't want to play with the default one.

 - Add new nodes by clicking **right mouse button**
 - Select node by clicking it with mouse
 - When selected, you can
	 - Color the node, by pressing one of the **keys 1-9**
	 - Empty the color, by pressing **key 0**
	 - Delete the node, by pressing **delete**
	 - Construct an edge by clicking another node
	 - Click anywhere else to unselect the node

After the graph is constructed:

 - Select a problem by clicking on dropdown **Select problem**
- Select either of the problems
	- Note that bipartite maximal matching has prerequisites for the graph: it has to be bipartite and colored with two colors
	- Minimum vertex cover 3-approximation does not have prerequisites
	- If the prerequisites does fullfill, the running terminates immediately
- Press **Run** to start the simulation
- After this, proceed by pressing **Next round** until the algorithm halts
	- Algorithm halts when all states are stopping states. In this case, next round - button becomes disabled indicating the stop
	- If the algorithm design is poor or the validaty criteria for the graph is incomplete, it is possible that the algorithm does not halt at all. This is quite easy to identify, though
- When the algorithm has stopped, you can reset the simulation by pressing **Clear**

# Photos

![Bipartite maximal matching](https://raw.githubusercontent.com/olkkon/da-pn-model/main/img/Bipartite.png)

![Minimum vertex cover 3-approximation](https://raw.githubusercontent.com/olkkon/da-pn-model/main/img/MVC3.png)

![Default setting](https://raw.githubusercontent.com/olkkon/da-pn-model/main/img/default.png)
