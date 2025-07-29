# SMUME: Saint Martin's University Mechanical Engineering Curriculum Planner

SMUME is a Python-based tool for visualizing and managing Mechanical Engineering degree plans at Saint Martin’s University. It supports students, advisors, and faculty by offering a flexible and programmable way to define curricula, create student-specific academic plans, and generate dependency-aware flowcharts.

---

## 🔧 Features

### For Students & Advisors
- **Student Plans**: Generate a personalized academic plan from a catalog year and start term (e.g., Fall 2024).
- **Prerequisite Checking**: Automatically detect and highlight missing or improperly sequenced prerequisites, corequisites, and concurrent prerequisites.
- **Flowchart Generation**: Render academic plans as dependency graphs with color-coded course categories, term clustering, and visual indicators for completion and violations.

### For Faculty
- **Curriculum Definition**: Easily define new curriculum structures using Python—no GUI builder required.
- **Generic Plans**: Assign default term-by-term layouts for catalog years.
- **Extensibility**: Add metadata like full course names, notes, and categories (Core, Math/Science, GE, ME, Other).

---

## 📁 Project Structure

- `smume/curricula/` – Defines catalog year curricula (e.g. `_2024_25.py`)
- `smume/generic_plans/` – Maps courses to default terms
- `smume/student_plan.py` – Logic for student-specific academic planning
- `smume/graph_builder.py` – Graphviz-based flowchart generation

---

## 📌 Notes

- Term formats are flexible: both `Fall` and `F`, and `2025` or `25` are valid.
- Curriculum and plan objects are fully programmable—ideal for integration into other workflows or GUIs.
- Graphs highlight completed courses (gray, checkmarks), unmet dependencies (red), and visually group courses by academic term.

---

## 📚 Example

<img src="img/2024-25.svg" width="100%" />

---

## 👥 Who It's For

- **Students**: Visualize and adjust your academic plan semester by semester.
- **Advisors**: Confirm course sequencing and verify prerequisite compliance.
- **Faculty**: Define and revise curriculum plans in code with minimal friction.

---

## 🛠️ Future Work

- Web frontend
- Support for electives and transfer credit
- Improved drag-and-drop UI for plan adjustment

---

## 🚀 Quick Start

Install the package with pip:

```bash
pip install smume
```

For development:

```bash
git clone https://github.com/YOUR_USERNAME/smu-curriculum-flowcharts.git
cd smu-curriculum-flowcharts
poetry install
```

Usage examples:

```bash
# Clone and install
poetry install

# Example: generate a graph for the 2024–25 curriculum
poetry run python scripts/generate_generic_graph.py 2024-25

# Example: create and render a student plan
poetry run python scripts/generate_student_graph.py 2024-25 --start-year 2024 --start-term Fall
```

---

MIT Licensed · Developed by Dr. Rico Picone and collaborators
