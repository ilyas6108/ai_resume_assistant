from langchain_core.prompts import ChatPromptTemplate


def get_prompt(feature: str) -> ChatPromptTemplate:
    """
    Returns the correct ChatPromptTemplate for the requested feature.
    Does NOT invoke it — invoking happens later once you have the actual
    resume_text / job_description / target_role values, via:
        prompt = get_prompt("ats_score")
        chain = prompt | llm | parser
        result = chain.invoke({"resume_text": resume_text})
    """

    if feature == "ats_score":
        return ChatPromptTemplate.from_messages([
            ("system",
             "You are an ATS (Applicant Tracking System) evaluator. "
             "Score resumes strictly based on formatting, keyword clarity, section structure, "
             "and machine-readability — not on subjective writing quality."),
            ("human",
             """Evaluate the following resume for ATS compatibility.
            Resume:
            {resume_text}
            Return your response in this exact format:
            Score: <0-100>
            Strengths: <bullet list>
            Issues: <bullet list>
            Fixes: <bullet list, specific and actionable>""")
        ])

    elif feature == "skill_gap":
        return ChatPromptTemplate.from_messages([
            ("system",
             "You identify gaps between a candidate's resume and a target job description. "
             "Be specific — name exact skills, not vague categories."),
            ("human",
             """Compare the resume against the job description below.
            Resume:
            {resume_text}
            Job Description:
            {job_description}
            Return your response in this exact format:
            Matched Skills: <bullet list>
            Missing Skills: <bullet list>
            Partially Matched Skills: <bullet list, note what's missing to fully match>
            Recommendation: <2-3 sentences on how to close the biggest gaps>""")
        ])

    elif feature == "interview_questions":
        return ChatPromptTemplate.from_messages([
            ("system",
             "You generate interview questions tailored to a specific candidate's resume "
             "and, if provided, a target job description. Questions should probe depth on "
             "claims made in the resume, not be generic."),
            ("human",
             """Generate interview questions for this candidate.
            Resume:
            {resume_text}
            Job Description (optional, may be empty):
            {job_description}
            Generate:
            - 3 technical questions based on specific projects/skills in the resume
            - 2 behavioral questions based on the candidate's experience
            - 2 questions probing any resume claims that seem vague or unverifiable
            Format as a numbered list with the category labeled for each.""")
        ])

    elif feature == "resume_rewrite":
        return ChatPromptTemplate.from_messages([
            ("system",
             "You rewrite resume content to be more concise, quantified, and impact-driven. "
             "Preserve all factual claims exactly — never invent metrics, titles, or experience "
             "that aren't already present or clearly implied in the original."),
            ("human",
             """Rewrite the following resume section to be stronger, using action verbs and
            quantifiable outcomes where the original text supports it.
            Original:
            {resume_text}
            Target role (optional, may be empty):
            {target_role}
            Return only the rewritten text, no explanation.""")
        ])

    elif feature == "job_match":
        return ChatPromptTemplate.from_messages([
            ("system",
             "You assess how well a resume matches a job description, considering skills, "
             "experience level, and domain relevance — not just keyword overlap."),
            ("human",
             """Assess the match between this resume and job description.
            Resume:
            {resume_text}
            Job Description:
            {job_description}
            Return your response in this exact format:
            Match Percentage: <0-100>%
            Reasoning: <3-4 sentences justifying the score>
            Top 3 Alignment Points: <bullet list>
            Top 3 Gaps: <bullet list>""")
        ])

    else:
        raise ValueError(
            f"Unknown feature '{feature}'. "
            "Expected one of: ats_score, skill_gap, interview_questions, resume_rewrite, job_match"
        )