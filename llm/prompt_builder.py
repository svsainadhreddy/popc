def build_ppc_prompt(patient, survey, section_scores, answers, question):
    # Group answers by section
    section_answers = {}
    for ans in answers:
        section_answers.setdefault(ans.section_name, []).append(
            f"- {ans.question}: {ans.selected_option} (Score {ans.score})"
        )

    formatted_sections = ""
    for section, qa_list in section_answers.items():
        formatted_sections += f"\n{section}:\n"
        formatted_sections += "\n".join(qa_list)
        formatted_sections += "\n"

    return f"""
You are a clinical decision support assistant for doctors.

You do NOT ask questions.
You ONLY provide concise, evidence-based suggestions.
you Only provide answer for asked question correctly.
you only provide short answer.

=====================
PATIENT SUMMARY
=====================
Age: {patient.age}
BMI: {patient.bmi}

=====================
PPC RISK
=====================
Total Score: {survey.total_score}/85
Risk Level: {survey.risk_level}

=====================
SECTION SCORES
=====================
{chr(10).join(f"- {s.section_name}: {s.score}" for s in section_scores)}

=====================
QUESTIONNAIRE DETAILS
=====================
{formatted_sections}

=====================
DOCTOR QUESTION
=====================
{question},based on the above patient information and related to question in 5lines?

=====================
FINAL ANSWER (START HERE)
=====================
"""
