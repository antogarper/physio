import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import os

# ── REGISTER COMPONENT ────────────────────────────────────
_component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "physio_form", "frontend")
physio_form = components.declare_component("physio_form", path=_component_dir)

st.set_page_config(page_title="PhysioAI Assessment", page_icon="🏥", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
.stApp { background-color: #f4f7fb; }
</style>
""", unsafe_allow_html=True)

# ── RENDER FORM COMPONENT ─────────────────────────────────
result = physio_form(key="physio_form")

# ── PROCESS WHEN SUBMITTED ────────────────────────────────
if result and result.get("submitted"):

    age               = result.get("age", 45)
    gender            = result.get("gender", "")
    weight            = result.get("weight", 70)
    height_val        = result.get("height", 170)
    occupation        = result.get("occupation", "")
    physical_activity = result.get("physical_activity", "")
    main_complaint    = result.get("main_complaint", "")
    body_area         = result.get("body_area", "")
    problem_duration  = result.get("problem_duration", "")
    problem_onset     = result.get("problem_onset", "")
    has_pain          = result.get("has_pain", False)
    pain_intensity    = result.get("pain_intensity", 0)
    aggravating       = result.get("aggravating", "")
    relieving         = result.get("relieving", "")
    previous_history  = result.get("previous_history", "")
    current_treatments= result.get("current_treatments", "")
    additional_info   = result.get("additional_info", "")
    language          = result.get("language", "English")

    prompt = f"""You are an expert physiotherapist assistant. Analyze the following patient data and return ONLY a valid JSON object, with no extra text, no markdown, no backticks.

PATIENT PROFILE:
- Age: {age} | Gender: {gender}
- Weight: {weight} kg | Height: {height_val} cm
- Occupation: {occupation}
- Physical activity: {physical_activity}

MAIN COMPLAINT:
- Description: {main_complaint}
- Body area affected: {body_area}
- Duration: {problem_duration}
- Onset: {problem_onset}

SYMPTOMS:
- Pain present: {"Yes, intensity " + str(pain_intensity) + "/10" if has_pain else "No"}
- Aggravating factors: {aggravating}
- Relieving factors: {relieving}

CLINICAL HISTORY:
- Previous injuries / conditions: {previous_history}
- Current treatments / medications: {current_treatments}
- Additional information: {additional_info}

Return this exact JSON structure (all text in {language}):
{{
  "primary_diagnosis": "Name of the most likely condition",
  "diagnosis_reasoning": "2-3 sentences explaining why this is the most likely diagnosis",
  "confidence": "High / Medium / Low",
  "differential_diagnoses": [
    {{"name": "Condition name", "reason": "Brief reason why it must be considered"}},
    {{"name": "Condition name", "reason": "Brief reason"}},
    {{"name": "Condition name", "reason": "Brief reason"}}
  ],
  "red_flags": ["flag 1", "flag 2"],
  "treatment": {{
    "acute":      {{"phase": "Acute Phase (Week 1-2)",    "goals": "Goals for this phase", "interventions": ["intervention 1", "intervention 2", "intervention 3"]}},
    "recovery":   {{"phase": "Recovery Phase (Week 3-6)", "goals": "Goals for this phase", "interventions": ["intervention 1", "intervention 2", "intervention 3"]}},
    "functional": {{"phase": "Functional Phase (Week 7+)","goals": "Goals for this phase", "interventions": ["intervention 1", "intervention 2", "intervention 3"]}}
  }},
  "home_exercises": [
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}},
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}},
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}},
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}}
  ],
  "referral": {{"needed": "Yes / No", "reason": "Explanation or null"}},
  "follow_up": "Recommended follow-up timeframe"
}}"""

    with st.spinner("Analyzing patient data..."):
        try:
            token = st.secrets["DATABRICKS_TOKEN"]
            response = requests.post(
                url="https://dbc-c0c5e61a-9d9c.cloud.databricks.com/ai-gateway/mlflow/v1/chat/completions",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"model": "databricks-gpt-oss-120b", "max_tokens": 3000,
                      "messages": [{"role": "user", "content": prompt}]}
            )
            result_api = response.json()

            if "choices" in result_api:
                content = result_api["choices"][0]["message"]["content"]
                if isinstance(content, list):
                    raw = " ".join(b["text"] for b in content if b.get("type") == "text")
                else:
                    raw = content
                clean = raw.replace("```json", "").replace("```", "").strip()
                start = clean.find("{")
                end   = clean.rfind("}") + 1
                if start != -1 and end > start:
                    clean = clean[start:end]
                data = json.loads(clean)

                # ── RESULTS ───────────────────────────────────────
                st.markdown("""
                <div style="background:linear-gradient(135deg,#1a3a5c,#2e6da4);padding:16px 24px;
                            border-radius:10px;margin-bottom:20px;margin-top:8px;">
                    <div style="color:white;font-size:18px;font-weight:700;">📋 AI Assessment Results</div>
                </div>
                """, unsafe_allow_html=True)

                conf = data.get("confidence", "High")
                conf_bg = {"High": "#1a3a5c", "Medium": "#2e6da4", "Low": "#6699cc"}.get(conf, "#1a3a5c")
                st.markdown(f"""
                <div style="background:#eaf1fb;border:1px solid #b8cfe8;border-radius:10px;padding:20px;margin-bottom:16px;">
                    <div style="font-size:11px;font-weight:700;color:#2e6da4;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Primary Diagnosis</div>
                    <div style="font-size:22px;font-weight:700;color:#1a3a5c;margin-bottom:8px;">{data.get('primary_diagnosis','')}</div>
                    <div style="font-size:14px;color:#3a5a7c;line-height:1.6;margin-bottom:12px;">{data.get('diagnosis_reasoning','')}</div>
                    <span style="background:{conf_bg};color:white;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;">Confidence: {conf}</span>
                </div>
                """, unsafe_allow_html=True)

                red_flags = data.get("red_flags", [])
                if red_flags:
                    st.markdown(f"""
                    <div style="background:#dce8f5;border:1px solid #1a3a5c;border-radius:8px;padding:14px 18px;margin-bottom:16px;">
                        <div style="font-weight:700;color:#1a3a5c;margin-bottom:6px;">⚠️ Red Flags Identified</div>
                        <ul style="margin:0;padding-left:18px;color:#1a3a5c;font-size:14px;">{"".join(f"<li>{f}</li>" for f in red_flags)}</ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background:#eaf1fb;border:1px solid #b8cfe8;border-radius:8px;padding:12px 18px;margin-bottom:16px;color:#1a3a5c;font-size:14px;">
                        ✓ No red flags identified
                    </div>
                    """, unsafe_allow_html=True)

                col_diag, col_ref = st.columns(2)
                with col_diag:
                    st.markdown("""<div style="font-size:11px;font-weight:700;color:#2e6da4;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Differential Diagnoses</div>""", unsafe_allow_html=True)
                    for i, diff in enumerate(data.get("differential_diagnoses", []), 1):
                        st.markdown(f"""
                        <div style="background:#f4f7fb;border:1px solid #b8cfe8;border-left:4px solid #1a3a5c;border-radius:6px;padding:12px;margin-bottom:8px;">
                            <div style="font-weight:700;color:#1a3a5c;font-size:14px;">{i}. {diff.get('name','')}</div>
                            <div style="color:#3a5a7c;font-size:13px;margin-top:4px;">{diff.get('reason','')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with col_ref:
                    st.markdown("""<div style="font-size:11px;font-weight:700;color:#2e6da4;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Referral & Follow-up</div>""", unsafe_allow_html=True)
                    referral = data.get("referral", {})
                    ref_icon = "⚠️ Referral needed" if referral.get("needed") == "Yes" else "✓ No referral needed"
                    ref_reason = f"<div style='font-size:13px;color:#3a5a7c;margin-top:6px;'>{referral.get('reason','')}</div>" if referral.get("needed") == "Yes" else ""
                    st.markdown(f"""
                    <div style="background:#eaf1fb;border:1px solid #b8cfe8;border-left:4px solid #1a3a5c;border-radius:6px;padding:12px;margin-bottom:8px;">
                        <div style="font-weight:700;color:#1a3a5c;font-size:14px;">{ref_icon}</div>{ref_reason}
                    </div>
                    <div style="background:#eaf1fb;border:1px solid #b8cfe8;border-left:4px solid #2e6da4;border-radius:6px;padding:12px;">
                        <div style="font-size:11px;font-weight:700;color:#2e6da4;text-transform:uppercase;letter-spacing:1px;">Follow-up</div>
                        <div style="font-size:14px;color:#1a3a5c;margin-top:4px;">{data.get('follow_up','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='margin:20px 0 8px 0'></div>", unsafe_allow_html=True)
                st.markdown("""<div style="font-size:11px;font-weight:700;color:#2e6da4;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Treatment Plan</div>""", unsafe_allow_html=True)
                treatment = data.get("treatment", {})
                tab1, tab2, tab3 = st.tabs(["Acute Phase", "Recovery Phase", "Functional Phase"])
                for tab, phase_key in zip([tab1, tab2, tab3], ["acute", "recovery", "functional"]):
                    with tab:
                        phase = treatment.get(phase_key, {})
                        st.markdown(f"""<div style="background:#eaf1fb;border-radius:6px;padding:12px;margin-bottom:12px;font-size:14px;color:#1a3a5c;"><strong>Goal:</strong> {phase.get('goals','')}</div>""", unsafe_allow_html=True)
                        for item in phase.get("interventions", []):
                            st.markdown(f"""<div style="padding:8px 12px;border-left:3px solid #2e6da4;margin-bottom:6px;font-size:14px;color:#3a5a7c;background:#f4f7fb;border-radius:0 6px 6px 0;">{item}</div>""", unsafe_allow_html=True)

                st.markdown("<div style='margin:20px 0 8px 0'></div>", unsafe_allow_html=True)
                st.markdown("""<div style="font-size:11px;font-weight:700;color:#2e6da4;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Home Exercise Program</div>""", unsafe_allow_html=True)
                exercises = data.get("home_exercises", [])
                cols = st.columns(len(exercises)) if exercises else []
                for col, ex in zip(cols, exercises):
                    with col:
                        st.markdown(f"""
                        <div style="background:#eaf1fb;border:1px solid #b8cfe8;border-top:4px solid #1a3a5c;border-radius:8px;padding:16px;">
                            <div style="font-weight:700;color:#1a3a5c;font-size:14px;margin-bottom:8px;">{ex.get('name','')}</div>
                            <div style="font-size:13px;color:#3a5a7c;line-height:1.5;margin-bottom:10px;">{ex.get('description','')}</div>
                            <div style="font-size:12px;color:#2e6da4;font-weight:600;">🕐 {ex.get('frequency','')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("""
                <div style="background:#dce8f5;border:1px solid #b8cfe8;border-radius:8px;padding:12px 18px;font-size:13px;color:#1a3a5c;margin-top:20px;">
                    ⚠️ AI-assisted screening only. Must be reviewed by a qualified physiotherapist.
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("API Error: " + json.dumps(result_api, indent=2))

        except json.JSONDecodeError:
            st.error("Could not parse AI response. Raw output:")
            st.code(clean)
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
