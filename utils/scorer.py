from google import genai
import os
from dotenv import load_dotenv
import json
import re
import time

load_dotenv()


# ---- STEP 1: Connect to Gemini ----
def get_client():
    """Creates and returns Gemini client"""
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ---- STEP 2: Main Resume Analysis Prompt ----
PROMPT_TEMPLATE = """
You are an expert HR recruiter and resume analyst with 10 years experience.
You have reviewed thousands of resumes for Data Science and ML roles.

Your job is to carefully analyse the resume against the job description below.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Analyse thoroughly and return ONLY a JSON object with this exact structure.
Do not write anything before or after the JSON.
Do not add markdown or code blocks.

{{
    "match_score": <integer between 0 and 100>,
    "match_level": "<one of: Poor / Average / Good / Excellent>",
    "matched_skills": [<list of skills found in both resume and JD>],
    "missing_skills": [<list of skills mentioned in JD but absent in resume>],
    "strengths": [<list of 3 specific strong points of this resume for this role>],
    "weaknesses": [<list of 3 specific weak points of this resume for this role>],
    "suggestions": [<list of 3 specific actionable improvements candidate should make>],
    "overall_summary": "<2-3 sentence honest assessment of this candidate for this role>",
    "ats_score": <integer between 0 and 100 — how well resume will pass ATS software>,
    "ats_issues": [<list of ATS formatting problems found in resume>],
    "keywords_to_add": [<exact keywords from JD that are missing in resume>],
    "learning_roadmap": [
        {{
            "skill": "<missing skill name>",
            "time_to_learn": "<realistic time like 2 weeks or 1 month>",
            "free_resource": "<specific free course or resource name>"
        }}
    ]
}}
"""


# ---- STEP 3: Interview Questions Prompt ----
INTERVIEW_PROMPT = """
You are an expert technical interviewer for Data Science and ML roles.

Based on the resume and job description below, generate 8 likely interview questions
this candidate should prepare for.

RESUME STRENGTHS: {strengths}
RESUME WEAKNESSES: {weaknesses}
JOB DESCRIPTION: {jd}

Return ONLY a JSON object. No markdown. No extra text.

{{
    "technical_questions": [
        {{
            "question": "<interview question>",
            "why_asked": "<why interviewer would ask this>",
            "hint": "<key points to cover in answer>"
        }}
    ],
    "hr_questions": [
        {{
            "question": "<HR question>",
            "hint": "<how to answer well>"
        }}
    ]
}}
"""


# ---- STEP 4: Resume Bullet Rewriter Prompt ----
REWRITER_PROMPT = """
You are an expert resume writer specialising in Data Science and ML roles.

Rewrite the following weak resume bullet point to be stronger and more impactful.
Target role: {role}
Original bullet: {bullet}

Rules:
- Start with a strong action verb
- Add numbers or percentages where possible
- Be specific not vague
- Keep under 20 words each

Return ONLY a JSON object. No markdown. No extra text.

{{
    "original": "<original bullet>",
    "rewritten_versions": [
        "<version 1 — strong action verb>",
        "<version 2 — quantified impact>",
        "<version 3 — technical focus>"
    ],
    "why_better": "<one sentence explaining what makes these better>"
}}
"""


# ---- STEP 5: Interview Answer Generator Prompt ----
ANSWER_PROMPT = """
You are an expert interview coach for Data Science and ML fresher roles in India.

Generate a complete, confident, and personalized model answer for this interview question.

QUESTION: {question}
QUESTION TYPE: {question_type}
CANDIDATE RESUME SUMMARY: {resume_summary}
TARGET ROLE: {target_role}

Rules for the answer:
- Sound natural, not robotic
- Use STAR format for behavioural questions (Situation, Task, Action, Result)
- Use clear technical explanation for technical questions
- Reference candidate's actual projects where relevant
- Keep answer between 100-150 words — not too short, not too long
- End with a confident closing line

Return ONLY a JSON object. No markdown. No extra text.

{{
    "model_answer": "<complete answer the candidate should give>",
    "key_points_covered": [<list of 3-4 key points this answer hits>],
    "delivery_tips": "<one tip on HOW to deliver this answer confidently>",
    "follow_up_question": "<one likely follow-up question interviewer might ask next>",
    "follow_up_hint": "<brief hint on how to answer the follow up>"
}}
"""


# ---- HELPER: Call Gemini with retry logic ----
def call_gemini(prompt):
    """
    Calls Gemini API with automatic retry on 503 errors.
    Returns raw text response or error dict.
    """
    client = get_client()

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception as e:
            error_msg = str(e)

            if "503" in error_msg or "UNAVAILABLE" in error_msg:
                if attempt < 2:
                    wait_time = (attempt + 1) * 10
                    print(f"Server busy. Waiting {wait_time}s... (attempt {attempt + 1}/3)")
                    time.sleep(wait_time)
                    continue
                else:
                    return {"error": "Gemini server busy. Please try again in 1 minute."}

            elif "429" in error_msg:
                return {"error": "API quota exceeded. Wait a few minutes and try again."}

            else:
                return {"error": f"Unexpected error: {error_msg}"}


# ---- HELPER: Parse JSON from Gemini response ----
def parse_json(raw_text):
    """
    Extracts and parses JSON from Gemini response.
    Handles all edge cases including bool and None returns.
    """
    # Handle bool or None — sometimes Gemini returns these on errors
    if isinstance(raw_text, bool) or raw_text is None:
        return {"error": "Empty or invalid response from Gemini. Try again."}

    # Already an error dict from call_gemini
    if isinstance(raw_text, dict):
        return raw_text

    try:
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Could not find JSON in response", "raw": raw_text}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing failed: {str(e)}", "raw": raw_text}


# ================================================
# MAIN FUNCTIONS — called from main.py
# ================================================

# ---- FUNCTION 1: Score Resume ----
def score_resume(resume_text, jd_text):
    """
    Main resume analysis function.
    INPUT:  resume_text, jd_text (strings)
    OUTPUT: dict with score, skills, ATS, roadmap
    """
    prompt = PROMPT_TEMPLATE.format(
        resume=resume_text[:3000],
        jd=jd_text[:2000]
    )
    raw = call_gemini(prompt)
    return parse_json(raw)


# ---- FUNCTION 2: Generate Interview Questions ----
def generate_interview_questions(strengths, weaknesses, jd_text):
    """
    Generates interview questions based on resume analysis.
    INPUT:  strengths (list), weaknesses (list), jd_text (string)
    OUTPUT: dict with technical and HR questions
    """
    prompt = INTERVIEW_PROMPT.format(
        strengths=", ".join(strengths),
        weaknesses=", ".join(weaknesses),
        jd=jd_text[:1500]
    )
    raw = call_gemini(prompt)
    return parse_json(raw)


# ---- FUNCTION 3: Rewrite Resume Bullet ----
def rewrite_bullet(bullet_text, target_role):
    """
    Rewrites a weak resume bullet point.
    INPUT:  bullet_text (string), target_role (string)
    OUTPUT: dict with 3 rewritten versions
    """
    prompt = REWRITER_PROMPT.format(
        bullet=bullet_text,
        role=target_role
    )
    raw = call_gemini(prompt)
    return parse_json(raw)


# ---- FUNCTION 4: Generate Answer for Interview Question ----
def generate_answer(question, question_type, resume_summary, target_role):
    """
    Generates a complete model answer for one interview question.
    INPUT:
        question       — the interview question string
        question_type  — "technical" or "hr"
        resume_summary — short summary of candidate background
        target_role    — e.g. "Data Analyst" or "ML Engineer"
    OUTPUT: dict with model_answer, key_points, delivery_tips, follow_up
    """
    prompt = ANSWER_PROMPT.format(
        question=question,
        question_type=question_type,
        resume_summary=resume_summary,
        target_role=target_role
    )
    raw = call_gemini(prompt)
    return parse_json(raw)