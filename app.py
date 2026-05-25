import streamlit as st
import streamlit.components.v1 as components
import requests
import json

st.set_page_config(page_title="PhysioAI Assessment", page_icon="🏥", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
.stApp { background-color: #f4f7fb; }
div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #1a3a5c !important; border: none !important;
    border-radius: 8px !important; color: white !important;
    font-weight: 700 !important; padding: 12px 36px !important;
    font-size: 15px !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover { background-color: #0f2540 !important; }
label { color: #1a3a5c !important; font-weight: 600 !important; font-size: 13px !important; }
div[data-baseweb="input"] input { border: 1px solid #b8cfe8 !important; border-radius: 6px !important; }
div[data-baseweb="input"] input:focus { border-color: #1a3a5c !important; }
</style>
""", unsafe_allow_html=True)

# ── SECTION HEADER ────────────────────────────────────────
def section(title):
    st.markdown(f"""
    <div style="background:#1a3a5c;color:white;padding:8px 14px;border-radius:6px;
                font-size:12px;font-weight:700;letter-spacing:1px;
                text-transform:uppercase;margin-bottom:12px;">{title}</div>
    """, unsafe_allow_html=True)

# ── BANNER ────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a3a5c,#2e6da4);padding:24px 28px;
            border-radius:12px;margin-bottom:24px;">
    <div style="color:#ffffff;font-size:24px;font-weight:700;margin-bottom:4px;">
        🏥 PhysioAI — Clinical Assessment Tool
    </div>
    <div style="color:#b8d4f0;font-size:13px;">AI-assisted physiotherapy screening</div>
</div>
""", unsafe_allow_html=True)

# ── ROW 1 ─────────────────────────────────────────────────
col_s1, col_s2 = st.columns(2)

with col_s1:
    section("① Patient Profile")
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
    occupation        = st.text_input("Occupation", key="occupation", placeholder="e.g. Office worker, nurse...")
    physical_activity = st.text_input("Physical Activity Level", key="physical_activity", placeholder="e.g. Sedentary, walks daily...")

with col_s2:
    section("② Main Complaint")
    main_complaint   = st.text_input("Describe the patient's main problem *", key="main_complaint", placeholder="e.g. Difficulty walking after knee surgery...")
    body_area        = st.text_input("Body Area Affected *", key="body_area", placeholder="e.g. Left knee, lower back, right shoulder...")
    problem_duration = st.text_input("How long has this problem existed?", key="problem_duration", placeholder="e.g. 2 weeks, 6 months...")
    problem_onset    = st.selectbox("How did the problem start?", [
        "Sudden (accident / injury)", "Gradual (developed over time)",
        "After surgery", "After illness", "Unknown / no clear cause"
    ])

st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)

# ── ROW 2 ─────────────────────────────────────────────────
col_s3, col_s4 = st.columns(2)

with col_s3:
    section("③ Symptoms")
    has_pain = st.checkbox("Pain is present", value=True)
    if has_pain:
        pain_intensity = st.slider("Pain Intensity (0 = no pain, 10 = worst possible)", 0, 10, 5)
    else:
        pain_intensity = 0
    aggravating = st.text_input("What makes it worse?", key="aggravating", placeholder="e.g. Walking, sitting too long...")
    relieving   = st.text_input("What makes it better?", key="relieving", placeholder="e.g. Rest, heat, ice...")

with col_s4:
    section("④ Clinical History")
    previous_history   = st.text_input("Previous injuries, surgeries or medical conditions", key="previous_history", placeholder="e.g. Knee surgery 2022, diabetes...")
    current_treatments = st.text_input("Current treatments or medications", key="current_treatments", placeholder="e.g. Taking ibuprofen, wearing a brace...")
    additional_info    = st.text_input("Any other relevant information", key="additional_info", placeholder="e.g. Patient goals, sport they want to return to...")

st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)

# ── LANGUAGE ──────────────────────────────────────────────
section("⑤ Response Language")
language = st.radio("", options=["English", "Spanish", "Finnish"], horizontal=True)

# ── MIC PANEL ─────────────────────────────────────────────
# Single mic panel below the form — user speaks, text shown,
# then they paste into the field they want
st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)
section("🎤 Voice Input")
st.caption("Select the field you want to fill, click the microphone, speak, then copy the text into the field above.")

MIC_HTML = """
<style>
* { box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
body { margin: 0; background: #f4f7fb; }
.wrap { display: flex; gap: 10px; align-items: flex-start; padding: 4px 0; }
select {
    padding: 8px 10px; border: 1px solid #b8cfe8; border-radius: 6px;
    font-size: 13px; color: #1a3a5c; background: white;
    outline: none; flex: 1;
}
.mic-btn {
    padding: 8px 16px; background: #1a3a5c; color: white;
    border: none; border-radius: 6px; cursor: pointer;
    font-size: 14px; font-weight: 600; white-space: nowrap;
}
.mic-btn.on { background: #2e6da4; }
.result-box {
    margin-top: 10px; padding: 10px 12px;
    border: 1px solid #b8cfe8; border-radius: 6px;
    background: white; font-size: 13px; color: #1a3a5c;
    min-height: 38px; line-height: 1.5;
}
.copy-btn {
    margin-top: 8px; padding: 7px 16px; background: #eaf1fb;
    border: 1px solid #b8cfe8; border-radius: 6px; cursor: pointer;
    font-size: 13px; color: #1a3a5c; font-weight: 600;
}
.copy-btn:hover { background: #dce8f5; }
.status { font-size: 11px; color: #2e6da4; margin-top: 4px; min-height: 14px; }
</style>

<div class="wrap">
    <select id="field_select">
        <option value="occupation">Occupation</option>
        <option value="physical_activity">Physical Activity Level</option>
        <option value="main_complaint">Main Complaint</option>
        <option value="body_area">Body Area Affected</option>
        <option value="problem_duration">Problem Duration</option>
        <option value="aggravating">What makes it worse</option>
        <option value="relieving">What makes it better</option>
        <option value="previous_history">Previous History</option>
        <option value="current_treatments">Current Treatments</option>
        <option value="additional_info">Additional Info</option>
    </select>
    <button class="mic-btn" id="mic_btn" onclick="toggleMic()">🎤 Start Speaking</button>
</div>
<div class="status" id="status"></div>
<div class="result-box" id="result_box">Your spoken text will appear here...</div>
<button class="copy-btn" onclick="copyText()">📋 Copy text</button>

<script>
var rec = null;
var transcript = '';

function toggleMic() {
    if (rec) { rec.stop(); return; }

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        document.getElementById('status').innerText = '⚠️ Use Chrome or Edge browser';
        return;
    }

    transcript = '';
    var SR  = window.SpeechRecognition || window.webkitSpeechRecognition;
    rec = new SR();
    rec.lang = navigator.language || 'en-US';
    rec.continuous = true;
    rec.interimResults = true;

    var btn    = document.getElementById('mic_btn');
    var status = document.getElementById('status');
    var box    = document.getElementById('result_box');

    btn.innerText = '⏹ Stop';
    btn.classList.add('on');
    status.innerText = '🔴 Listening... click Stop when done';
    box.innerText = '';

    rec.onresult = function(e) {
        var interim = '', final = '';
        for (var i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) final += e.results[i][0].transcript;
            else interim += e.results[i][0].transcript;
        }
        if (final) transcript += (transcript ? ' ' : '') + final;
        box.innerText = transcript + (interim ? ' ' + interim : '');
        status.innerText = interim ? '💬 ' + interim : '🔴 Listening...';
    };

    rec.onend = function() {
        rec = null;
        btn.innerText = '🎤 Start Speaking';
        btn.classList.remove('on');
        box.innerText = transcript || 'Nothing captured. Try again.';
        status.innerText = transcript ? '✅ Done — copy the text above into the field' : '';
    };

    rec.onerror = function(e) {
        rec = null;
        btn.innerText = '🎤 Start Speaking';
        btn.classList.remove('on');
        status.innerText = '⚠️ Error: ' + e.error;
    };

    rec.start();
}

function copyText() {
    var text = document.getElementById('result_box').innerText;
    if (!text || text === 'Your spoken text will appear here...') return;
    navigator.clipboard.writeText(text).then(function() {
        document.getElementById('status').innerText = '✅ Copied! Now paste it into the field above (Ctrl+V)';
        setTimeout(function() {
            document.getElementById('status').innerText = '';
        }, 3000);
    });
}
</script>
"""

components.html(MIC_HTML, height=200, scrolling=False)

st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)

# ── BUTTON ────────────────────────────────────────────────
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
        <div style="background:#dce8f5;border-left:4px solid #1a3a5c;border-radius:6px;
                    padding:12px 16px;color:#1a3a5c;font-size:14px;">
            ⚠️ Please fill in <strong>Main Complaint</strong> and <strong>Body Area Affected</strong>.
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

                    st.markdown("""
                    <div style="background:linear-gradient(135deg,#1a3a5c,#2e6da4);padding:16px 24px;
                                border-radius:10px;margin-bottom:20px;margin-top:16px;">
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
                    st.error("API Error: " + json.dumps(result, indent=2))

            except json.JSONDecodeError:
                st.error("Could not parse AI response. Raw output:")
                st.code(clean)
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
