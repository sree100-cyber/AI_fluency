"""The one tool: a GPA calculator.

A language model predicts text; it does not run arithmetic. This function does the
exact weighted-average calculation, and returns its result (or its error) as PLAIN TEXT.
"""

GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "U": 0}


def calculate_gpa(courses: list) -> str:
    """courses: list of {"name": str, "grade": str, "credits": number}.
    Returns a plain-text report. Never raises: errors come back as text too."""
    try:
        if not courses:
            return "ERROR: no courses were given."
        total_points = 0.0
        total_credits = 0.0
        lines = []
        for i, c in enumerate(courses, start=1):
            grade = str(c.get("grade", "")).strip().upper()
            credits = float(c.get("credits", 0))
            name = c.get("name", f"Course {i}")
            if grade not in GRADE_POINTS:
                return (f"ERROR: unknown grade '{grade}' for {name}. "
                        f"Valid grades: {', '.join(GRADE_POINTS)}.")
            if credits <= 0:
                return f"ERROR: credits for {name} must be greater than 0."
            pts = GRADE_POINTS[grade] * credits
            total_points += pts
            total_credits += credits
            lines.append(f"{name}: grade {grade} ({GRADE_POINTS[grade]}) x {credits:g} credits = {pts:g}")
        gpa = total_points / total_credits
        return ("\n".join(lines)
                + f"\nTotal grade points = {total_points:g}; total credits = {total_credits:g}"
                + f"\nGPA = {total_points:g} / {total_credits:g} = {gpa:.2f}")
    except Exception as e:  # even unexpected failures are returned as text
        return f"ERROR: could not calculate GPA ({e})."


# The schema: this is ALL the model ever sees of the function.
TOOL_SCHEMA = {
    "name": "calculate_gpa",
    "description": (
        "Calculates a semester GPA exactly as a credit-weighted average of grade points. "
        "Use it whenever the user gives a list of courses with grades and credits and wants a GPA. "
        "Grade scale: O=10, A+=9, A=8, B+=7, B=6, C=5, U=0."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "courses": {
                "type": "array",
                "description": "One entry per course.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Course name"},
                        "grade": {"type": "string", "description": "Letter grade, e.g. A+"},
                        "credits": {"type": "number", "description": "Credit value of the course"},
                    },
                    "required": ["grade", "credits"],
                },
            }
        },
        "required": ["courses"],
    },
}
