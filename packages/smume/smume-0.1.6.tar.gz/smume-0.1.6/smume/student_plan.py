import re
from smume.generic_plan import GenericPlan
import datetime

class StudentPlan(GenericPlan):
    """
    A student-specific plan that extends a catalog-based GenericPlan with
    specific academic years and term overrides.
    """

    def __init__(self, catalog: str, start_year: int, start_semester: str = "Fall", student_name: str = None, student_id: str = None, DTA: str = None):
        super().__init__(catalog)
        self.start_year = start_year
        self.start_semester = start_semester  # "Fall" or "Spring"
        self.term_now = self.get_term_now()
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
                    #     term = self.courses_by_term.get(course_name, None) # Get the term of the W version
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
                    self.set_term(course_name, "0000-Transfer")
                    print(f"  Marking {course_name} as completed due to DTA exemption.")
        else:
            print("No DTA requirements found to exempt.")
    
    def get_term_now(self):
        """
        Returns the current academic term as a normalized term label.
        """
        now = datetime.datetime.now()
        year = now.year
        # Fall is August to December, Spring is January to May, Summer is June to July
        semester = "F" if now.month in [8, 9, 10, 11, 12] else "S" if now.month in [1, 2, 3, 4, 5] else "Su"
        return self._normalize_term_label(year, semester)
    
    def set_term_now(self, term_now: str):
        """
        Sets the current term to a specific normalized term label.
        """
        if not re.match(r"^\d{4}-(F|S|Su|Transfer)$", term_now):
            raise ValueError(f"Invalid term format: {term_now}. Expected format is 'YYYY-F', 'YYYY-S', 'YYYY-Su', or 'YYYY-Transfer'.")
        self.term_now = term_now

    def move_unfinished_courses_forward(self):
        """
        Moves unfinished courses from planned terms past to the upcoming term (relative to the current term).
        """
        print(f"Moving unfinished courses from past terms to the next term after {self.term_now}.")
        current_year, current_semester = self.extract_year_and_semester(self.term_now)
        for course_name, course in self.curriculum.courses.items():
            if course.term is not None:
                if not course.completed:
                    term = course.term
                    if self.is_term_past(term):
                        # Move to the term after the current term
                        next_term = self.get_term_after(self.get_term_now())
                        next_year, next_semester = self.extract_year_and_semester(next_term)
                        self.set_course_term(course.name, next_year, next_semester)
                        print(f"Moved {course.name} from {term} to {next_term}.")

    def is_term_past(self, term_label: str):
        """
        Checks if the given term label is in the past compared to the current term.
        """
        current_year, current_semester = self.extract_year_and_semester(self.term_now)
        term_year, term_semester = self.extract_year_and_semester(term_label)
        if term_year < current_year:
            return True
        semester_order =  ["S", "Su", "Su1", "Su2", "F"]
        if term_year == current_year and semester_order.index(term_semester) < semester_order.index(current_semester):
            return True
        return False
    
    def get_term_after(self, term_label: str, skip_summer=True, skip_half_terms=True):
        """
        Gets the term label for the term after the given term.
        """
        year, semester = self.extract_year_and_semester(term_label)
        all_semesters = ["S", "Su", "Su1", "Su2", "F"]
        if skip_summer:
            semester_order = ["S", "F"]
        elif skip_half_terms:
            semester_order = ["S", "Su", "F"]
        else:
            semester_order = all_semesters
        current_index = all_semesters.index(semester)
        for i in range(current_index + 1, len(all_semesters)):
            if i < len(all_semesters):
                next_semester = all_semesters[i]
                if next_semester in semester_order:
                    return f"{year}-{next_semester}"
        # If we reach the end of the semester list, increment the year and start from the first valid semester
        year += 1
        for i in range(len(all_semesters)):
            next_semester = all_semesters[i]
            if next_semester in semester_order:
                return f"{year}-{next_semester}"
            
    def get_term_before(self, term_label: str, skip_summer=True, skip_half_terms=True):
        """
        Gets the term label for the term before the given term.
        """
        year, semester = self.extract_year_and_semester(term_label)
        all_semesters = ["S", "Su", "Su1", "Su2", "F"]
        if skip_summer:
            semester_order = ["S", "F"]
        elif skip_half_terms:
            semester_order = ["S", "Su", "F"]
        else:
            semester_order = all_semesters
        current_index = all_semesters.index(semester)
        for i in range(current_index - 1, -1, -1):
            if i >= 0:
                prev_semester = all_semesters[i]
                if prev_semester in semester_order:
                    return f"{year}-{prev_semester}"
        # If we reach the beginning of the semester list, decrement the year and start from the last valid semester
        year -= 1
        for i in range(len(all_semesters) - 1, -1, -1):
            prev_semester = all_semesters[i]
            if prev_semester in semester_order:
                return f"{year}-{prev_semester}"
            
    def enforce_coprerequisites(self):
        """
        Moves courses with unmet coprerequisites forward to the term of its coprerequisite with the latest term.
        Iteratively moves courses forward until all coprerequisites are satisfied.
        If a coprerequisite does not yet have a term, it will be assigned to the term of the course.
        """
        is_unmet = True
        while is_unmet:
            is_unmet = False
            for course_name, course in self.curriculum.courses.items():
                print(f"Checking coprerequisites for course {course_name}.")
                if not course.completed:
                    unmet_coprereqs = self.get_unmet_coprerequisites_in_term(course_name)
                    if unmet_coprereqs:
                        is_unmet = True
                        # Move the course to the term of the coprerequisite with the latest FUTURE term
                        latest_term = None
                        for copreq in unmet_coprereqs:
                            copreq_course = self.curriculum.courses.get(copreq)
                            if copreq_course and (latest_term is None or self.is_term_earlier(copreq_course.term, latest_term, equal=True)):
                                latest_term = copreq_course.term
                        if latest_term:
                            print(f"  Moving {course_name} to the term of its latest coprerequisite: {latest_term}.")
                            year, semester = self.extract_year_and_semester(latest_term)
                            self.set_course_term(course_name, year, semester)
    
    def get_unmet_coprerequisites_in_term(self, course_name, term=None):
        """
        Returns a list of coprerequisites for a given course that will not be met by the term in which the course is planned.
        """
        course = self.curriculum.courses.get(course_name)
        if not course:
            return []
        course_term = term if term is not None else course.term  # Use the provided term or the course's term
        unmet_coprereqs = []
        for copreq in course.coprereqs:
            copreq_course = self.curriculum.courses.get(copreq)
            copreq_term = copreq_course.term
            if copreq_course and not self.is_term_earlier(term=copreq_term, than=course_term, equal=True):
                unmet_coprereqs.append(copreq)
        print(f"  Unmet coprerequisites for {course_name} in term {course_term}: {unmet_coprereqs}")
        return unmet_coprereqs
    
    def enforce_corequisites(self):
        """
        Moves courses with unmet corequisites forward to the term of its corequisite with the latest term.
        Iteratively moves courses forward until all corequisites are satisfied.
        If a corequisite does not yet have a term, it will be assigned to the term of the course.
        """
        is_unmet = True
        while is_unmet:
            is_unmet = False
            for course_name, course in self.curriculum.courses.items():
                print(f"Checking corequisites for course {course_name}.")
                if not course.completed:
                    unmet_coreqs = self.get_unmet_corequisites_in_term(course_name)
                    if unmet_coreqs:
                        is_unmet = True
                        # Move the course to the term of the corequisite with the latest FUTURE term
                        latest_term = None
                        for coreq in unmet_coreqs:
                            coreq_course = self.curriculum.courses.get(coreq)
                            if coreq_course and (latest_term is None or self.is_term_earlier(coreq_course.term, latest_term, equal=True)):
                                latest_term = coreq_course.term
                        if latest_term:
                            print(f"  Moving {course_name} to the term of its latest corequisite: {latest_term}.")
                            year, semester = self.extract_year_and_semester(latest_term)
                            self.set_course_term(course_name, year, semester)

    def get_unmet_corequisites_in_term(self, course_name, term=None):
        """
        Returns a list of corequisites for a given course that will not be met by the term in which the course is planned.
        """
        course = self.curriculum.courses.get(course_name)
        if not course:
            return []
        course_term = term if term is not None else course.term  # Use the provided term or the course's term
        unmet_coreqs = []
        for coreq in course.coreqs:
            coreq_course = self.curriculum.courses.get(coreq)
            coreq_term = coreq_course.term
            if coreq_course and not self.is_term_earlier(term=coreq_term, than=course_term, equal=True):
                unmet_coreqs.append(coreq)
        print(f"  Unmet corequisites for {course_name} in term {course_term}: {unmet_coreqs}")
        return unmet_coreqs
                    
    def enforce_prerequisites(self):
        """
        Moves courses with unmet prerequisites to terms in which they can be taken.
        Iteratively moves courses forward until all prerequisites are satisfied.
        """
        # Check all courses for unmet prerequisites
        is_unmet = True
        while is_unmet:
            is_unmet = False
            for course_name, course in self.curriculum.courses.items():
                print(f"Checking prerequisites for course {course_name}.")
                if not course.completed:
                    unmet_prereqs = self.get_unmet_prerequisites_in_term(course_name)
                    if unmet_prereqs:
                        is_unmet = True
                        # Move the course to the term after the term it was in
                        current_term = course.term
                        if current_term:
                            next_term = self.get_term_after(current_term)
                            year, semester = self.extract_year_and_semester(next_term)
                            self.set_course_term(course_name, year, semester)
                            print(f"Moved {course_name} to {next_term} due to unmet prerequisites.")

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
        
    def get_unmet_prerequisites_in_term(self, course_name, term=None):
        """
        Returns a list of prerequisites for a given course that will not be met by the term in which the course is planned.
        """
        course = self.curriculum.courses.get(course_name)
        if not course:
            return []
        course_term = term if term is not None else course.term  # Use the provided term or the course's term
        unmet_prereqs = []
        for prereq in course.prereqs:
            print(f"Checking prerequisite {prereq} for course {course_name}.")
            prereq_course = self.curriculum.courses.get(prereq)
            prereq_term = prereq_course.term
            print(f"  Is {prereq_term} older than {course_term}?")
            if prereq_course and not self.is_term_earlier(term=prereq_term, than=course_term, equal=False):
                print(f"  {prereq} is not met for {course_name} in term {course_term}.")
                unmet_prereqs.append(prereq)
            else:
                print(f"  {prereq} is met for {course_name} in term {course_term}.")
        print(f"  Unmet prerequisites for {course_name} in term {course_term}: {unmet_prereqs}")
        return unmet_prereqs
    
    def is_term_earlier(self, term, than, equal=False):
        """
        Checks if the given term is older than the specified term.
        If equal is True, it also considers terms that are the same as older.
        """
        term_year, term_semester = self.extract_year_and_semester(term)
        than_year, than_semester = self.extract_year_and_semester(than)
        
        if term_year < than_year:
            return True
        elif term_year == than_year:
            semester_order = ["S", "Su", "Su1", "Su2", "F"]
            if semester_order.index(term_semester) < semester_order.index(than_semester):
                return True
            elif equal and semester_order.index(term_semester) == semester_order.index(than_semester):
                return True
        return False

    def compress_schedule(self, only_constrained=True):
        """
        Compresses the schedule by moving courses to the earliest possible term.
        This is useful for optimizing the course load and ensuring prerequisites are met.
        """
        print("Compressing schedule by moving courses to the earliest possible term.")
        for course_name, course in self.curriculum.courses.items():
            if not course.completed:
                current_term = course.term
                if current_term:
                    # Move everything (or everything constrained) to next semester (this will violate pre, co, and coprerequisites)
                    next_term = self.get_term_after(self.get_term_now())
                    if self.is_term_earlier(next_term, than=current_term, equal=False):
                        if only_constrained:
                            if (course.prereqs or course.coreqs or course.coprereqs):
                                self.set_course_term(course_name, *self.extract_year_and_semester(next_term))
                        else:
                            self.set_course_term(course_name, *self.extract_year_and_semester(next_term))
        # Now we need to enforce prerequisites, coprerequisites, and corequisites
        self.enforce_prerequisites()
        self.enforce_coprerequisites()
        self.enforce_corequisites()

    def set_course_term(self, course_name: str, year: int = None, semester: str = None, term: str = None):
        """
        Assigns a specific normalized term label like '2025-F' to the course.
        Term has to be provided as a string like '2025-F' to term argument or
        as separate year and semester arguments.
        """
        if term:
            year, semester = self.extract_year_and_semester(term)
        term_label = self._normalize_term_label(year, semester)
        self.courses_by_term()[course_name] = term_label
        self.set_term(course_name, term_label)

    def get_course_term(self, course_name: str):
        """
        Retrieves the term assignment for a course.
        """
        return self.courses[course_name].term if course_name in self.courses else None
    
    def bump_course_term(self, course_name: str, skip_summer=True, skip_half_terms=True, reverse=False):
        """
        Moves the course to the next term after its current term.
        If reverse is True, it moves to the previous term instead.
        If skip_summer is True, it skips summer terms.
        """
        if course_name not in self.courses:
            raise KeyError(f"Course {course_name} not found in curriculum.")
        
        current_term = self.get_course_term(course_name)
        if current_term is None:
            raise ValueError(f"Course {course_name} does not have a term assigned.")
        
        if reverse: # Move to the previous term
            new_term = self.get_term_before(current_term, skip_summer=skip_summer, skip_half_terms=skip_half_terms)
        else: # Move to the next term
            new_term = self.get_term_after(current_term, skip_summer=skip_summer, skip_half_terms=skip_half_terms)
        self.set_course_term(course_name, term=new_term)

    def bump_to_typical_term(self, course_name: str):
        """
        Moves the course to the typical term for its type.
        For example, if the course is typically taken in Fall, it will be moved to the next Fall term.
        """
        if course_name not in self.curriculum.courses:
            raise KeyError(f"Course {course_name} not found in curriculum.")
        
        course = self.curriculum.courses[course_name]

        if course.term is None:
            raise ValueError(f"Course {course_name} does not have a term assigned.")
        
        if course.completed:
            return course.term  # No need to bump completed courses
        
        # Determine the typical term based on the course's type
        typical_semester = course.typical_semester
        if typical_semester is None:
            # If no typical semester is defined, we can't bump the course
            print(f"No typical semester defined for {course_name}, cannot bump.")
            return course.term
        else:
            current_semester = self.extract_year_and_semester(course.term)[1]
            if typical_semester != current_semester:
                # Move to the next occurrence of the typical semester
                # Iterate through the terms until we find the next occurrence of the typical semester
                while True:
                    next_term = self.get_term_after(course.term, skip_summer=True, skip_half_terms=True)
                    next_year, next_semester = self.extract_year_and_semester(next_term)
                    course.term = next_term
                    if next_semester == typical_semester:
                        break
        print(f"Bumping {course_name} from {current_semester} to its typical term: {course.term}.")
        return course.term
    
    def bump_all_courses_to_typical_terms(self):
        """
        Moves all courses in the plan to their typical terms.
        This is useful for ensuring that courses are scheduled in the semesters they are typically offered.
        """
        print("Bumping all courses to their typical terms.")
        for course_name in self.curriculum.courses:
            try:
                self.bump_to_typical_term(course_name)
            except ValueError as e:
                print(f"Could not bump {course_name}: {e}")

    def remove_course_term(self, course_name: str):
        """
        Removes the term assignment for a course, effectively removing it from the plan.
        """
        self.courses_by_term().pop(course_name, None)
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
        start_index = term_order.index(self._normalize_term_label(self.start_year, self.start_semester).split("-")[1])
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
                # If it ends with a letter, and that letter isn't a W or L, strip it
                if course_name[-1].isalpha() and course_name[-1] != 'W' and course_name[-1] != 'L':
                    course_name = course_name[:-1]
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
                        # if match.group(2).lower() == "transfer":
                            # self.start_year = 0
                            # self.start_semester = "Transfer"
                        year_raw = match.group(1)
                        semester_raw = match.group(2)
                        print(f"  Setting term for {course_name} to semester {semester_raw} of year {year_raw}.")
                        try:
                            term_label = self._normalize_term_label(year_raw, semester_raw)
                            self.courses_by_term()[course_name] = term_label
                            self.set_term(course_name, term_label)
                        except Exception as e:
                            print(f"  Error setting term for {course_name}: {e}")
                            pass
        self.move_unfinished_courses_forward()  # Move unfinished courses to the next term after the current term
        self.enforce_prerequisites()  # Ensure all courses have their prerequisites satisfied
        self.enforce_coprerequisites()  # Ensure all courses have their coprerequisites satisfied
        self.enforce_corequisites()  # Ensure all courses have their corequisites satisfied
    
    def last_term(self):
        """
        Returns the last term in the plan.
        """
        last_term = self._normalize_term_label(self.start_year, self.start_semester)
        for course_name, course in self.curriculum.courses.items():
            if course.term is not None:
                print(f"IS {course_name} in the last term? Is {course.term} later than {last_term}? ", end="")
                if not self.is_term_earlier(course.term, last_term, equal=True):
                    last_term = course.term
                    print(f" ... YES!")
        return last_term