from smume.course_model import Course
from smume.utils import normalize_categories

class Curriculum:
    """
    Container for a curriculum's set of courses. Defines structure, not term plans.
    """

    def __init__(self, name: str, categories_def: dict = None, ):
        self.name = name
        self.courses = {}
        self.define_categories(categories_def or {})
        self.category_requirements = {}
        self.explicit_category_requirements = {}
        self.implicit_category_requirements = {}
        self.update_implicit_category_requirements()
        self.merge_category_requirements()

    def course(self, name, credits, categories=None, **kwargs):
        """
        Creates and registers a course in the curriculum.
        Does not set term or completion status.
        """
        categories = normalize_categories(categories, valid_categories=self.valid_categories)
        course = Course(name, credits, categories=categories, **kwargs)
        self.courses[name] = course
        return course
    
    def define_categories(self, categories_def: dict):
        """
        Defines the categories used in this curriculum.
        Categories are a dictionary mapping category names to their full names.
        """
        self.categories = categories_def.keys() or []
        self.category_names = {cat: category["name"] for cat, category in categories_def.items()}
        self.category_order = {category["name"]: category["order"] for category in categories_def.values()}
        self.valid_categories = {cat: cat for cat in self.categories}
        valid_aliases = {alias: cat for cat, aliases in categories_def.items() for alias in aliases}
        self.valid_categories.update(valid_aliases)

    def category_requirement(self, category: str, kind: str, number: int = None, note: str = None):
        """
        Defines a category requirement for the curriculum.
        """
        # Update explicit requirements
        if category not in self.explicit_category_requirements:
            self.explicit_category_requirements[category] = []
        self.explicit_category_requirements[category].append({
            "kind": kind,
            "number": number,
            "note": note
        })
        self.update_implicit_category_requirements() # Update implicit requirements
        self.merge_category_requirements()  # Merge explicit and implicit requirements
        return self

    def update_implicit_category_requirements(self):
        """
        Updates the implicit category requirements based on courses.
        If a category has no explicit Number of Credits requirements, we assume that all credits in that category must be completed.
        """
        implicit_reqs = {}
        for category in self.categories:
            explicit_requirements = self.explicit_category_requirements.get(category, [])
            if not any(req["kind"] == "Number of Credits" for req in explicit_requirements):
                # If no explicit Number of Credits requirements, assume all courses in category are required
                # However, don't double count credits if course is in multiple categories
                number_of_credits = sum(course.credits for course in self.courses.values() if category in course.categories)
                implicit_reqs[category] = {
                    "kind": "Number of Credits",
                    "number": number_of_credits,
                    "note": f"All courses in {category} category must be completed"
                }
        self.implicit_category_requirements = implicit_reqs
        return self.implicit_category_requirements

    def merge_category_requirements(self):
        """
        Merges explicit and implicit category requirements into a single dictionary (category_requirements).
        """
        merged_requirements = self.explicit_category_requirements.copy()
        for category, implicit_req in self.implicit_category_requirements.items():
            if category not in merged_requirements:
                merged_requirements[category] = []
            merged_requirements[category].append(implicit_req)
        self.category_requirements = merged_requirements
        return self.category_requirements