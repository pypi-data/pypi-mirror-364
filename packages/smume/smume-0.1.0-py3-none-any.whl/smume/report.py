class Report:
    def __init__(self, plan):
        self.plan = plan
        self.title = "Plan Report"
        self.styles = {}  # optional: for future styling options
        self.include_categories = None  # optional filter

    def generate_html(self):
        """Generate a structured HTML report of courses by category hierarchy."""
        def all_courses_completed(data):
            for key, value in data.items():
                if hasattr(value, 'name'):
                    if not getattr(value, 'completed', False):
                        return False
                else:
                    if not all_courses_completed(value):
                        return False
            return True

        def render_hierarchy(level, data):
            html = ['<ul>']
            category_order = self.plan.curriculum.category_order
            category_names = self.plan.curriculum.category_names

            def fmt_percent(value):
                return f"{value:.0%}" if value is not None else None

            # First, collect and render all courses
            course_items = []
            category_items = []
            for key, value in sorted(data.items(), key=lambda item: category_order.get(item[0], 999)):
                if hasattr(value, 'name'):
                    course_items.append((key, value))
                else:
                    category_items.append((key, value))

            for key, value in course_items:
                title = f"{value.name}: {value.full_name}" if getattr(value, "full_name", None) else value.name
                css_class = "course-item" + (" course-completed" if getattr(value, 'completed', False) else "")
                html.append(f'<li class="{css_class}">{title} ({value.credits})</li>')

            for key, value in category_items:
                cat_name = category_names.get(key, key)
                status = self.plan.category_requirement_status(key)
                completed = all_courses_completed(value)
                status_text = ""

                if status is not None:
                    if status and completed:
                        status_text = " (complete)"
                    elif status and not completed:
                        planned_fraction = self.plan.fraction_of_category_satisfied(key, completed_only=False)
                        completed_fraction = self.plan.fraction_of_category_satisfied(key, completed_only=True)
                        if planned_fraction is None and completed_fraction is None:
                            status_text = ""
                        elif planned_fraction is None:
                            status_text = f" (Completed: {fmt_percent(completed_fraction)})"
                        elif completed_fraction is None:
                            status_text = f" (Planned: {fmt_percent(planned_fraction)})"
                        else:
                            status_text = f" (Planned: {fmt_percent(planned_fraction)}, Completed: {fmt_percent(completed_fraction)})"
                    elif not status:
                        unsatisfied_info = getattr(self.plan, 'category_requirement_unsatisfied_info', lambda k: "")(key)
                        status_text = f" (not satisfied{': ' + unsatisfied_info if unsatisfied_info else ''})"

                html.append(f'<li class="category-group">{cat_name}{status_text}{render_hierarchy(level + 1, value)}</li>')

            html.append('</ul>')
            return "\n".join(html)

        html = ['<div class="report">']
        html.append(f'<h2>{self.title}</h2>')
        html.append('<h3>1. Notes</h3>\n\n<ul>')
        for note in self.plan.notes:
            html.append(f'<li>{note["timestamp"]}: {note["text"]}</li>')
        html.append('</ul>')
        html.append('<h3>2. Courses by Category</h3>')
        rendered = render_hierarchy(0, self.hierarchy)
        if rendered.startswith('<ul>') and rendered.endswith('</ul>'):
            rendered = rendered[len('<ul>'):-len('</ul>')]
        html.append('<ul class="report-columns">')
        html.append(rendered)
        html.append('</ul>')
        html.append('</div>')
        return "\n".join(html)
    
    def generate_text(self):
        """Generate a hierarchical text report of courses by category."""
        lines = [self.title, "=" * len(self.title)]
        
        def all_courses_completed(data):
            for key, value in data.items():
                if hasattr(value, 'name'):
                    if not getattr(value, 'completed', False):
                        return False
                else:
                    if not all_courses_completed(value):
                        return False
            return True

        def render_hierarchy(level, data):
            indent = "  " * level
            category_order = self.plan.curriculum.category_order
            category_names = self.plan.curriculum.category_names
            # First, collect courses and categories
            course_items = []
            category_items = []
            for key, value in sorted(data.items(), key=lambda item: category_order.get(item[0], 999)):
                if hasattr(value, 'name'):
                    course_items.append((key, value))
                else:
                    category_items.append((key, value))

            for key, value in course_items:
                title = f"{value.name}: {value.full_name}" if getattr(value, "full_name", None) else value.name
                completed_mark = " ✓" if getattr(value, 'completed', False) else ""
                lines.append(f"{indent}- {completed_mark} {title} ({value.credits})")

            for key, value in category_items:
                cat_name = category_names.get(key, key)
                status = self.plan.category_requirement_status(key)
                completed = all_courses_completed(value)
                status_text = ""
                if status is not None:
                    if status and completed:
                        status_text = " (Complete)"
                    elif status and not completed:
                        planned_fraction = self.plan.fraction_of_category_satisfied(key, completed_only=False)
                        completed_fraction = self.plan.fraction_of_category_satisfied(key, completed_only=True)
                        if planned_fraction is None and completed_fraction is None:
                            status_text = ""
                        elif planned_fraction is None:
                            status_text = f" (Completed: {completed_fraction:.0%})"
                        elif completed_fraction is None:
                            status_text = f" (Planned: {planned_fraction:.0%})"
                        else:
                            status_text = f" (Planned: {planned_fraction:.0%}, Completed: {completed_fraction:.0%})"
                    elif not status:
                        unsatisfied_info = getattr(self.plan, 'category_requirement_unsatisfied_info', lambda k: "")(key)
                        status_text = f" (not satisfied{': ' + unsatisfied_info if unsatisfied_info else ''})"
                lines.append(f"{indent}{cat_name}{status_text}:")
                render_hierarchy(level + 1, value)

        render_hierarchy(0, self.hierarchy)
        return "\n".join(lines)
    
    @property
    def hierarchy(self):
        """
        Return a hierarchical structure of courses by category.
        Items without categories are at the top level.
        Items with just one category are grouped under that category at the second level.
        Items with two categories are grouped under both categories at the third level. Etc.
        If `include_categories` is set, only those categories are included.
        """
        hierarchy = {}
        for course in self.plan.courses:
            if self.include_categories and not any(cat in self.include_categories for cat in course.categories):
                continue
            current_level = hierarchy
            for cat in course.categories:
                if cat not in current_level:
                    current_level[cat] = {}
                current_level = current_level[cat]
            current_level[course.name] = course
        return hierarchy
    
    def save(self, filepath):
        """Save the report to the given filepath based on file extension."""
        content = self.generate_html() if filepath.endswith(".html") else self.generate_text()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def css_styles(self):
        """Return CSS styles for the report, including print formatting."""
        return """
        <style>
            body { font-family: Palatino, serif; }
            .report { margin: 20px; }
            .category-group { font-weight: bold; }
            .course-item { margin-left: 20px; font-weight: normal; }
            .course-completed::before { content: "✓ "; }

            ul.report-columns {
                column-count: 2;
                column-gap: 40px;
            }
        </style>
        """