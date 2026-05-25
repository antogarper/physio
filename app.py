import streamlit as st
import requests
import json

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="PhysioAI Assessment",
    page_icon="🏥",
    layout="wide"
)

# ── GLOBAL STYLE — elegant blue palette ──────────────────
st.markdown("""
<style>
/* ── Fonts & base ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ── Page background ── */
.stApp { background-color: #f4f7fb; }

/* ── Header ── */
h1 { color: #1a3a5c !important; }

/* ── Section subheaders ── */
h3 { color: #1a3a5c !important; font-size: 15px !important; 
     text-transform: uppercase; letter-spacing: 1px; }

/* ── Input fields ── */
input[type=text], input[type=number], textarea, select,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    border: 1px solid #b8cfe8 !important;
    border-radius: 6px !important;
    background: #ffffff !important;
}
input:focus, textarea:focus {
    border-color: #1a3a5c !important;
    box-shadow: 0 0 0 2px rgba(26,58,92,0.15) !important;
}

/* ── Labels ── */
label { color: #1a3a5c !important; font-weight: 600 !important; font-size: 13px !important; }

/* ── Slider ── */
div[data-testid="stSlider"] div[role="slider"] { background: #1a3a5c !important; }
div[data-testid="stSlider"] div[data-testid="stTickBar"] { background: #b8cfe8 !important; }

/* ── Radio buttons ── */
div[data-testid="stRadio"] label { font-weight: 400 !important; color: #1a3a5c !important; }

/* ── Primary button ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #1a3a5c !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    transition: background 0.2s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #0f2540 !important;
}

/* ── Checkbox ── */
input[type="checkbox"]:checked { accent-color: #1a3a5c !important; }

/* ── Tabs ── */
div[data-testid="stTabs"] button {
    color: #1a3a5c !important;
    font-weight: 600 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    border-bottom: 3px solid #1a3a5c !important;
    color: #1a3a5c !important;
}

/* ── Divider ── */
hr { border-color: #b8cfe8 !important; }

/* ── Spinner ── */
div[data-testid="stSpinner"] { color: #1a3a5c !important; }
</style>
""", unsafe_allow_html=True)

# ── TITLE ─────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a3a5c,#2e6da4); padding:28px 32px;
            border-radius:12px; margin-bottom:28px;">
    <span style="display:block; color:#ffffff !important; font-size:26px; font-weight:700; text-shadow:0 1px 4px rgba(0,0,0,0.4); margin-bottom:6px;">🏥 PhysioAI — Clinical Assessment Tool</span>
    <span style="display:block; color:#b8d4f0 !important; font-size:14px;">AI-assisted physiotherapy screening</span>
</div>
""", unsafe_allow_html=True)

# ── SECTION HEADER HELPER ─────────────────────────────────
def section(title):
    st.markdown(f"""
    <div style="background:#1a3a5c; color:white; padding:8px 16px;
                border-radius:6px; font-size:13px; font-weight:700;
                letter-spacing:1px; margin-bottom:14px;">
        {title}
    </div>
    """, unsafe_allow_html=True)

# ── ROW 1: SECTIONS 1 AND 2 ──────────────────────────────
col_s1, col_s2 = st.columns(2)

with col_s1:
    section("① PATIENT PROFILE")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age (years)", min_value=1, max_value=120, value=45)
    with c2:
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
    c3, c4 = st.columns(2)
    with c3:
        weight = st.number_input("Weight (kg)", min_value=1, max_value=300, value=68)
    with c4:
        height_val = st.number_input("Height (cm)", min_value=50, max_value=250, value=165)
    occupation = st.text_input("Occupation", key="occupation",
        placeholder="e.g. Office worker, nurse, construction worker...")
    physical_activity = st.text_input("Physical Activity Level", key="physical_activity",
        placeholder="e.g. Sedentary, walks daily, plays football 2x/week...")

with col_s2:
    section("② MAIN COMPLAINT")
    main_complaint = st.text_input("Describe the patient's main problem *", key="main_complaint",
        placeholder="e.g. Difficulty walking after knee surgery, loss of balance...")
    body_area = st.text_input("Body Area Affected *", key="body_area",
        placeholder="e.g. Left knee, lower back, right shoulder, both hands...")
    problem_duration = st.text_input("How long has this problem existed?", key="problem_duration",
        placeholder="e.g. 2 weeks, 6 months, since birth...")
    problem_onset = st.selectbox("How did the problem start?", [
        "Sudden (accident / injury)", "Gradual (developed over time)",
        "After surgery", "After illness", "Unknown / no clear cause"
    ])

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

# ── ROW 2: SECTIONS 3 AND 4 ──────────────────────────────
col_s3, col_s4 = st.columns(2)

with col_s3:
    section("③ SYMPTOMS")
    has_pain = st.checkbox("Pain is present", value=True)
    if has_pain:
        pain_intensity = st.slider("Pain Intensity (0 = no pain, 10 = worst possible)", 0, 10, 5)
    else:
        pain_intensity = 0
    aggravating = st.text_input("What makes it worse?", key="aggravating",
        placeholder="e.g. Walking, sitting too long, lifting, certain movements...")
    relieving = st.text_input("What makes it better?", key="relieving",
        placeholder="e.g. Rest, heat, ice, specific positions...")

with col_s4:
    section("④ CLINICAL HISTORY")
    previous_history = st.text_input("Previous injuries, surgeries or medical conditions",
        key="previous_history",
        placeholder="e.g. Knee surgery 2022, diabetes, herniated disc, stroke...")
    current_treatments = st.text_input("Current treatments or medications",
        key="current_treatments",
        placeholder="e.g. Taking ibuprofen, wearing a brace, home exercises...")
    additional_info = st.text_input("Any other relevant information",
        key="additional_info",
        placeholder="e.g. Patient goals, sport they want to return to...")

st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

# ── LANGUAGE + BUTTON ─────────────────────────────────────
section("⑤ RESPONSE LANGUAGE")
language = st.radio(
    "Select the language for the AI assessment report:",
    options=["English", "Spanish", "Finnish"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)
run = st.button("🔍 Run AI Assessment", type="primary")

# ── AI CALL ───────────────────────────────────────────────
if run:
    main_complaint    = st.session_state.get("main_complaint", "")
    body_area         = st.session_state.get("body_area", "")
    occupation        = st.session_state.get("occupation", "")
    physical_activity = st.session_state.get("physical_activity", "")
    problem_duration  = st.session_state.get("problem_duration", "")
    aggravating       = st.session_state.get("aggravating", "")
    relieving         = st.session_state.get("relieving", "")
    previous_history  = st.session_state.get("previous_history", "")
    current_treatments= st.session_state.get("current_treatments", "")
    additional_info   = st.session_state.get("additional_info", "")

    if not main_complaint.strip() or not body_area.strip():
        st.markdown("""
        <div style="background:#dce8f5; border-left:4px solid #1a3a5c; border-radius:6px;
                    padding:12px 16px; color:#1a3a5c; font-size:14px; margin-top:12px;">
            ⚠️ Please fill in the <strong>Main Complaint</strong> and <strong>Body Area Affected</strong> fields.
        </div>
        """, unsafe_allow_html=True)
    else:
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
                result = response.json()

                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
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

                    # ── RESULTS HEADER ────────────────────────────────
                    st.markdown("<div style='margin:24px 0 8px 0'></div>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style="background:linear-gradient(135deg,#1a3a5c,#2e6da4); padding:16px 24px;
                                border-radius:10px; margin-bottom:20px;">
                        <h2 style="color:white; margin:0; font-size:18px;">📋 AI Assessment Results</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── PRIMARY DIAGNOSIS ─────────────────────────────
                    conf = data.get("confidence", "High")
                    conf_bg = {"High": "#1a3a5c", "Medium": "#2e6da4", "Low": "#6699cc"}.get(conf, "#1a3a5c")
                    st.markdown(f"""
                    <div style="background:#eaf1fb; border:1px solid #b8cfe8; border-radius:10px;
                                padding:20px; margin-bottom:16px;">
                        <div style="font-size:11px; font-weight:700; color:#2e6da4; letter-spacing:2px;
                                    text-transform:uppercase; margin-bottom:8px;">Primary Diagnosis</div>
                        <div style="font-size:22px; font-weight:700; color:#1a3a5c; margin-bottom:8px;">
                            {data.get('primary_diagnosis', '')}
                        </div>
                        <div style="font-size:14px; color:#3a5a7c; line-height:1.6; margin-bottom:12px;">
                            {data.get('diagnosis_reasoning', '')}
                        </div>
                        <span style="background:{conf_bg}; color:white; padding:4px 14px;
                                     border-radius:20px; font-size:12px; font-weight:600;">
                            Confidence: {conf}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── RED FLAGS ─────────────────────────────────────
                    red_flags = data.get("red_flags", [])
                    if red_flags:
                        flags_html = "".join(f"<li>{f}</li>" for f in red_flags)
                        st.markdown(f"""
                        <div style="background:#dce8f5; border:1px solid #1a3a5c; border-radius:8px;
                                    padding:14px 18px; margin-bottom:16px;">
                            <div style="font-weight:700; color:#1a3a5c; margin-bottom:6px;">
                                ⚠️ Red Flags Identified
                            </div>
                            <ul style="margin:0; padding-left:18px; color:#1a3a5c; font-size:14px;">
                                {flags_html}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background:#eaf1fb; border:1px solid #b8cfe8; border-radius:8px;
                                    padding:12px 18px; margin-bottom:16px; color:#1a3a5c; font-size:14px;">
                            ✓ No red flags identified
                        </div>
                        """, unsafe_allow_html=True)

                    # ── DIFFERENTIALS + REFERRAL ──────────────────────
                    col_diag, col_ref = st.columns(2)

                    with col_diag:
                        st.markdown("""
                        <div style="font-size:11px; font-weight:700; color:#2e6da4;
                                    letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                            Differential Diagnoses
                        </div>""", unsafe_allow_html=True)
                        for i, diff in enumerate(data.get("differential_diagnoses", []), 1):
                            st.markdown(f"""
                            <div style="background:#f4f7fb; border:1px solid #b8cfe8;
                                        border-left:4px solid #1a3a5c; border-radius:6px;
                                        padding:12px; margin-bottom:8px;">
                                <div style="font-weight:700; color:#1a3a5c; font-size:14px;">
                                    {i}. {diff.get('name', '')}
                                </div>
                                <div style="color:#3a5a7c; font-size:13px; margin-top:4px;">
                                    {diff.get('reason', '')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    with col_ref:
                        st.markdown("""
                        <div style="font-size:11px; font-weight:700; color:#2e6da4;
                                    letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                            Referral & Follow-up
                        </div>""", unsafe_allow_html=True)
                        referral = data.get("referral", {})
                        ref_bg = "#dce8f5" if referral.get("needed") == "Yes" else "#eaf1fb"
                        ref_icon = "⚠️ Referral needed" if referral.get("needed") == "Yes" else "✓ No referral needed"
                        ref_reason = f"<div style='font-size:13px; color:#3a5a7c; margin-top:6px;'>{referral.get('reason','')}</div>" if referral.get("needed") == "Yes" else ""
                        st.markdown(f"""
                        <div style="background:{ref_bg}; border:1px solid #b8cfe8;
                                    border-left:4px solid #1a3a5c; border-radius:6px;
                                    padding:12px; margin-bottom:8px;">
                            <div style="font-weight:700; color:#1a3a5c; font-size:14px;">{ref_icon}</div>
                            {ref_reason}
                        </div>
                        <div style="background:#eaf1fb; border:1px solid #b8cfe8;
                                    border-left:4px solid #2e6da4; border-radius:6px; padding:12px;">
                            <div style="font-size:11px; font-weight:700; color:#2e6da4;
                                        text-transform:uppercase; letter-spacing:1px;">Follow-up</div>
                            <div style="font-size:14px; color:#1a3a5c; margin-top:4px;">
                                {data.get('follow_up', '')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # ── TREATMENT PLAN ────────────────────────────────
                    st.markdown("<div style='margin:20px 0 8px 0'></div>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style="font-size:11px; font-weight:700; color:#2e6da4;
                                letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                        Treatment Plan
                    </div>""", unsafe_allow_html=True)

                    treatment = data.get("treatment", {})
                    tab1, tab2, tab3 = st.tabs(["Acute Phase", "Recovery Phase", "Functional Phase"])
                    for tab, phase_key in zip([tab1, tab2, tab3], ["acute", "recovery", "functional"]):
                        with tab:
                            phase = treatment.get(phase_key, {})
                            st.markdown(f"""
                            <div style="background:#eaf1fb; border-radius:6px; padding:12px;
                                        margin-bottom:12px; font-size:14px; color:#1a3a5c;">
                                <strong>Goal:</strong> {phase.get('goals', '')}
                            </div>
                            """, unsafe_allow_html=True)
                            for item in phase.get("interventions", []):
                                st.markdown(f"""
                                <div style="padding:8px 12px; border-left:3px solid #2e6da4;
                                            margin-bottom:6px; font-size:14px; color:#3a5a7c;
                                            background:#f4f7fb; border-radius:0 6px 6px 0;">
                                    {item}
                                </div>
                                """, unsafe_allow_html=True)

                    # ── HOME EXERCISES ────────────────────────────────
                    st.markdown("<div style='margin:20px 0 8px 0'></div>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style="font-size:11px; font-weight:700; color:#2e6da4;
                                letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                        Home Exercise Program
                    </div>""", unsafe_allow_html=True)

                    exercises = data.get("home_exercises", [])
                    cols = st.columns(len(exercises)) if exercises else []
                    for col, ex in zip(cols, exercises):
                        with col:
                            st.markdown(f"""
                            <div style="background:#eaf1fb; border:1px solid #b8cfe8;
                                        border-top:4px solid #1a3a5c; border-radius:8px; padding:16px;">
                                <div style="font-weight:700; color:#1a3a5c; font-size:14px;
                                            margin-bottom:8px;">
                                    {ex.get('name', '')}
                                </div>
                                <div style="font-size:13px; color:#3a5a7c; line-height:1.5;
                                            margin-bottom:10px;">
                                    {ex.get('description', '')}
                                </div>
                                <div style="font-size:12px; color:#2e6da4; font-weight:600;">
                                    🕐 {ex.get('frequency', '')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    # ── DISCLAIMER ────────────────────────────────────
                    st.markdown("<div style='margin:20px 0 0 0'></div>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style="background:#dce8f5; border:1px solid #b8cfe8; border-radius:8px;
                                padding:12px 18px; font-size:13px; color:#1a3a5c;">
                        ⚠️ AI-assisted screening only. Must be reviewed by a qualified physiotherapist.
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <div style="background:#dce8f5; border-left:4px solid #1a3a5c; border-radius:6px;
                                padding:12px 16px; color:#1a3a5c; font-size:14px;">
                        API Error: {json.dumps(result, indent=2)}
                    </div>
                    """, unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.error("Could not parse AI response. Raw output:")
                st.code(clean)
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
