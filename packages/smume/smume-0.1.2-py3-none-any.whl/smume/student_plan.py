import re
from smume.generic_plan import GenericPlan

class StudentPlan(GenericPlan):
    """
    A student-specific plan that extends a catalog-based GenericPlan with
    specific academic years and term overrides.
    """

    def __init__(self, catalog: str, start_year: int, start_term: str = "Fall", student_name: str = None, student_id: str = None, DTA: str = None):
        super().__init__(catalog)
        self.start_year = start_year
        self.start_term = start_term  # "Fall" or "Spring"
        self.student_course_terms = {}
        self._assign_specific_terms()
        self.student_name = student_name or "Student"
        self.student_id = student_id  # Optional student ID, needed for parsing unofficial transcripts
        self._DTA = DTA
        self.notes = []  # Store student-specific notes
    
    @property
    def DTA(self):
        """
        Returns the DTA status of the student plan.
        If DTA is set, it returns the DTA type (e.g., "AA-DTA", "AS-DTA").
        Otherwise, returns None.
        """
        return self._DTA
    
    @DTA.setter
    def DTA(self, value):
        """
        Sets the DTA status of the student plan.
        Accepts "AA-DTA" or "AS-DTA" to indicate the type of DTA.
        """
        if value not in ["AA-DTA", "AS-DTA"]:
            raise ValueError("DTA must be 'AA-DTA' or 'AS-DTA'")
        self._DTA = value
        # Exempt the student via DTA
        self.exempt_DTA()

    def exempt_DTA(self):
        """
        Exempts the student from DTA requirements.
        """
        if self._DTA:
            print(f"Exempting student from {self._DTA} requirements.")
            # If DTA is set, mark all DTA courses as completed. Check also for W versions of exempted courses.
            w_versions = [course_name + "W" for course_name in self.curriculum.DTA_exemptions.get(self._DTA, [])]
            for course_name in self.curriculum.DTA_exemptions.get(self._DTA, []) + w_versions:
                if course_name in self.curriculum.courses:
                    # If there is a W writing intensive version, switch it to the non-W version ... I don't think this is necessary
                    # if course_name.endswith("W"):
                    #     term = self.student_course_terms.get(course_name, None) # Get the term of the W version
                    #     if term is None:
                    #         continue
                    #     term = self.extract_year_and_semester(term) if term else None
                    #     self.remove_course_term(course_name)  # Remove the W version
                    #     course_name = course_name[:-1] # Remove the 'W'
                    #     self.set_course_term(course_name, term.year, term.semester)  # Add the non-W version back to the plan
                    # If the course is not already completed, mark it as completed
                    # Mark the course as completed
                    course = self.curriculum.courses[course_name]
                    course.set_completed(True)
                    print(f"  Marking {course_name} as completed due to DTA exemption.")
        else:
            print("No DTA requirements found to exempt.")
    
    def extract_year_and_semester(self, term_label):
        """
        Extracts the year and semester from a term label like '2025-F' or '2024-S'.
        Returns a tuple (year, semester).
        """
        match = re.match(r"(\d{4})-(\w+)", term_label)
        if match:
            year = int(match.group(1))
            semester = match.group(2)
            return year, semester
        else:
            raise ValueError(f"Invalid term label format: {term_label}")

    def set_course_term(self, course_name: str, year, semester):
        """
        Assigns a specific normalized term label like '2025-F' to the course.
        """
        term_label = self._normalize_term_label(year, semester)
        self.student_course_terms[course_name] = term_label
        self.set_term(course_name, term_label)

    def remove_course_term(self, course_name: str):
        """
        Removes the term assignment for a course, effectively removing it from the plan.
        """
        self.student_course_terms.pop(course_name, None)
        if course_name in self.curriculum.courses:
            self.curriculum.courses[course_name].term = None
        else:
            print(f"Course {course_name} not found in curriculum, cannot remove term assignment.")

    def _normalize_term_label(self, year, semester):
        """
        Normalize year and semester into a term label like '2025-F'.
        Accepts 2- or 4-digit years and maps full season names to abbreviations.
        """
        if isinstance(year, int):
            if year == 0:
                year = "0000"  # Special case for transfer terms
            else:
                if year < 100:  # Handle 2-digit years
                    year += 2000
                year = str(year)
        elif isinstance(year, str):
            if year == "0000":
                year = "0000"
            else:
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
            "Su2": "Su2", "Summer2": "Su2",
            "Transfer": "Transfer"
        }

        sem = season_map.get(semester)
        if sem is None:
            raise ValueError(f"Invalid semester/season: {semester}. Must be one of: F, S, Su, Su1, Su2, Transfer.")

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
            # Find the current term from the previous h2 tag
            h2_tag = row.find_previous("h2")
            if h2_tag is not None:
                current_term = h2_tag.get_text(strip=True)

            cells = row.find_all("td")
            if len(cells) >= 6:
                course_name = cells[0].get_text(strip=True)
                title = cells[1].get_text(strip=True)
                letter_grade = cells[3].get_text(strip=True)
                credits = cells[4].get_text(strip=True)
                quality_points = cells[5].get_text(strip=True)

                # Filter: If credits and quality points don't parse to floats, discard the row
                if not (credits.replace('.', '', 1).isdigit() and quality_points.replace('.', '', 1).isdigit()):
                    continue

                # Filter: If course name contains ["TERM", "OVERALL"], discard the row
                if any(term.lower() in course_name.lower() for term in ["TERM", "OVERALL"]):
                    continue

                # Normalize course name (some transcripts may have variations like "COR100" instead of "COR 100" or "ME100" instead of "ME 100"). We may need to split after the letters prefix.
                course_name = re.sub(r'(\D+)(\d+)', r'\1 \2', course_name)  # Add space between letters and numbers
                course_name = re.sub(r'\s+', ' ', course_name)  # Normalize multiple spaces
                course_name = course_name.strip().upper()
                if course_name in self.curriculum.courses:
                    course = self.curriculum.courses[course_name]
                else:
                    # Check if it's actually a DTA, not a course at all
                    if "AA-DTA" in course_name:
                        self.DTA = "AA-DTA"
                        print(f"  Detected DTA: {self.DTA}")
                        continue
                    if "AS-DTA" in course_name:
                        self.DTA = "AS-DTA"
                        print(f"  Detected DTA: {self.DTA}")
                        continue
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
                    # Expecting something like "2023 Fall" or "2024 Spring" or "0000 Transfer" 
                    match = re.match(r"(\d{4})\s*(Fall|Spring|Summer|Su1|Su2|Su|Transfer)", current_term, re.IGNORECASE)
                    print(f"  Current term match parts: {match.groups() if match else None}")
                    if match:
                        # Handle transfer terms. Change the start_year to 0000
                        if match.group(2).lower() == "transfer":
                            self.start_year = 0
                            self.start_term = "Transfer"
                        year_raw = match.group(1)
                        semester_raw = match.group(2)
                        print(f"  Setting term for {course_name} to semester {semester_raw} of year {year_raw}.")
                        try:
                            term_label = self._normalize_term_label(year_raw, semester_raw)
                            self.student_course_terms[course_name] = term_label
                            self.set_term(course_name, term_label)
                        except Exception as e:
                            print(f"  Error setting term for {course_name}: {e}")
                            pass