import streamlit as st
import requests
import json

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="PhysioAI Assessment",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 PhysioAI — Clinical Assessment Tool")
st.caption("AI-assisted physiotherapy screening powered by Databricks GPT")
st.divider()

# ── ROW 1: SECTIONS 1 AND 2 ──────────────────────────────
col_s1, col_s2 = st.columns(2)

with col_s1:
    st.subheader("① Patient Profile")
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
    st.subheader("② Main Complaint")
    main_complaint = st.text_area("Describe the patient's main problem *", key="main_complaint",
        placeholder="e.g. Difficulty walking after knee surgery, loss of balance, limited shoulder mobility...",
        height=120)
    body_area = st.text_input("Body Area Affected *", key="body_area",
        placeholder="e.g. Left knee, lower back, right shoulder, both hands...")
    problem_duration = st.text_input("How long has this problem existed?", key="problem_duration",
        placeholder="e.g. 2 weeks, 6 months, since birth...")
    problem_onset = st.selectbox("How did the problem start?", [
        "Sudden (accident / injury)", "Gradual (developed over time)",
        "After surgery", "After illness", "Unknown / no clear cause"
    ])

st.divider()

# ── ROW 2: SECTIONS 3 AND 4 ──────────────────────────────
col_s3, col_s4 = st.columns(2)

with col_s3:
    st.subheader("③ Symptoms")
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
    st.subheader("④ Clinical History")
    previous_history = st.text_area("Previous injuries, surgeries or medical conditions",
        key="previous_history",
        placeholder="e.g. Knee surgery 2022, diabetes, herniated disc, stroke...",
        height=100)
    current_treatments = st.text_area("Current treatments or medications",
        key="current_treatments",
        placeholder="e.g. Taking ibuprofen, wearing a brace, home exercises...",
        height=80)
    additional_info = st.text_area("Any other relevant information",
        key="additional_info",
        placeholder="e.g. Patient goals, sport they want to return to...",
        height=80)

st.divider()

# ── LANGUAGE + BUTTON ─────────────────────────────────────
st.subheader("⑤ Response Language")
language = st.radio(
    "Select the language for the AI assessment report:",
    options=["English", "Spanish", "Finnish"],
    horizontal=True
)
run = st.button("🔍 Run AI Assessment", type="primary")

# ── AI CALL ───────────────────────────────────────────────
if run:
    main_complaint = st.session_state.get("main_complaint", "")
    body_area      = st.session_state.get("body_area", "")
    occupation     = st.session_state.get("occupation", "")
    physical_activity = st.session_state.get("physical_activity", "")
    problem_duration  = st.session_state.get("problem_duration", "")
    aggravating    = st.session_state.get("aggravating", "")
    relieving      = st.session_state.get("relieving", "")
    previous_history  = st.session_state.get("previous_history", "")
    current_treatments = st.session_state.get("current_treatments", "")
    additional_info   = st.session_state.get("additional_info", "")

    if not main_complaint.strip() or not body_area.strip():
        st.error("⚠️ Please fill in the Main Complaint and Body Area Affected fields.")
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

        with st.spinner("🤖 Analyzing patient data... please wait"):
            try:
                token = st.secrets["DATABRICKS_TOKEN"]
                response = requests.post(
                    url="https://dbc-c0c5e61a-9d9c.cloud.databricks.com/ai-gateway/mlflow/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "databricks-gpt-oss-120b",
                        "max_tokens": 3000,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                result = response.json()

                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]

                    # Handle list of blocks (reasoning + text)
                    if isinstance(content, list):
                        raw = " ".join(b["text"] for b in content if b.get("type") == "text")
                    else:
                        raw = content

                    # Clean markdown fences
                    clean = raw.replace("```json", "").replace("```", "").strip()

                    # Extract JSON object — find first { to last }
                    start = clean.find("{")
                    end   = clean.rfind("}") + 1
                    if start != -1 and end > start:
                        clean = clean[start:end]

                    data = json.loads(clean)

                    # ── RESULTS ───────────────────────────────────────
                    st.divider()
                    st.subheader("📋 AI Assessment Results")

                    # Primary diagnosis
                    confidence_color = {"High": "green", "Medium": "orange", "Low": "red"}.get(
                        data.get("confidence", ""), "green")
                    st.markdown(f"""
                    <div style="background:#f0f8ff; padding:20px; border-radius:10px;
                                border-left:6px solid #1f77b4; margin-bottom:16px">
                        <h2 style="margin:0; color:#1f77b4;">🔍 {data.get('primary_diagnosis', '')}</h2>
                        <p style="margin:8px 0 4px 0; color:#333;">{data.get('diagnosis_reasoning', '')}</p>
                        <span style="background:{confidence_color}; color:white; padding:3px 12px;
                                     border-radius:20px; font-size:13px;">
                            Confidence: {data.get('confidence', '')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Red flags
                    red_flags = data.get("red_flags", [])
                    if red_flags:
                        st.error("🚨 **Red Flags Identified:**")
                        for flag in red_flags:
                            st.markdown(f"- ⚠️ {flag}")
                    else:
                        st.success("✅ No red flags identified")

                    st.markdown("---")
                    col_diag, col_ref = st.columns(2)

                    # Differentials
                    with col_diag:
                        st.markdown("### 🔄 Differential Diagnoses")
                        for i, diff in enumerate(data.get("differential_diagnoses", []), 1):
                            st.markdown(f"""
                            <div style="background:#f9f9f9; border-radius:8px; padding:12px;
                                        margin-bottom:8px; border-left:4px solid #aaa;">
                                <strong>{i}. {diff.get('name', '')}</strong><br>
                                <span style="color:#555; font-size:13px;">{diff.get('reason', '')}</span>
                            </div>
                            """, unsafe_allow_html=True)

                    # Referral
                    with col_ref:
                        st.markdown("### 📅 Referral & Follow-up")
                        referral = data.get("referral", {})
                        if referral.get("needed") == "Yes":
                            st.warning(f"**Referral needed:** {referral.get('reason', '')}")
                        else:
                            st.success("**No referral needed**")
                        st.info(f"**Follow-up:** {data.get('follow_up', '')}")

                    # Treatment plan
                    st.markdown("---")
                    st.markdown("### 💊 Treatment Plan")
                    treatment = data.get("treatment", {})
                    tab1, tab2, tab3 = st.tabs(["🔴 Acute Phase", "🟡 Recovery Phase", "🟢 Functional Phase"])
                    for tab, phase_key in zip([tab1, tab2, tab3], ["acute", "recovery", "functional"]):
                        with tab:
                            phase = treatment.get(phase_key, {})
                            st.markdown(f"**Goals:** {phase.get('goals', '')}")
                            st.markdown("**Interventions:**")
                            for item in phase.get("interventions", []):
                                st.markdown(f"- {item}")

                    # Home exercises
                    st.markdown("---")
                    st.markdown("### 🏃 Home Exercise Program")
                    exercises = data.get("home_exercises", [])
                    cols = st.columns(len(exercises)) if exercises else []
                    for col, ex in zip(cols, exercises):
                        with col:
                            st.markdown(f"""
                            <div style="background:#f0fff0; border-radius:10px; padding:14px;
                                        border-top:4px solid #2ca02c;">
                                <strong>💪 {ex.get('name', '')}</strong><br><br>
                                <span style="font-size:13px;">{ex.get('description', '')}</span><br><br>
                                <span style="font-size:12px; color:#2ca02c;">🕐 {ex.get('frequency', '')}</span>
                            </div>
                            """, unsafe_allow_html=True)

                    st.divider()
                    st.warning("⚠️ AI-assisted screening only. Must be reviewed by a qualified physiotherapist.")

                else:
                    st.error("API Error: " + json.dumps(result, indent=2))

            except json.JSONDecodeError:
                st.error("Could not parse AI response. Raw output:")
                st.code(clean)
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
