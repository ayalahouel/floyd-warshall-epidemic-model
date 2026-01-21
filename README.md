# Floyd–Warshall Epidemic Model

## 📌 Project Overview
This project presents a Python implementation of the **Floyd–Warshall algorithm** applied to a **real-world inspired epidemic propagation model**.

Beyond its classical use in network routing, the Floyd–Warshall algorithm is here used to analyze **virus transmission risks** within a social network.  
The project demonstrates how indirect connections between individuals can play a critical role in epidemic spread.

This work was carried out as part of an academic Master 1 project.

---

## 🧠 Algorithm: Floyd–Warshall
The Floyd–Warshall algorithm is a dynamic programming algorithm used to compute the **shortest paths between all pairs of vertices** in a directed, weighted graph.

**Key characteristics:**
- Works with directed and weighted graphs
- Supports negative weights (without negative cycles)
- Time complexity: **O(N³)**
- Particularly efficient for dense graphs of moderate size

---

## 🦠 Epidemic Modeling Approach
In this project, the shortest-path problem is reinterpreted as a **risk propagation problem**.

### Graph Representation
- **Vertices (Nodes)**: Individuals in a community (nodes 0 to 19)
- **Directed Edges**: Possible virus transmission from one person to another
- **Weights**: Resistance to contamination  
  - Low weight → high infection risk (close contact)
  - High weight → low infection risk (distant or protected contact)

Thus, the shortest path computed by the algorithm represents the **path of minimal resistance for virus transmission**.

---

## 📊 Dataset Description
The dataset models a realistic social structure:
- **20 nodes** representing individuals
- **49 directed edges** representing interactions
- Social structure includes:
  - Family clusters (very low resistance)
  - Professional connections (moderate resistance)
  - Social bridges (potential super-spreaders)

The data files are located in the `data/` directory.

---

## 🔍 Case Study: Patient 0 → Patient 19
A key experiment analyzes how the virus could spread from **Patient 0** to **Patient 19**, who belong to different social groups.

### Result
- **Minimal transmission cost**: 40
- **Computed path**:
0 → 1 → 6 → 7 → 8 → 9 → 14 → 19

### Interpretation
- The algorithm avoids obvious but highly resistant paths
- Social bridge nodes play a crucial role
- Indirect connections significantly increase transmission risk

---


## Technologies
* **Python 3.8+** - Core programming language
* **NumPy** - Efficient matrix operations
* **Matplotlib** - Graph visualization and plotting
* **Graph Theory** - Algorithmic foundation
* **Dynamic Programming** - Floyd-Warshall methodology
* **Object-Oriented Programming** - Code architecture

## Documentation
* **Technical Report**: `Rapport_Floyd_warshall.pdf` - Complete analysis including algorithm implementation, complexity study, and epidemic modeling approach
* **Graph Visualizations**: `graphs/TestGraphs.pdf` - Graphical representations of test cases and transmission paths
* **Presentation**: `presentation/Project_Presentation.pptx` - Academic presentation of the project
* **Code Documentation**: Inline comments and docstrings throughout source files

## Project Team
**Group Members:**
- Aya LAHOUEL
- Meriem TIH  
- Zoubir SAHNOUN
- Mohamed Hedi MOURALI
- Mohamed Ilyes BEN SAID
- Mohamed SAKHO

**Academic Context:**
- Master 1 in Computer Science
- Academic Year: 2025–2026
- Institution: EFREI Paris
- Course: Graph Algorithms and Applications
