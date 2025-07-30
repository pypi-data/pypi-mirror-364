from smume.curriculum import Curriculum
from smume.generic_plan import GenericPlan

curriculum = Curriculum("ME 2024–25")

# Define Categories

categories_def = {
    "C": {"name": "Core", "order": 0, "aliases": ["Core"]},
    "F": {"name": "Foundation", "order": 1, "aliases": ["Foundation"]},
    "Con": {"name": "Conversatio", "order": 2, "aliases": ["Conversatio"]},
    "Ora": {"name": "Ora et Labora", "order": 3, "aliases": ["Ora et Labora"]},
    "MS": {"name": "Math and Science", "order": 4, "aliases": ["Math and Science"]},
    "GE": {"name": "General Engineering", "order": 5, "aliases": ["General Engineering"]},
    "ME": {"name": "Mechanical Engineering", "order": 6, "aliases": ["Mechanical Engineering"]},
    "O": {"name": "Other", "order": 7, "aliases": ["Other"]},
}
curriculum.define_categories(categories_def)

# Define the Courses

## Core Courses
curriculum.course('COR 100', 4, categories=["C", "F"], critical_path=False, full_name="First-Year Seminar")
curriculum.course('COR 110', 3, categories=["C", "F"], critical_path=False, full_name="Religious Studies")
curriculum.course('COR 120', 4, categories=["C", "F"], critical_path=True, full_name="Critical Reading and Writing")
curriculum.course('COR 210', 3, categories=["C", "Con"], critical_path=False, full_name="Humanities")
curriculum.course('COR 220', 3, categories=["C", "Con"], critical_path=False, full_name="Social Sciences")
curriculum.course('COR 240', 3, categories=["C", "Con"], critical_path=False, full_name="Artistic and Creative Expression")
curriculum.course('COR 250', 3, categories=["C", "Con"], critical_path=False, full_name="Historical and Political Studies")
curriculum.course('COR 310', 3, categories=["C", "Ora"], critical_path=False, full_name="Community: The Call to Serve the Common Good")
curriculum.course('COR 320', 3, categories=["C", "Ora"], critical_path=False, full_name="Hospitality and Openness to Others")
curriculum.course('COR 330', 3, categories=["C", "Ora"], critical_path=False, full_name="Stewardship: Responsible Use of Creation")
curriculum.course('COR 340', 3, categories=["C", "Ora"], critical_path=False, full_name="Ethics and the Dignity of Work")
curriculum.course('COR 210W', 4, categories=["C", "Con"], writing_intensive=True, critical_path=False, full_name="Humanities (Writing Intensive)")
curriculum.course('COR 220W', 4, categories=["C", "Con"], writing_intensive=True, critical_path=False, full_name="Social Sciences (Writing Intensive)")
curriculum.course('COR 240W', 4, categories=["C", "Con"], writing_intensive=True, critical_path=False, full_name="Artistic and Creative Expression (Writing Intensive)")
curriculum.course('COR 250W', 4, categories=["C", "Con"], writing_intensive=True, critical_path=False, full_name="Historical and Political Studies (Writing Intensive)")
curriculum.course('COR 310W', 4, categories=["C", "Ora"], writing_intensive=True, critical_path=False, full_name="Community: The Call to Serve the Common Good (Writing Intensive)")
curriculum.course('COR 320W', 4, categories=["C", "Ora"], writing_intensive=True, critical_path=False, full_name="Hospitality and Openness to Others (Writing Intensive)")
curriculum.course('COR 330W', 4, categories=["C", "Ora"], writing_intensive=True, critical_path=False, full_name="Stewardship: Responsible Use of Creation (Writing Intensive)")
curriculum.course('COR 340W', 4, categories=["C", "Ora"], writing_intensive=True, critical_path=False, full_name="Ethics and the Dignity of Work (Writing Intensive)")

## Math and Science
curriculum.course('MTH 171', 4, categories=["MS"], critical_path=True, full_name="Calculus I")
curriculum.course('PHY 171', 4, categories=["MS"], critical_path=True, full_name="Physics I").add_coprereq('MTH 171')
curriculum.course('PHY 171L', 1, categories=["MS"], critical_path=True, full_name="Physics I Laboratory").add_coreq('PHY 171')
curriculum.course('MTH 172', 4, categories=["MS"], critical_path=True, full_name="Calculus II").add_prereq('MTH 171')
curriculum.course('PHY 172', 4, categories=["MS"], critical_path=True, full_name="Physics II").add_coprereq('MTH 172').add_prereq('PHY 171')
curriculum.course('PHY 172L', 1, categories=["MS"], critical_path=True, full_name="Physics II Laboratory").add_coreq('PHY 172')
curriculum.course('CHM 145', 3, categories=["MS"], critical_path=True, full_name="Chemistry for Engineers", note="Chemistry for Engineers. Or CHM 141 (more credits).")
curriculum.course('MTH 353', 3, categories=["MS"], critical_path=True, full_name="Linear Algebra").add_prereq('MTH 172')

## General Engineering (GE)
curriculum.course('GE 104', 3, categories=["GE"], critical_path=True, full_name="Engineering Computing").add_prereq('MTH 171').add_prereq('PHY 171')
curriculum.course('GE 204', 3, categories=["GE"], critical_path=True, full_name="Statics").add_prereq('MTH 171').add_prereq('PHY 171')
curriculum.course('GE 205', 3, categories=["GE"], critical_path=True, full_name="Dynamics").add_prereq('GE 204')
curriculum.course('GE 206', 3, categories=["GE"], critical_path=True, full_name="Mechanics of Materials").add_prereq('GE 204')
curriculum.course('GE 207', 1, categories=["GE"], critical_path=True, full_name="Mechanics of Materials Laboratory").add_coprereq('GE 206')

## Mechanical Engineering (ME)
curriculum.course('ME 100', 1, categories=["ME"], critical_path=True, full_name="Mechanical Engineering Seminar")
curriculum.course('ME 201', 2, categories=["ME"], critical_path=True, full_name="Technical Communication").add_prereq('COR 120')
curriculum.course('ME 300', 3, categories=["ME"], critical_path=True, full_name="Manufacturing").add_prereq('GE 206')
curriculum.course('ME 300L', 1, categories=["ME"], critical_path=True, full_name="Manufacturing Laboratory").add_coprereq('ME 300')
curriculum.course('ME 303', 3, categories=["ME", "MS"], critical_path=True, full_name="Materials Science").add_prereq('GE 206').add_prereq('CHM 145')
curriculum.course('ME 316', 2, categories=["ME", "MS"], ms_credits=1, critical_path=True, full_name="Mechatronics and Instrumentation Laboratory").add_coprereq('ME 345')
curriculum.course('ME 340', 3, categories=["ME"], critical_path=True, full_name="Thermodynamics I").add_prereq('CHM 145').add_prereq('PHY 172').add_coprereq('MTH 172')
curriculum.course('ME 345', 3, categories=["ME"], critical_path=True, full_name="Mechatronics").add_prereq('MTH 172').add_prereq('PHY 172')
curriculum.course('ME 302', 3, categories=["ME"], critical_path=True, full_name="Machine Design").add_prereq('GE 206')
curriculum.course('ME 308', 3, categories=["ME"], critical_path=True, full_name="Fluid Mechanics I").add_prereq('GE 205').add_prereq('GE 206').add_prereq('MTH 172')
curriculum.course('ME 309', 2, categories=["ME", "MS"], ms_credits=1, critical_path=True, full_name="Fluid Mechanics Laboratory").add_coreq('ME 308')
curriculum.course('ME 350', 3, categories=["ME"], critical_path=True, full_name="Parametric Solid Modeling")
curriculum.course('ME 370', 3, categories=["ME"], critical_path=True, full_name="System Dynamics and Control").add_prereq('ME 345').add_prereq('GE 205').add_coprereq('MTH 353')
curriculum.course('ME 430', 3, categories=["ME"], critical_path=True, full_name="Heat Transfer").add_prereq('ME 340').add_prereq('ME 308')
curriculum.course('ME 430L', 2, categories=["ME", "MS"], ms_credits=1, critical_path=True, full_name="Heat Transfer Laboratory").add_coprereq('ME 430')
curriculum.course('ME 498', 3, categories=["ME"], critical_path=True, full_name="Senior Design I").add_prereq('ME 302').add_prereq('ME 370').add_coprereq('ME 430')
curriculum.course('ME 499', 3, categories=["ME"], critical_path=True, full_name="Senior Design II").add_prereq('ME 498')
curriculum.course('ME El. 1', 3, categories=["ME"], critical_path=True, full_name="Mechanical Engineering Elective 1")
curriculum.course('ME El. 2', 3, categories=["ME"], critical_path=True, full_name="Mechanical Engineering Elective 2")
curriculum.course('ME El. 3', 3, categories=["ME"], critical_path=True, full_name="Mechanical Engineering Elective 3")

# Define Category Requirements

# Core Requirements

## Total Credits (Have to be explicit because we defined all the W variants)
curriculum.category_requirement("C", kind="Number of Credits", number=31)
curriculum.category_requirement("F", kind="Number of Credits", number=11)
curriculum.category_requirement("Con", kind="Number of Credits", number=13)
curriculum.category_requirement("Ora", kind="Number of Credits", number=7)

## Specific Core Requirements
curriculum.category_requirement("Con", kind="Writing Intensive", number=1, note="One course must be writing intensive")
curriculum.category_requirement("Ora", kind="Writing Intensive", number=1, note="One course must be writing intensive")
curriculum.category_requirement("Ora", kind="Number of Courses", number=2, note="Two courses must be taken")

# Define DTA Exemptions
exemptions_DTA_AA = ["COR 100", "COR 120", "COR 210", "COR 220", "COR 240", "COR 250", "COR 310", "COR 320", "COR 330"]
curriculum.set_DTA_exemptions("AA-DTA", exemptions_DTA_AA)

# Assign Terms
generic_plan = GenericPlan(curriculum)
generic_plan.apply_term_mapping({
    "1F": ["MTH 171", "PHY 171", "PHY 171L", "ME 100", "COR 100"],
    "1S": ["MTH 172", "PHY 172", "PHY 172L", "GE 104", "COR 120"],
    "2F": ["GE 204", "CHM 145", "MTH 353", "ME 201", "COR 110"],
    "2S": ["GE 205", "GE 206", "GE 207", "ME 350", "COR 210"],
    "3F": ["ME 300", "ME 300L", "ME 303", "ME 316", "ME 345", "ME 340"],
    "3S": ["ME 302", "ME 308", "ME 309", "ME 370", "COR 220", "COR 240"],
    "4F": ["ME 430", "ME 430L", "ME 498", "ME El. 1", "COR 250W"],
    "4S": ["ME 499", "ME El. 2", "ME El. 3", "COR 310", "COR 340W"],
})
# generic_plan.print_dependency_issues() # Uncomment to check for dependency issues