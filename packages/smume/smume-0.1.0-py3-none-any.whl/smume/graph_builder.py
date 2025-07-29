# graph_builder.py

from graphviz import Digraph
from smume.utils import term_sort_key

def build_graph(plan, output_path=None, format="png"):
    graph = Digraph(format=format, engine='dot')
    graph.attr(rankdir='LR', newrank='true', compound='true', fontname='Palatino', fontsize='12')

    # Group courses by term
    courses_by_term = {}
    for course in plan.courses:
        if course.term:
            courses_by_term.setdefault(course.term, []).append(course)

    # Define category colors
    category_colors = {
        'C': '#f6e8c3',   # Core
        'MS': '#d5e8d4',  # Math and Science
        'GE': '#dae8fc',  # General Engineering
        'ME': '#f8cecc',  # Mechanical Engineering
        'O': '#e1d5e7',   # Other
    }

    # Define edge color palette (distinct, non-yellowish for clarity)
    edge_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#808000", "#17becf",
        "#393b79", "#637939", "#614100", "#843c39", "#7b4173",
        "#5254a3", "#6b6ecf", "#9c9ede", "#3182bd", "#31a354"
    ]

    sorted_terms = sorted(courses_by_term.keys(), key=term_sort_key)
    term_cluster_ids = []

    # Check for dependency violations if method exists
    violations = plan.check_dependencies() if hasattr(plan, 'check_dependencies') else {}

    # Create a subgraph for each term
    for idx, term in enumerate(sorted_terms):
        cluster_name = f"cluster_{idx}"
        sub = Digraph(name=cluster_name)
        if type(plan).__name__ == 'StudentPlan':
            term_label = f""
        else:
            term_label = f"Term: "
        sub.attr(rank='same', style='filled', color='#cecdc9',
                 label=f"<<B>{term_label}{term}</B><BR/><FONT POINT-SIZE=\"10\" COLOR=\"#6e6d6a\">{sum(c.credits for c in courses_by_term[term])} cr</FONT>>")

        for course in courses_by_term[term]:
            if course.completed:
                fill_color = '#cecdc9'
            else:
                category_for_color = next((c for c in course.categories if c in category_colors), None)
                fill_color = category_colors.get(category_for_color, '#ffffff')
            label_text = f"{course.name}<font color=\"#6e6d6a\"><sub>  {course.credits} cr</sub></font>"
            if course.completed:
                label_text = f"✓ {label_text}"
            style_attrs = {
                'label': f"<{label_text}>",
                'style': 'filled',
                'fillcolor': fill_color,
                'shape': 'box',
                'fontsize': '10',
                'tooltip': getattr(course, 'note', ''),
            }
            is_violation_node = course.name in violations or any(
                course.name in deps
                for v in violations.values()
                for deps in [v.get('prereq', []) + v.get('coreq', []) + v.get('coprereq', [])]
            )
            if is_violation_node:
                style_attrs['color'] = 'red'
                style_attrs['penwidth'] = '3'
            style_attrs.update(course.styles)
            sub.node(course.name, **style_attrs)

        graph.subgraph(sub)
        term_cluster_ids.append((term, cluster_name))

    # Add invisible edges to control horizontal layout between clusters
    for i in range(1, len(term_cluster_ids)):
        prev_term, prev_cluster = term_cluster_ids[i - 1]
        curr_term, curr_cluster = term_cluster_ids[i]
        prev_courses = courses_by_term[prev_term]
        curr_courses = courses_by_term[curr_term]
        if prev_courses and curr_courses:
            graph.edge(prev_courses[0].name, curr_courses[0].name,
                       style='invis', ltail=prev_cluster, lhead=curr_cluster)

    # Add dependency edges with unique colors
    color_index = 0
    for course in plan.courses:
        for prereq in course.prereqs:
            edge_color = edge_colors[color_index % len(edge_colors)]
            color_index += 1
            completed = next((c for c in plan.courses if c.name == prereq and c.completed), None)
            is_violation = (
                course.name in violations
                and prereq in violations[course.name].get('prereq', [])
            )
            if is_violation:
                for node_name in [course.name, prereq]:
                    graph.node(node_name, color='red', penwidth='3')
            graph.edge(
                prereq, course.name,
                color='red' if is_violation else ('#aaaaaa' if completed else edge_color),
                style='solid',
                minlen='2',
                labelfloat='true'
            )
        for coreq in course.coreqs:
            edge_color = edge_colors[color_index % len(edge_colors)]
            color_index += 1
            completed = next((c for c in plan.courses if c.name == coreq and c.completed), None)
            is_violation = (
                course.name in violations
                and coreq in violations[course.name].get('coreq', [])
            )
            if is_violation:
                for node_name in [course.name, coreq]:
                    graph.node(node_name, color='red', penwidth='3')
            graph.edge(
                coreq, course.name,
                color='red' if is_violation else ('#aaaaaa' if completed else edge_color),
                style='bold',
                dir='both',
                minlen='2',
                labelfloat='true'
            )
        for coprereq in course.coprereqs:
            edge_color = edge_colors[color_index % len(edge_colors)]
            color_index += 1
            completed = next((c for c in plan.courses if c.name == coprereq and c.completed), None)
            is_violation = (
                course.name in violations
                and coprereq in violations[course.name].get('coprereq', [])
            )
            if is_violation:
                for node_name in [course.name, coprereq]:
                    graph.node(node_name, color='red', penwidth='3')
            graph.edge(
                coprereq, course.name,
                color='red' if is_violation else ('#aaaaaa' if completed else edge_color),
                style='dashed',
                minlen='2',
                labelfloat='true'
            )

    # Add legend as a subgraph using positioned nodes and edges
    legend = Digraph(name="cluster_legend")
    # small rank sep to keep legend compact
    legend.attr(label="Legend", fontsize="12", fontname="Palatino", style="dashed", color="#cecdc9", margin="0.2,0.2,0.2,0.2", ranksep="0.04", nodesep="0.0")

    # Create horizontally arranged edge-label pairs with reduced spacing

    legend.node('pr_edge', '', shape='point', width='0.2', height='0.2', margin='0', style='invis')
    legend.node('pr_label', 'prerequisite', shape='plaintext')
    legend.edge('pr_edge', 'pr_label', style='solid', color='black', minlen='2')

    legend.node('copr_edge', '', shape='point', width='0.2', height='0.2', margin='0', style='invis')
    legend.node('copr_label', 'con-prerequisite', shape='plaintext')
    legend.edge('copr_edge', 'copr_label', style='dashed', color='black', minlen='2')

    legend.node('cr_edge', '', shape='point', width='0.2', height='0.2', margin='0', style='invis')
    legend.node('cr_label', 'corequisite', shape='plaintext')
    legend.edge('cr_edge', 'cr_label', style='bold', color='black', dir='both', minlen='2') 

    # Force alignment: all edges on same rank, all labels on same rank
    same_rank_edges = Digraph()
    same_rank_edges.attr(rank='same', margin='.2', ranksep="0.08", nodesep="0.08")
    same_rank_edges.node('pr_edge')
    same_rank_edges.node('cr_edge')
    same_rank_edges.node('copr_edge')
    legend.subgraph(same_rank_edges)

    same_rank_labels = Digraph()
    same_rank_labels.attr(rank='same', margin='.2', ranksep="0.08", nodesep="0.08")
    same_rank_labels.node('pr_label')
    same_rank_labels.node('cr_label')
    same_rank_labels.node('copr_label')
    legend.subgraph(same_rank_labels)

    # Add an invisible edge to pull the legend toward bottom right
    if plan.courses:
        last_course = list(plan.courses)[-1]
        graph.edge(last_course.name, 'pr_edge', style='invis')
    graph.subgraph(legend)

    if output_path:
        graph.render(filename=output_path, format=format, cleanup=True)
    return graph