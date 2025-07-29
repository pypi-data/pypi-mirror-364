# Fusion- Flexible Unification of Structured Intermodal Object Networks

<hr></hr>

Fusion is a Python package that provides solutions to the entity resolution in multimodal graphs problem. 
It implements the Fusion algorithm from the paper "Fusion: Flexible Unification of Structured Intermodal Object Networks" by Yoel Ashkenazi and Yoram Louzoun.

## Table of Contents

- [Installation](#installation)
- [Quick Tour](#quick-tour)
- [Directory Tree](#directory-tree)
- [Evaluation](#evaluation)
- [Plotting Graphs](#plotting-graphs)
- [Configuration File Example](#configuration-file-example)
- [Main Git Repository](#main-git-repository)

---

## Installation

To install the package and its dependencies, run:

```bash
pip install Fusion

```
Make sure you have Python 3.8+ installed.

<hr></hr>

## Quick Tour
### Directory Tree

```json
project_root/
│
├── Fusion/
│   └── main.py
├── Entity_detection/
│   ├── my_algorithm.py
│   └── Record_linkage/
│       └── RL_test.py
├── evaluate.py
├── utils.py
├── data/
│   └── graph.gpickle
├── output/
│   ├── DatasetName_results.json
│   └── DatasetName_colored_graph.gpickle
├── requirements.txt
└── config.json
```

1. Fusion/main.py: Main entry point.
2. Entity_detection/: Contains model and record linkage code.
3. evaluate.py: Evaluation functions.
4. utils.py: Utility functions (drawing, graph manipulation).
5. data/: Place your .gpickle graph files here.
6. output/: Results and colored graphs are saved here.

<hr></hr>

Running the Fusion Model or Record Linkage Test
Use the main script to run the fusion process or record linkage test:

```python
python Fusion/main.py --config path/to/config.json --output path/to/output_folder
```

* --config: Path to your configuration file (see Configuration File Example).
* --output: Directory where results and colored graphs will be saved.
Evaluating Results
After running the model, results are saved as a pickle file in your output directory. 


## Evaluation
To evaluate the partition, use the get_truth_values function from evaluate.py:

```python
from evaluate import get_truth_values

TP, FP, TN, FN = get_truth_values(graph, true_graph, partition, true_entities)
```

Explanation of Metrics:
1. True Positives (TP): Vertices correctly grouped.
2. False Positives (FP): Vertices incorrectly grouped (should not be in the partition).
3. True Negatives (TN): Vertices correctly not grouped.
4. False Negatives (FN): Vertices that should have been grouped but were not.

Calculating Performance Metrics:
Using the above values, you can calculate:


* Precision: TP / (TP + FP) - Measures the accuracy of positive predictions.
* Recall: TP / (TP + FN) - Measures the ability to find all positive instances.
* F1-Score: 2 * (Precision * Recall) / (Precision + Recall) - Harmonic mean of precision and recall.

Example:
```python
precision = TP / (TP + FP) if (TP + FP) > 0 else 0
recall = TP / (TP + FN) if (TP + FN) > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-Score: {f1_score}")
```

#### Saving Results:
The results, including metrics, are saved as a JSON file in the output directory. For example:

```python
import json

results = {
    'TP': TP,
    'FP': FP,
    'TN': TN,
    'FN': FN,
    'precision': precision,
    'recall': recall,
    'F1_score': f1_score,
}

with open('output/results.json', 'w') as f:
    json.dump(results, f, indent=4)
```

This ensures you can review and analyze the evaluation metrics later.

<hr></hr>

## Plotting Graphs
To visualize the partitioned graph, use the draw method from utils.py. Below are examples of how to use it:

Example 1: Plotting a Colored Graph

```python
import utils
import networkx as nx

# Load the true graph and partition
true_graph = utils.load_dataset("data/graph.gpickle")
partition = {"node1": 0, "node2": 1, "node3": 0}  # Example partition

# Color the graph by partition
colored_graph = utils.color_by_partition(true_graph, partition)

# Plot the graph
utils.draw(colored_graph)
```

This will display the graph with nodes colored according to their partition.

Example 2: Saving the Colored Graph

```python
import pickle as pkl

# Save the colored graph
with open("output/colored_graph.gpickle", "wb") as f:
    pkl.dump(colored_graph, f, protocol=pkl.HIGHEST_PROTOCOL)

print("Colored graph saved to output/colored_graph.gpickle")
```

Example 3: Plotting with Custom Layout

```python
import matplotlib.pyplot as plt

# Use a spring layout for better visualization
pos = nx.spring_layout(colored_graph)

# Draw the graph with the custom layout
utils.draw(colored_graph, pos=pos)

# Show the plot
plt.show()
```

<hr></hr>

## Configuration File Example
Below is an example of a configuration file (config.json). 

Note:
1. graph_path must point to a .gpickle file.
2. Parameters like blue_in, red_out, C, etc., affect the model.
3. Parameters like test type, add_num, remove_num are for execution.

```json
{
    "verbosity_level": 1,           // int: Logging level (0 = silent, 1 = basic info, 2 = detailed debug info)
    "draw": false,                  // bool: Whether to plot graphs during execution
    "blue_in": 1.0,                 // float: Weight for blue intra-cluster edges
    "blue_out": 1.0,                // float: Weight for blue inter-cluster edges
    "red_in": 1.0,                  // float: Weight for red intra-cluster edges
    "red_out": 1.0,                 // float: Weight for red inter-cluster edges
    "C": 1.0,                       // float: Regularization parameter for the model
    "epsilon": 1e-6,                // float: Convergence threshold for iterative algorithms
    "history": true,                // bool: Whether to keep a history of iterations
    "type_dist": null,              // null or str: Type of distance metric (e.g., "euclidean", "cosine")
    "quality_type": "adjusted_OOE", // str: Quality metric for evaluating partitions (e.g., "adjusted_OOE", "NMI")
    "amplitude": 5.0,               // float: Amplitude parameter for edge weight adjustments
    "update_factor": 0.1,           // float: Factor for updating weights during iterations
    "ddelta": 0.1,                  // float: Step size for parameter updates
    "iterator": false,              // bool: Whether to use an iterative approach
    "decompose": false,             // bool: Whether to decompose the graph into subgraphs
    "graph_path": "data/graph.gpickle", // str: Path to the input graph file (must be a .gpickle file)
    "name": "DatasetName",          // str: Name for the dataset (used in output file naming)
    "test type": "GM",              // str: Test type ("GM" for Fusion, "RL" for Record Linkage)
    "add_num": 100,                 // int: Number of false identity edges to add to the graph
    "remove_num": 100,              // int: Number of identity edges to remove from the graph
    "removal_chance": 0.2           // float: Probability of removing an edge during preprocessing
}
```

#### Key Notes:
* graph_path: Ensure this points to a valid .gpickle file containing the graph data.

* test type: Use "GM" for running the Fusion model or "RL" for Record Linkage tests.

* Model Parameters: Parameters like blue_in, red_out, C, etc., directly affect the behavior of the Fusion model.

* Execution Parameters: Parameters like add_num, remove_num, and removal_chance control preprocessing and execution behavior.

<hr></hr>

## Main Git Repository
For further information, updates, and exemplary material, please refer to the main Git repository:
[GitHub Repository](https://github.com/yoelAshkenazi/MAGIC)
