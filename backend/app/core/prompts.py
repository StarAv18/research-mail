from typing import Any, Dict

class PromptTemplate:
    """
    Utility for managing and formatting AI prompts.
    
    Ensures that prompts are consistent and handles variable injection.
    """
    
    def __init__(self, template: str, input_variables: list[str]):
        self.template = template
        self.input_variables = input_variables

    def format(self, **kwargs: Any) -> str:
        """
        Format the template with the provided variables.
        
        Args:
            **kwargs: Variables to inject into the template.
            
        Returns:
            The formatted prompt string.
            
        Raises:
            KeyError: If a required variable is missing.
        """
        # Validate that all required variables are present
        for var in self.input_variables:
            if var not in kwargs:
                raise KeyError(f"Missing required prompt variable: {var}")
        
        return self.template.format(**kwargs)

# Centralized Prompts
SUMMARIZATION_TEMPLATE = """
You are an expert academic researcher. Your task is to analyze the provided research text about a professor and extract a structured summary.

Input Text:
{research_text}

Output Format (JSON ONLY):
{output_format}

Rules:
1. Return ONLY valid JSON.
2. If a field is unknown, use an empty list or null.
3. Ensure the summary is professional and academic.
4. Focus on the most recent and impactful information.
5. The summary must be at least 50 characters long.
"""

SUMMARIZATION_PROMPT = PromptTemplate(
    template=SUMMARIZATION_TEMPLATE,
    input_variables=["research_text", "output_format"]
)

# Email Generation Prompts
EMAIL_GENERATION_TEMPLATE = """
You are an expert at writing personalized, professional outreach emails for research internships.
Your goal is to write an email to a professor from a student, showing deep interest in their research.

Professor Information:
Name: {professor_name}
University: {professor_university}
Research Interests: {professor_interests}
Research Summary: {professor_summary}

Student Information:
Name: {student_name}
University: {student_university}
Major: {student_major}
Skills: {student_skills}
Experience: {student_experience}
Interests: {student_interests}

Email Style: {email_style}

Output Format (JSON ONLY):
{{
    "subject": "Professional and engaging subject line",
    "body": "The complete personalized email body"
}}

Rules:
1. Tone: Professional, academic, respectful, and genuinely interested.
2. Personalization: Reference the professor's specific research focus and connect it to the student's background.
3. Length: Concise but meaningful (approx 150-250 words).
4. Do NOT use placeholders like [Professor Name]; use the actual information provided.
5. Ensure a strong call to action (e.g., asking for a brief meeting or opportunity to discuss).
"""

EMAIL_GENERATION_PROMPT = PromptTemplate(
    template=EMAIL_GENERATION_TEMPLATE,
    input_variables=[
        "professor_name", "professor_university", "professor_interests", "professor_summary",
        "student_name", "student_university", "student_major", "student_skills", 
        "student_experience", "student_interests", "email_style"
    ]
)
