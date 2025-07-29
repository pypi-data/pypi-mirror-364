import re
from smume.generic_plan import GenericPlan

class StudentPlan(GenericPlan):
    """
    A student-specific plan that extends a catalog-based GenericPlan with
    specific academic years and term overrides.
    """

    def __init__(self, catalog: str, start_year: int, start_term: str = "Fall", student_name: str = None, student_id: str = None):
        super().__init__(catalog)
        self.start_year = start_year
        self.start_term = start_term  # "Fall" or "Spring"
        self.student_course_terms = {}
        self._assign_specific_terms()
        self.student_name = student_name or "Student"
        self.student_id = None  # Optional student ID, needed for parsing unofficial transcripts
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

    def parse_html_transcript(self, file_path: str):
        """
        Parses an HTML transcript file and extracts course information.
        :param file_path: Path to the HTML transcript file.
        """
        from bs4 import BeautifulSoup
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        rows = soup.find_all("tr")

        current_term = None

        for row in rows:
            # Check if row is an h2 tag by looking for h2 elements in its children
            h2_tag = row.find_previous_sibling("h2")
            if h2_tag is not None:
                current_term = h2_tag.get_text(strip=True)

            cells = row.find_all("td")
            if len(cells) >= 6:
                course_name = cells[0].get_text(strip=True)
                title = cells[1].get_text(strip=True)
                letter_grade = cells[3].get_text(strip=True)
                credits = cells[4].get_text(strip=True)
                quality_points = cells[5].get_text(strip=True)

                # If credits and quality points don't parse to floats, discard the row
                if not (credits.replace('.', '', 1).isdigit() and quality_points.replace('.', '', 1).isdigit()):
                    continue

                print(f"Parsing course: {course_name}, Title: {title}, Grade: {letter_grade}, Credits: {credits}, Quality Points: {quality_points}")

                # Normalize course name (some transcripts may have variations like "COR100" instead of "COR 100" or "ME100" instead of "ME 100"). We may need to split after the letters prefix.
                course_name = re.sub(r'(\D+)(\d+)', r'\1 \2', course_name)  # Add space between letters and numbers
                course_name = re.sub(r'\s+', ' ', course_name)  # Normalize multiple spaces
                course_name = course_name.strip().upper()
                if course_name in self.curriculum.courses:
                    course = self.curriculum.courses[course_name]
                else:
                    # Add course with category Other
                    self.curriculum.course(course_name, credits=float(credits) if credits else 0.0, categories=["O"])
                    course = self.curriculum.courses[course_name]
                course.letter_grade = letter_grade
                course.grade = float(quality_points) / float(credits) if float(credits) > 0 else 0
                course.title = title
                course.credits = int(float(credits)) if credits else 0
                course.quality_points = float(quality_points) if quality_points else 0.0
                if course.letter_grade not in ["F", "", "W", "IP", "AU", "I", "NC"]:
                    print(f"  Marking course {course_name} as completed.")
                    course.set_completed(True)

                if current_term:
                    # Attempt to parse year and semester from current_term
                    # Expecting something like "Fall 2023" or "Spring 2024"
                    match = re.match(r"(Fall|Spring|Summer|Su1|Su2|Su)\s*(\d{2,4})", current_term, re.IGNORECASE)
                    if match:
                        semester_raw = match.group(1)
                        year_raw = match.group(2)
                        try:
                            term_label = self._normalize_term_label(year_raw, semester_raw)
                            self.student_course_terms[course_name] = term_label
                            self.set_term(course_name, term_label)
                        except Exception:
                            # Ignore term parsing errors
                            pass