# course_model.py

class Course:
    """Defines a course with relationships and metadata."""

    def __init__(self, name, credits, term=None, completed=False, critical_path=True, categories=None, full_name=None, note=None, ms_credits=None, writing_intensive=False):
        self.name = name
        self.credits = credits
        self.term = term
        self.completed = completed
        self.critical_path = critical_path
        self.prereqs = []
        self.coreqs = []
        self.coprereqs = []
        self.styles = {}
        self.categories = categories
        self.full_name = full_name or name
        self.note = note
        if self.note is None:
            if self.full_name:
                self.note = f"{self.full_name}"
            else:
                self.note = f"{self.name} ({self.credits} cr)"
        if "MS" in self.categories:
            self.ms_credits = ms_credits if ms_credits is not None else credits
        else:
            self.ms_credits = 0
        self.writing_intensive = writing_intensive

    def add_prereq(self, prereq_name):
        self.prereqs.append(prereq_name)
        return self

    def add_coreq(self, coreq_name):
        self.coreqs.append(coreq_name)
        return self

    def add_coprereq(self, coprereq_name):
        self.coprereqs.append(coprereq_name)
        return self

    def add_style(self, style_key, style_value):
        self.styles[style_key] = style_value
        return self

    def set_completed(self, completed=True):
        self.completed = completed
        return self

def new_course(name, credits, term=None, completed=False, categories=None):
    """Creates and registers a new course."""
    course = Course(name, credits, term, completed, categories)
    return course