from smume.generic_plan import GenericPlan

class StudentPlan(GenericPlan):
    """
    A student-specific plan that extends a catalog-based GenericPlan with
    specific academic years and term overrides.
    """

    def __init__(self, catalog: str, start_year: int, start_term: str = "Fall", student_name: str = None):
        super().__init__(catalog)
        self.start_year = start_year
        self.start_term = start_term  # "Fall" or "Spring"
        self.student_course_terms = {}
        self._assign_specific_terms()
        self.student_name = student_name or "Student"
        self.notes = []  # Store student-specific notes

    def set_course_term(self, course_name: str, year, semester):
        """
        Assigns a specific normalized term label like '2025-F' to the course.
        """
        term_label = self._normalize_term_label(year, semester)
        self.student_course_terms[course_name] = term_label
        self.set_term(course_name, term_label)

    def _normalize_term_label(self, year, semester):
        """
        Normalize year and semester into a term label like '2025-F'.
        Accepts 2- or 4-digit years and maps full season names to abbreviations.
        """
        if isinstance(year, int):
            if year < 100:
                year += 2000
            year = str(year)
        elif isinstance(year, str):
            if len(year) == 2 and year.isdigit():
                year = "20" + year
            elif not year.isdigit() or len(year) not in [2, 4]:
                raise ValueError(f"Invalid year format: {year}")
        else:
            raise TypeError("Year must be int or string")

        season_map = {
            "F": "F", "Fall": "F",
            "S": "S", "Spring": "S",
            "Su": "Su", "Summer": "Su",
            "Su1": "Su1", "Summer1": "Su1",
            "Su2": "Su2", "Summer2": "Su2"
        }

        sem = season_map.get(semester)
        if sem is None:
            raise ValueError(f"Invalid semester/season: {semester}. Must be one of: F, S, Su, Su1, Su2.")

        return f"{year}-{sem}"

    def mark_completed(self, course_name: str):
        """
        Marks a course as completed.
        """
        course = self.curriculum.courses[course_name]
        if course:
            course.set_completed(True)
    def _assign_specific_terms(self):
        """
        Converts generic plan term labels like '1F', '2S', etc. into
        specific year-term labels based on student start year and term.
        Only considers S and F terms in a yearly cycle.
        """
        term_order = ["S", "F"]
        start_index = term_order.index(self._normalize_term_label(self.start_year, self.start_term).split("-")[1])
        generic_terms = sorted(t for t in self.courses_by_term().keys() if t is not None)

        year = self.start_year
        season_index = start_index
        for generic_term in generic_terms:
            actual_term = f"{year}-{term_order[season_index]}"
            for course in self.courses_by_term()[generic_term]:
                course_name = course.name
                self.set_term(course_name, actual_term)
                if course_name in self.curriculum.courses:
                    self.curriculum.courses[course_name].term = actual_term
            season_index += 1
            if season_index >= len(term_order):
                season_index = 0
                year += 1

    def add_note(self, note: str, date: str):
        """
        Adds a note to the student plan.
        Notes are specific to the student and not tied to courses or terms.
        :param note: The note text.
        :param date: The date of the note in 'YYYY-MM-DD' format.
        """
        note_structured = {
            "text": note,
            "timestamp": date
        }
        self.notes.append(note_structured)