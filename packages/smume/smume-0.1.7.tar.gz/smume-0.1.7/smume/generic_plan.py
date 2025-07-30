import re
from smume.utils import term_sort_key, normalize_categories

def catalog_to_module_name(catalog):
    """
    Normalize a human-friendly catalog string to a valid Python module name.
    Examples:
        "ME 2024–25" -> "_2024_25"
        "2024–25"    -> "_2024_25"
        "2024-2025"  -> "_2024_25"
    """
    match = re.search(r"(\d{4})\D+(\d{2,4})", catalog)
    if match:
        start_year, end_year = match.groups()
        end_year = end_year[-2:]  # get last 2 digits
        return f"_{start_year}_{end_year}"
    raise ValueError(f"Unrecognized catalog format: {catalog}")


import importlib

class GenericPlan:
    """
    A plan representing the default recommended sequence for a given catalog year.
    Stores the initial term layout as defined in the curriculum module.
    """

    def __init__(self, catalog):
        if isinstance(catalog, str):
            module_name = catalog_to_module_name(catalog)
            mod = importlib.import_module(f"smume.curricula.{module_name}")
            self.curriculum = mod.curriculum
            self.catalog = catalog
        else:
            self.curriculum = catalog
            self.catalog = str(catalog)
        self.name = self.curriculum.name
        self.notes_generic = []

    @property
    def courses(self):
        """
        Returns all courses with a term assigned.
        This includes courses that are not yet completed.
        """
        return [course for course in self.courses_all if course.term]

    @property
    def courses_all(self):
        """
        Returns all courses in the curriculum.
        """
        return self.curriculum.courses.values()

    @property
    def course_terms(self):
        """
        Returns a mapping of course names to their assigned terms.
        """
        return {
            name: course.term for name, course in self.curriculum.courses.items()
        }

    @property
    def course_categories(self):
        """
        Returns a dictionary mapping category names to lists of courses.
        A course may appear in multiple categories.
        """
        from collections import defaultdict
        category_map = defaultdict(list)
        for course in self.courses:
            for category in course.categories:
                category_map[category].append(course)
        return dict(category_map)

    def get_term(self, course_name):
        return self.course_terms.get(course_name)

    def set_term(self, course_name, term):
        if course_name in self.course_terms:
            self.course_terms[course_name] = term
        if course_name in self.curriculum.courses:
            self.curriculum.courses[course_name].term = term
    
    def add_course(self, course_name, term):
        """
        Adds a course to the plan with a specific term.
        """
        if course_name not in self.curriculum.courses:
            raise ValueError(f"Course '{course_name}' not found in curriculum.")
        
        self.set_term(course_name, term)
    
    def remove_course(self, course_name):
        """
        Removes a course from the plan.
        """
        if course_name not in self.curriculum.courses:
            raise ValueError(f"Course '{course_name}' not found in curriculum.")
        
        self.set_term(course_name, None)
    
    def substitute_course(self, old_name, new_name):
        """
        Substitutes an old course with a new one.
        """
        if old_name not in self.curriculum.courses:
            raise ValueError(f"Course '{old_name}' not found in curriculum.")
        if new_name not in self.curriculum.courses:
            raise ValueError(f"Course '{new_name}' not found in curriculum.")

        old_course = self.curriculum.courses[old_name]
        new_course = self.curriculum.courses[new_name]

        # Copy term and other attributes from the old course
        new_course.term = old_course.term
        new_course.completed = old_course.completed
        new_course.critical_path = old_course.critical_path

        # Remove the old course from the plan
        old_course.term = None

    def switch_writing_intensive(self, old_name, new_name):
        """
        Substitutes one writing intensive course for another and adds the non-writing intensive version of the old course.
        """
        if old_name not in self.curriculum.courses:
            raise ValueError(f"Course '{old_name}' not found in curriculum.")
        if new_name not in self.curriculum.courses:
            raise ValueError(f"Course '{new_name}' not found in curriculum.")

        old_course = self.curriculum.courses[old_name]
        new_course = self.curriculum.courses[new_name]

        # Ensure both courses are writing intensive
        if not old_course.writing_intensive or not new_course.writing_intensive:
            raise ValueError("Both courses must be writing intensive.")

        # Find the non-writing intensive version of the old course
        non_writing_course_name = old_name.replace("W", "")
        if non_writing_course_name not in self.curriculum.courses:
            raise ValueError(f"Non-writing intensive version '{non_writing_course_name}' not found in curriculum.")
        non_writing_course = self.curriculum.courses[non_writing_course_name]

        # Add the non-writing intensive course to the plan by setting its term
        if old_course.term:
            self.set_term(non_writing_course_name, old_course.term)
        else:
            raise ValueError(f"Old course '{old_name}' does not have a term assigned. Cannot set term for non-writing intensive course.")
        
        # Remove the non-writing intensive version of the new course
        non_writing_course_name = new_name.replace("W", "")
        if non_writing_course_name in self.curriculum.courses:
            self.remove_course(non_writing_course_name)

        # Substitute the old course with the new one
        self.substitute_course(old_name, new_name)

    def apply_term_mapping(self, term_map: dict, check: bool = False):
        """
        Updates course terms based on a dictionary like:
        {
            "1F": ["ME 345", "ME 316"],
            "1S": ["ME 392"]
        }
        Only updates terms for the listed courses. Other courses remain unchanged.
        If check=True, returns a dictionary of dependency issues.
        """
        for term, course_list in term_map.items():
            for course_name in course_list:
                self.set_term(course_name, term)

        if check:
            return self.check_dependencies()
    
    def courses_by_term(self):
        grouped = {}
        for course in self.courses:
            grouped.setdefault(course.term, []).append(course)
        return grouped

    def check_dependencies(self):
        """
        Check for unmet prerequisites, corequisites, and coprerequisites
        in the course plan. Returns a dictionary of problems keyed by course name.
        """
        problems = {}

        term_order = sorted(
            {t for t in self.course_terms.values() if t is not None},
            key=term_sort_key
        )
    
        term_index = {term: i for i, term in enumerate(term_order)}

        for course in self.courses:
            course_term = self.course_terms.get(course.name)
            course_index = term_index.get(course_term, -1)

            unmet = {"prereq": [], "coreq": [], "coprereq": []}

            for pre in getattr(course, "prereqs", []):
                pre_term = self.course_terms.get(pre)
                if pre_term is None or term_index.get(pre_term, -1) >= course_index:
                    unmet["prereq"].append(pre)

            for co in getattr(course, "coreqs", []):
                co_term = self.course_terms.get(co)
                if co_term is None or term_index.get(co_term, -1) != course_index:
                    unmet["coreq"].append(co)

            for copre in getattr(course, "coprereqs", []):
                copre_term = self.course_terms.get(copre)
                if copre_term is None or term_index.get(copre_term, -1) > course_index:
                    unmet["coprereq"].append(copre)

            if any(unmet.values()):
                problems[course.name] = unmet

        return problems
    
    def print_dependency_issues(self):
        """
        Print any unmet prerequisites, corequisites, or coprerequisites.
        """
        issues = self.check_dependencies()
        if not issues:
            print("No dependency issues found.")
            return

        for course_name, unmet in issues.items():
            print(f"Course: {course_name}")
            if unmet["prereq"]:
                print(f"  - Unmet Prerequisites: {', '.join(unmet['prereq'])}")
            if unmet["coreq"]:
                print(f"  - Unmet Corequisites: {', '.join(unmet['coreq'])}")
            if unmet["coprereq"]:
                print(f"  - Unmet Coprerequisites: {', '.join(unmet['coprereq'])}")

    def check_category_requirements(self):
        """
        Check if the courses in the plan meet the category requirements defined in the curriculum.
        Returns a dictionary of unmet category requirements.
        """
        unmet_requirements = {}
        checking_methods = {
            "Writing Intensive": self.check_writing_intensive,
            "Number of Courses": self.check_number_of_courses,
            "Number of Credits": self.check_number_of_credits,
        }
        for category, requirements in self.curriculum.category_requirements.items():
            for requirement in requirements:
                # Call the appropriate checking method
                if "kind" not in requirement:
                    unmet_requirements[category] = "Missing 'kind' in requirement"
                    continue
                if requirement["kind"] not in checking_methods:
                    unmet_requirements[category] = f"Unknown requirement kind: {requirement['kind']}"
                    continue
                # Call the checking method for this requirement kind
                check_method = checking_methods[requirement["kind"]]
                result = check_method(requirement, category)
                if result:
                    if category not in unmet_requirements:
                        unmet_requirements[category] = {}
                    unmet_requirements[category][requirement.get("note", "No note")] = result
        return unmet_requirements
    
    def check_writing_intensive(self, requirement: dict, category: str, completed_only: bool = False):
        """
        Check if the plan meets the writing intensive requirements for a given category.
        """
        if completed_only:
            writing_courses = [c for c in self.courses if c.writing_intensive and c.completed and category in normalize_categories(c.categories, self.curriculum.valid_categories)]
        else:
            writing_courses = [c for c in self.courses if c.writing_intensive and category in normalize_categories(c.categories, self.curriculum.valid_categories)]
        if len(writing_courses) < requirement.get("number", 1):
            return f"At least {requirement['number']} writing intensive course(s) required in {category}."
        return None

    def check_number_of_courses(self, requirement: dict, category: str, completed_only: bool = False):
        """
        Check if the plan meets the number of courses required for a given category.
        """
        if completed_only:
            courses_in_category = [c for c in self.courses if c.completed and category in c.categories]
        else:
            courses_in_category = [c for c in self.courses if category in c.categories]
        if len(courses_in_category) < requirement.get("number", 1):
            return f"At least {requirement['number']} course(s) required in {category}."
        return None

    def check_number_of_credits(self, requirement: dict, category: str, completed_only: bool = False):
        """
        Check if the plan meets the number of credits required for a given category.
        """
        if completed_only:
            credits_in_category = sum(c.credits for c in self.courses if c.completed and category in c.categories)
        else:
            credits_in_category = sum(c.credits for c in self.courses if category in c.categories)
        if credits_in_category < requirement.get("number", 3):
            return f"At least {requirement['number']} credits required in {category}."
        return None
    
    def print_category_requirement_issues(self):
        """
        Print any unmet category requirements.
        """
        issues = self.check_category_requirements()
        if not issues:
            print("All category requirements met.")
            return

        for category, issue in issues.items():
            print(f"Category: {category}")
            for note, message in issue.items():
                print(f"  - Issue: {note}. {message}")
        print("Please review the curriculum for unmet category requirements.")
        return issues
    
    def category_requirement_status(self, category, completed_only=False):
        """
        Checks if the plan meets the category requirement for a given category.
        Returns True if the requirement is satisfied, a message if not.
        If completed_only is True, only considers completed courses.
        """
        if category not in self.curriculum.category_requirements:
            return None
        
        requirements = self.curriculum.category_requirements[category]

        for requirement in requirements:
            if "kind" not in requirement:
                return f"Missing requirement 'kind' for category '{category}'."
            if requirement["kind"] == "Writing Intensive":
                result = self.check_writing_intensive(requirement, category)
            elif requirement["kind"] == "Number of Courses":
                result = self.check_number_of_courses(requirement, category)
            elif requirement["kind"] == "Number of Credits":
                result = self.check_number_of_credits(requirement, category)
            else:
                return False
            
            if result:
                return result
        
        return True
    
    def fraction_of_category_satisfied(self, category, requirement_kind="Number of Credits", completed_only=False):
        """
        Returns the fraction of the category requirement that has been satisfied.
        For "Number of Courses", returns the fraction of courses completed.
        For "Number of Credits", returns the fraction of credits completed.
        For completed_only=True, only considers completed courses (fraction completed).
        For completed_only=False, considers all courses in the category (fraction planned).
        """
        if category not in self.curriculum.category_requirements:
            print(f"Category '{category}' not found in curriculum.")
            return None
        
        requirements = self.curriculum.category_requirements[category]
        total_required = 0
        total_completed = 0
        total_planned = 0

        for requirement in requirements:
            if requirement["kind"] == requirement_kind:
                if requirement_kind == "Number of Courses":
                    total_required += requirement.get("number", 1)
                    total_completed += len([c for c in self.courses if category in c.categories and c.completed])
                    total_planned += len([c for c in self.courses if category in c.categories])
                elif requirement_kind == "Number of Credits":
                    total_required += requirement.get("number")
                    total_planned += sum(c.credits for c in self.courses if category in c.categories)
                    total_completed += sum(c.credits for c in self.courses if category in c.categories and c.completed)

        if total_required == 0:
            return None
        
        if completed_only:
            return total_completed / total_required
        else:
            return total_planned / total_required
        
    def add_generic_note(self, note):
        """
        Adds a note to the generic plan.
        Notes are not tied to specific courses or terms.
        """
        self.notes_generic.append(note)