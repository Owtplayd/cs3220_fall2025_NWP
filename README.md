# 🧠 CS3220 – Lab 6
### Constraint Satisfaction & Propagation (AC-3)
### Author: *Nemanja and Brian*

---

### 📘 Overview

This lab implements **Constraint Satisfaction Problems (CSPs)** using the lab’s provided CSP framework (`src/CSPclass.py`, `src/algorithms.py`, `src/utils.py`).  
We extend these classes to solve two new problems — as described in **Lab 6: CSP Constraints Propagation Tutorial & Tasks** — and visualize both using a **Streamlit web application**.

The app demonstrates:
- how **CSPs** are modeled (variables, domains, neighbors, constraints)  
- how the **AC-3 algorithm** enforces arc consistency  
- how constraint propagation reduces possible values (domains)  
- how visualizations (via PyVis) show the network before and after AC-3  

---

## 🧩 Tasks Implemented

### **Task 1 – Exam Schedule CSP (12 points)**
#### 📋 Description
We create an exam schedule for seven courses.  
Each course is a CSP variable; its domain is the possible exam days (`Mon, Tue, Wed`).  
The single constraint: **no two courses can have exams on the same day** (all different).

#### 🏗 Implementation Steps
| Step | Implementation | File |
|------|-----------------|------|
| 1 | Defined variables and domains for each course (from PDF). | `data/data_lab6_task1_examCSP.py` |
| 2 | Built a complete neighbor graph (all courses connected). | `data/data_lab6_task1_examCSP.py` |
| 3 | Applied constraint `different_values_constraint(A,a,B,b)`. | `src/utils.py` imported into data file |
| 4 | Built CSP instance via `CSPBasic`. | `data/data_lab6_task1_examCSP.py` |
| 5 | Enforced arc consistency with AC-3 algorithm. | `src/algorithms.py` / `csp_AC3_agentProgram.py` |
| 6 | Visualized graph (before and after AC-3) using PyVis. | `app.py` |
| 7 | Displayed resulting domains for three specific courses (Practical Programming Methodology, Computer Organization & Architecture I, Linear Algebra I). | `app.py` |

#### 🖼 Visualization Meaning
- **Node = course**  
- **Edge = “must have different day” constraint**  
- **Yellow node = domain fixed (single value)**  
- **White node = multiple possible days**  
- **Red edges = binary constraints**  

After AC-3 runs, courses that conflict with fixed ones lose those days from their domain.

---

### **Task 2 – Asterisk Sudoku CSP (13 points)**
#### 📋 Description
A 9×9 Sudoku variant where:  
- every row, column, and 3×3 box must contain 1–9 once, **and**  
- the nine asterisk-shaded cells also must contain 1–9 once.  

Each cell is a variable; its domain is 1–9 (initially or with givens from the puzzle).

#### 🏗 Implementation Steps
| Step | Implementation | File |
|------|-----------------|------|
| 1 | Defined 81 variables (A1 – I9) via helper `cross(ROWS,COLS)`. | `data/data_lab6_task2_asteriskSudokuCSP.py` |
| 2 | Set domains (1–9 or given values from puzzle). | `data/data_lab6_task2_asteriskSudokuCSP.py` |
| 3 | Computed neighbors for each cell (same row, col, box, asterisk). | `data/data_lab6_task2_asteriskSudokuCSP.py` |
| 4 | Applied constraint `x != y`. | `data/data_lab6_task2_asteriskSudokuCSP.py` |
| 5 | Built CSP with `CSPBasic`. | `data/data_lab6_task2_asteriskSudokuCSP.py` |
| 6 | Applied AC-3 to propagate constraints and reduce domains. | `csp_AC3_agentProgram.py` / `app.py` |
| 7 | Visualized constraint graph before and after AC-3. | `app.py` |

#### 🖼 Visualization Meaning
| Edge Color | Constraint Type |
|-------------|----------------|
| **Red** | Same row |
| **Blue** | Same column |
| **Green** | Same 3×3 box |
| **Purple** | Asterisk constraint |

- **Yellow nodes** = fixed (givens or domain size 1)  
- **White nodes** = unfixed (domain > 1)  

After AC-3, the hover tooltips show each cell’s reduced domain.

---

## 🖥 Streamlit App Structure

| Component | Purpose |
|------------|----------|
| **`app.py`** | Main Streamlit app with two tabs (Task 1 & Task 2). |
| **`show_html()`** | Embeds PyVis-generated HTML graphs into Streamlit. |
| **`visualize_exam_csp()`** | Draws Task 1 constraint graph. |
| **`visualize_asterisk_sudoku()`** | Draws Task 2 constraint graph. |
| **Tabs** | “Task 1 – Exam Schedule” and “Task 2 – Asterisk Sudoku”. |

**Workflow inside each tab:**
1. Build CSP from `data/…` file.  
2. Generate “Before AC-3” PyVis graph → HTML.  
3. Run `AC3()` to enforce arc consistency.  
4. Generate “After AC-3” PyVis graph → HTML.  
5. Display both graphs inline with final domains.

---

## 📂 Folder Layout

```
CS3220_FALL2025_NWP/
│
├── app.py
├── csp_AC3_agentProgram.py
├── run_task1_exam.py
├── run_task2_asterisk.py
│
├── data/
│   ├── data_lab6_task1_examCSP.py
│   ├── data_lab6_task2_asteriskSudokuCSP.py
│   ├── RomaniaMapData.py
│   └── vacuumWorldData.py
│
├── src/
│   ├── CSPclass.py
│   ├── algorithms.py
│   ├── utils.py
│   └── ...
│
├── requirements.txt
└── README.md
```

---

## ▶️ Running the App

1. Install dependencies:
   ```bash
   pip install streamlit pyvis networkx
   ```

2. Launch Streamlit:
   ```bash
   streamlit run app.py
   ```

3. Open the browser (at `http://localhost:8501`)  
   → Navigate between **Task 1** and **Task 2** tabs.  

---

## 🧾 Output Artifacts

| File | Description |
|------|--------------|
| `exams_before.html` / `exams_after.html` | Task 1 constraint graphs (before/after AC-3). |
| `asterisk_before.html` / `asterisk_after.html` | Task 2 Sudoku constraint graphs (before/after AC-3). |

---

## 🎯 How This Meets Instructor’s Requirements

| Requirement (from PDF) | Where Implemented / Shown | Status |
|--------------------------|---------------------------|---------|
| CSP based on CSPBasic class | All data files (`make_exam_csp`, `make_asterisk_sudoku_csp`) | ✅ |
| Define variables, domains, neighbors, constraints | Data files for both tasks | ✅ |
| Apply AC-3 to enforce arc consistency | `src/algorithms.AC3()` in agent and Streamlit | ✅ |
| Show resulting domains (Task 1 – 3 courses, Task 2 – all cells) | `app.py` outputs in both tabs | ✅ |
| Two visualizations (before/after AC-3) | PyVis graphs embedded in Streamlit | ✅ |
| Reuse all provided files (src classes, utils) | Imports from `src.*` and `utils` | ✅ |
| Visualize constraint types (row, col, box, asterisk) | Color-coded edges in Sudoku tab | ✅ |

---

### 🏁 Conclusion
This project fully reproduces the instructor’s Lab 6 requirements:  
- Both CSPs are built on the provided framework.  
- AC-3 propagation is applied and visualized.  
- The Streamlit app presents results interactively and clearly.  

🎓 **Lab 6 – CSP & Constraint Propagation: Complete!**
