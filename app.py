import streamlit as st
import requests
import json

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="PhysioAI Assessment",
    page_icon="🏥",
    layout="wide"
)

# ── INJECT VOICE RECOGNITION SCRIPT ──────────────────────
# This script listens for mic button clicks anywhere on the page
# and fills the nearest Streamlit input/textarea via DOM manipulation
st.markdown("""
<style>
input[type=text], textarea { autocomplete: off !important; }
.mic-btn {
    background: #f0f2f6; border: 1px solid #ccc; border-radius: 6px;
    cursor: pointer; font-size: 16px; padding: 2px 8px;
    margin-left: 4px; vertical-align: middle;
}
.mic-btn.recording { background: #ffe0e0 !important; }
</style>

<script>
var activeRec = null;

function fillStreamlitField(fieldKey, text) {
    // Find the Streamlit input by its aria-label or data-testid
    var inputs = window.parent.document.querySelectorAll(
        'input[type="text"], textarea'
    );
    for (var i = 0; i < inputs.length; i++) {
        var el = inputs[i];
        // Match by placeholder or label text
        if (el.getAttribute('data-field-key') === fieldKey ||
            el.placeholder && el.placeholder.includes(fieldKey)) {
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.parent.HTMLInputElement.prototype, 'value'
            ) || Object.getOwnPropertyDescriptor(
                window.parent.HTMLTextAreaElement.prototype, 'value'
            );
            nativeInputValueSetter.set.call(el, text);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            break;
        }
    }
}

function startMic(targetId, statusId, btnId) {
    if (activeRec) { activeRec.stop(); return; }

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        document.getElementById(statusId).innerText = '⚠️ Use Chrome or Edge';
        return;
    }

    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    var rec = new SR();
    rec.lang = navigator.language || 'en-US';
    rec.continuous = true;
    rec.interimResults = true;
    activeRec = rec;

    var btn = document.getElementById(btnId);
    var status = document.getElementById(statusId);
    var target = document.getElementById(targetId);
    var existing = target ? target.value : '';

    if (btn) { btn.innerText = '⏹'; btn.classList.add('recording'); }
    if (status) status.innerText = '🔴 Listening... click ⏹ to stop';

    rec.onresult = function(e) {
        var interim = '', final = '';
        for (var i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) final += e.results[i][0].transcript;
            else interim += e.results[i][0].transcript;
        }
        if (target) {
            var sep = (existing && !existing.endsWith(' ')) ? ' ' : '';
            target.value = existing + sep + final;
            if (final) existing = target.value;
        }
        if (status) status.innerText = interim ? '💬 ' + interim : '🔴 Listening...';
    };

    rec.onend = function() {
        activeRec = null;
        if (btn) { btn.innerText = '🎤'; btn.classList.remove('recording'); }
        if (status) { status.innerText = '✅ Done'; setTimeout(function(){ status.innerText=''; }, 2000); }
    };

    rec.onerror = function(e) {
        activeRec = null;
        if (btn) { btn.innerText = '🎤'; btn.classList.remove('recording'); }
        if (status) status.innerText = '⚠️ ' + e.error;
    };

    rec.start();
}
</script>
""", unsafe_allow_html=True)


# ── MIC FIELD HELPER ─────────────────────────────────────
def mic_field(label, key, placeholder="", multiline=False, height=80):
    """Renders a labeled field with a 🎤 mic button using inline HTML + st input."""
    uid = key.replace("_", "")

    # The mic button + status sits above the Streamlit field
    st.markdown(f"""
        <div style="display:flex; align-items:center; margin-bottom:2px;">
            <span style="font-size:14px; font-weight:600; color:#31333f; flex:1">{label}</span>
            <button class="mic-btn" id="btn_{uid}"
                onclick="startMic('input_{uid}', 'status_{uid}', 'btn_{uid}')"
                title="Click to speak">🎤</button>
        </div>
        <div id="status_{uid}" style="font-size:11px; color:#888; height:14px; margin-bottom:2px;"></div>
        <div id="wrapper_{uid}">
    """, unsafe_allow_html=True)

    if multiline:
        val = st.text_area(
            label, key=key, placeholder=placeholder,
            height=height, label_visibility="collapsed"
        )
    else:
        val = st.text_input(
            label, key=key, placeholder=placeholder,
            label_visibility="collapsed"
        )

    # Inject id onto the rendered input so the JS can find it
    st.markdown(f"""
        </div>
        <script>
        (function() {{
            var wrapper = document.getElementById('wrapper_{uid}');
            if (wrapper) {{
                var el = wrapper.querySelector('input, textarea');
                if (el) el.id = 'input_{uid}';
            }}
        }})();
        </script>
    """, unsafe_allow_html=True)

    return val


# ── TITLE ─────────────────────────────────────────────────
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

    occupation = mic_field("Occupation", "occupation",
        placeholder="e.g. Office worker, nurse, construction worker...")
    physical_activity = mic_field("Physical Activity Level", "physical_activity",
        placeholder="e.g. Sedentary, walks daily, plays football 2x/week...")

with col_s2:
    st.subheader("② Main Complaint")
    main_complaint = mic_field("Describe the patient's main problem *", "main_complaint",
        placeholder="e.g. Difficulty walking after knee surgery, loss of balance, limited shoulder mobility...",
        multiline=True, height=120)
    body_area = mic_field("Body Area Affected *", "body_area",
        placeholder="e.g. Left knee, lower back, right shoulder, both hands...")
    problem_duration = mic_field("How long has this problem existed?", "problem_duration",
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

    aggravating = mic_field("What makes it worse?", "aggravating",
        placeholder="e.g. Walking, sitting too long, lifting, certain movements...")
    relieving = mic_field("What makes it better?", "relieving",
        placeholder="e.g. Rest, heat, ice, specific positions...")

with col_s4:
    st.subheader("④ Clinical History")
    previous_history = mic_field("Previous injuries, surgeries or medical conditions",
        "previous_history",
        placeholder="e.g. Knee surgery 2022, diabetes, herniated disc, stroke...",
        multiline=True, height=100)
    current_treatments = mic_field("Current treatments or medications",
        "current_treatments",
        placeholder="e.g. Taking ibuprofen, wearing a brace, doing home exercises...",
        multiline=True, height=80)
    additional_info = mic_field("Any other relevant information",
        "additional_info",
        placeholder="e.g. Patient goals, sport they want to return to...",
        multiline=True, height=80)

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
    if not (main_complaint or "").strip() or not (body_area or "").strip():
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
    "acute": {{
      "phase": "Acute Phase (Week 1-2)",
      "goals": "Goals for this phase",
      "interventions": ["intervention 1", "intervention 2", "intervention 3"]
    }},
    "recovery": {{
      "phase": "Recovery Phase (Week 3-6)",
      "goals": "Goals for this phase",
      "interventions": ["intervention 1", "intervention 2", "intervention 3"]
    }},
    "functional": {{
      "phase": "Functional Phase (Week 7+)",
      "goals": "Goals for this phase",
      "interventions": ["intervention 1", "intervention 2", "intervention 3"]
    }}
  }},
  "home_exercises": [
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}},
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}},
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}},
    {{"name": "Exercise name", "description": "How to perform it", "frequency": "How often"}}
  ],
  "referral": {{
    "needed": "Yes / No",
    "reason": "Explanation or null"
  }},
  "follow_up": "Recommended follow-up timeframe"
}}"""

        with st.spinner("🤖 Analyzing patient data... please wait"):
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
                    data = json.loads(clean)

                    # ── RESULTS ───────────────────────────────────────
                    st.divider()
                    st.subheader("📋 AI Assessment Results")

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

                    red_flags = data.get("red_flags", [])
                    if red_flags:
                        st.error("🚨 **Red Flags Identified:**")
                        for flag in red_flags:
                            st.markdown(f"- ⚠️ {flag}")
                    else:
                        st.success("✅ No red flags identified")

                    st.markdown("---")
                    col_diag, col_ref = st.columns(2)

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

                    with col_ref:
                        st.markdown("### 📅 Referral & Follow-up")
                        referral = data.get("referral", {})
                        if referral.get("needed") == "Yes":
                            st.warning(f"**Referral needed:** {referral.get('reason', '')}")
                        else:
                            st.success("**No referral needed**")
                        st.info(f"**Follow-up:** {data.get('follow_up', '')}")

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
                st.error("Could not parse AI response. Please try again.")
                st.code(raw)
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
