import streamlit as st
import sys
import os
import plotly.express as px
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_reader import extract_text_from_pdf
from utils.scorer import score_resume, generate_interview_questions, rewrite_bullet, generate_answer
from utils.database import init_db, save_result, get_history

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="HireBot — AI Resume Screener",
    page_icon="🤖",
    layout="wide"
)

init_db()

# ---- HEADER ----
st.title("🤖 HireBot — AI Resume Screener")
st.markdown("Upload your resume and job description for complete AI-powered analysis")
st.divider()

# ---- TABS ----
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Analyse Resume",
    "🎯 Interview Prep",
    "✏️ Bullet Rewriter",
    "📊 History"
])


# ================================================
# TAB 1 — MAIN ANALYSIS
# ================================================
with tab1:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📎 Upload Resume")
        resume_file = st.file_uploader(
            "Upload PDF resume",
            type=["pdf"],
            key="resume_upload"
        )
        if resume_file:
            st.success(f"✅ {resume_file.name} uploaded")

    with col2:
        st.subheader("📋 Job Description")
        jd_text = st.text_area(
            "Paste job description here",
            height=200,
            placeholder="Copy and paste from Naukri, LinkedIn...",
            key="jd_input"
        )

    st.divider()

    if st.button("🔍 Analyse My Resume", type="primary", use_container_width=True):

        if not resume_file:
            st.error("❌ Please upload your resume PDF")
            st.stop()
        if not jd_text.strip():
            st.error("❌ Please paste the job description")
            st.stop()

        with st.spinner("🤖 AI is analysing your resume..."):
            resume_text = extract_text_from_pdf(resume_file)
            result = score_resume(resume_text, jd_text)
            st.session_state["result"] = result
            st.session_state["jd_text"] = jd_text
            st.session_state["resume_text"] = resume_text

        if not isinstance(result, dict) or "error" in result:
            st.error(f"⚠️ {result.get('error', 'Something went wrong.')}")
            st.info("💡 Wait 1 minute and try again if server is busy.")
            st.stop()

        save_result(resume_file.name, result)
        st.success("✅ Analysis Complete!")
        st.divider()

        # ---- SCORES ----
        score = result.get("match_score", 0)
        ats = result.get("ats_score", 0)
        level = result.get("match_level", "")

        st.subheader("🎯 Scores")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Match Score", f"{score}/100")
            st.progress(score / 100)

        with c2:
            st.metric("ATS Score", f"{ats}/100")
            st.progress(ats / 100)

        with c3:
            if score >= 80:
                st.success(f"**{level}** ✅")
            elif score >= 60:
                st.warning(f"**{level}** 🟡")
            else:
                st.error(f"**{level}** ❌")

        st.divider()

        # ---- SKILLS CHART ----
        st.subheader("🛠️ Skills Analysis")
        matched = result.get("matched_skills", [])
        missing = result.get("missing_skills", [])

        chart_data = (
            [{"Skill": s, "Status": "✅ Matched"} for s in matched] +
            [{"Skill": s, "Status": "❌ Missing"} for s in missing]
        )

        if chart_data:
            df_skills = pd.DataFrame(chart_data)
            fig = px.bar(
                df_skills,
                x="Skill",
                color="Status",
                title="Skills: Matched vs Missing",
                color_discrete_map={
                    "✅ Matched": "#00cc66",
                    "❌ Missing": "#ff4444"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ---- ATS SECTION ----
        ats_issues = result.get("ats_issues", [])
        keywords = result.get("keywords_to_add", [])

        if ats_issues or keywords:
            st.subheader("🤖 ATS Analysis")
            ca, cb = st.columns(2)

            with ca:
                st.markdown("**⚠️ ATS Issues Found**")
                for issue in ats_issues:
                    st.warning(f"• {issue}")

            with cb:
                st.markdown("**🔑 Keywords to Add**")
                for kw in keywords:
                    st.info(f"• {kw}")

        st.divider()

        # ---- STRENGTHS & WEAKNESSES ----
        st.subheader("📊 Detailed Breakdown")
        c3, c4 = st.columns(2)

        with c3:
            st.markdown("**💪 Strengths**")
            for s in result.get("strengths", []):
                st.success(f"✅ {s}")

            st.markdown("**⚠️ Weaknesses**")
            for w in result.get("weaknesses", []):
                st.error(f"❌ {w}")

        with c4:
            st.markdown("**💡 Suggestions**")
            for i, s in enumerate(result.get("suggestions", []), 1):
                st.info(f"**{i}.** {s}")

        st.divider()

        # ---- LEARNING ROADMAP ----
        roadmap = result.get("learning_roadmap", [])
        if roadmap:
            st.subheader("🗺️ Learning Roadmap")
            for item in roadmap:
                with st.expander(f"📚 {item.get('skill', '')} — {item.get('time_to_learn', '')}"):
                    st.write(f"**Free Resource:** {item.get('free_resource', '')}")

        st.divider()

        # ---- SUMMARY ----
        st.subheader("📝 AI Summary")
        st.write(result.get("overall_summary", ""))


# ================================================
# TAB 2 — INTERVIEW PREP
# ================================================
with tab2:
    st.subheader("🎯 Interview Question Generator")

    if "result" not in st.session_state:
        st.info("👆 First analyse your resume in Tab 1, then come here.")
    else:
        result = st.session_state["result"]
        jd = st.session_state["jd_text"]

        resume_summary = f"""
        Strengths: {', '.join(result.get('strengths', []))}
        Skills: {', '.join(result.get('matched_skills', []))}
        Weaknesses: {', '.join(result.get('weaknesses', []))}
        """

        target_role = st.text_input(
            "Target Role",
            value="Data Analyst",
            placeholder="e.g. Data Analyst, ML Engineer"
        )

        if st.button("🎯 Generate Interview Questions", type="primary"):
            with st.spinner("Generating personalised questions..."):
                questions = generate_interview_questions(
                    result.get("strengths", []),
                    result.get("weaknesses", []),
                    jd
                )
            st.session_state["questions"] = questions
            st.session_state["target_role"] = target_role
            st.session_state["resume_summary"] = resume_summary

        if "questions" in st.session_state:
            questions = st.session_state["questions"]
            role = st.session_state.get("target_role", "Data Analyst")
            r_summary = st.session_state.get("resume_summary", "")

            if not isinstance(questions, dict) or "error" in questions:
                st.error(questions.get("error", "Something went wrong. Try again."))
            else:

                # ---- TECHNICAL QUESTIONS ----
                st.subheader("💻 Technical Questions")

                for i, q in enumerate(questions.get("technical_questions", [])):
                    question_text = q.get("question", "")

                    with st.expander(f"Q{i + 1}: {question_text}"):
                        st.markdown(f"**Why asked:** {q.get('why_asked', '')}")
                        st.markdown(f"**Hint:** {q.get('hint', '')}")

                        btn_key = f"tech_ans_{i}"
                        if st.button("🤖 Generate Model Answer", key=btn_key):
                            with st.spinner("Generating answer..."):
                                answer = generate_answer(
                                    question=question_text,
                                    question_type="technical",
                                    resume_summary=r_summary,
                                    target_role=role
                                )
                            st.session_state[btn_key + "_data"] = answer

                        if btn_key + "_data" in st.session_state:
                            ans = st.session_state[btn_key + "_data"]

                            if not isinstance(ans, dict) or "error" in ans:
                                st.error(ans.get("error", "Something went wrong. Try again."))
                            else:
                                st.divider()
                                st.markdown("**✅ Model Answer:**")
                                st.success(ans.get("model_answer", ""))

                                st.markdown("**📌 Key Points Covered:**")
                                for point in ans.get("key_points_covered", []):
                                    st.write(f"• {point}")

                                st.markdown(f"**🎤 Delivery Tip:** {ans.get('delivery_tips', '')}")

                                st.markdown("**🔄 Likely Follow-up Question:**")
                                st.warning(ans.get("follow_up_question", ""))
                                st.info(f"**Hint:** {ans.get('follow_up_hint', '')}")

                st.divider()

                # ---- HR QUESTIONS ----
                st.subheader("👔 HR Questions")

                for i, q in enumerate(questions.get("hr_questions", [])):
                    question_text = q.get("question", "")

                    with st.expander(f"Q{i + 1}: {question_text}"):
                        st.markdown(f"**Hint:** {q.get('hint', '')}")

                        btn_key = f"hr_ans_{i}"
                        if st.button("🤖 Generate Model Answer", key=btn_key):
                            with st.spinner("Generating answer..."):
                                answer = generate_answer(
                                    question=question_text,
                                    question_type="hr",
                                    resume_summary=r_summary,
                                    target_role=role
                                )
                            st.session_state[btn_key + "_data"] = answer

                        if btn_key + "_data" in st.session_state:
                            ans = st.session_state[btn_key + "_data"]

                            if not isinstance(ans, dict) or "error" in ans:
                                st.error(ans.get("error", "Something went wrong. Try again."))
                            else:
                                st.divider()
                                st.markdown("**✅ Model Answer:**")
                                st.success(ans.get("model_answer", ""))

                                st.markdown(f"**🎤 Delivery Tip:** {ans.get('delivery_tips', '')}")

                                st.markdown("**🔄 Likely Follow-up:**")
                                st.warning(ans.get("follow_up_question", ""))
                                st.info(f"**Hint:** {ans.get('follow_up_hint', '')}")


# ================================================
# TAB 3 — BULLET REWRITER
# ================================================
with tab3:
    st.subheader("✏️ Resume Bullet Point Rewriter")
    st.markdown("Paste any weak resume line and AI will rewrite it stronger")

    target_role_rw = st.text_input(
        "Target Role",
        placeholder="e.g. Data Analyst, ML Engineer",
        key="rw_role"
    )

    weak_bullet = st.text_area(
        "Paste your weak resume bullet point",
        placeholder="e.g. Worked on machine learning project using Python",
        height=100
    )

    if st.button("✨ Rewrite My Bullet", type="primary"):
        if not weak_bullet.strip():
            st.error("Please enter a bullet point")
            st.stop()
        if not target_role_rw.strip():
            st.error("Please enter target role")
            st.stop()

        with st.spinner("AI is rewriting your bullet..."):
            rewrite_result = rewrite_bullet(weak_bullet, target_role_rw)

        if not isinstance(rewrite_result, dict) or "error" in rewrite_result:
            st.error(rewrite_result.get("error", "Something went wrong. Try again."))
        else:
            st.divider()
            st.markdown("**❌ Original:**")
            st.error(rewrite_result.get("original", weak_bullet))

            st.markdown("**✅ Rewritten Versions:**")
            for i, version in enumerate(rewrite_result.get("rewritten_versions", []), 1):
                st.success(f"**Version {i}:** {version}")

            st.info(f"**💡 Why better:** {rewrite_result.get('why_better', '')}")


# ================================================
# TAB 4 — HISTORY
# ================================================
with tab4:
    st.subheader("📊 Past Analyses")

    history = get_history()

    if len(history) == 0:
        st.info("No analyses yet. Analyse a resume first.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Analyses", len(history))
        c2.metric("Average Score", f"{history['match_score'].mean():.0f}/100")
        c3.metric("Best Score", f"{history['match_score'].max()}/100")

        st.divider()

        fig2 = px.line(
            history,
            x="timestamp",
            y="match_score",
            title="Your Score Trend Over Time",
            markers=True
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(
            history[[
                "resume_name", "match_score",
                "match_level", "missing_skills", "timestamp"
            ]],
            use_container_width=True
        )