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
    background-color: #1a3a5c !important;
    border: none !important; border-radius: 8px !important;
    color: white !important; font-weight: 700 !important;
    padding: 12px 36px !important; font-size: 15px !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #0f2540 !important;
}
</style>
""", unsafe_allow_html=True)

# ── INITIALIZE SESSION STATE ──────────────────────────────
for key in ["age","gender","weight","height","occupation","physical_activity",
            "main_complaint","body_area","problem_duration","problem_onset",
            "has_pain","pain_intensity","aggravating","relieving",
            "previous_history","current_treatments","additional_info","language"]:
    if key not in st.session_state:
        st.session_state[key] = ""

FORM_HTML = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
body { background: #f4f7fb; }
.banner {
    background: linear-gradient(135deg,#1a3a5c,#2e6da4);
    padding: 24px 28px; border-radius: 12px; margin-bottom: 20px;
}
.banner .title { color: #ffffff; font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.banner .subtitle { color: #b8d4f0; font-size: 13px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 16px; }
.grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; }
.grid-2-inner { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.section-bar {
    background: #1a3a5c; color: white; padding: 8px 14px;
    border-radius: 6px; font-size: 12px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;
}
.field { margin-bottom: 12px; }
.field label { display: block; font-size: 12px; font-weight: 700; color: #1a3a5c; margin-bottom: 4px; }
.mic-row { display: flex; gap: 6px; align-items: center; }
.mic-row input, .mic-row select { flex: 1; }
input[type=text], input[type=number], select {
    width: 100%; padding: 8px 10px; border: 1px solid #b8cfe8;
    border-radius: 6px; font-size: 13px; color: #1a3a5c; background: white; outline: none;
}
input:focus, select:focus { border-color: #1a3a5c; }
.mic-btn {
    padding: 7px 10px; background: #eaf1fb; border: 1px solid #b8cfe8;
    border-radius: 6px; cursor: pointer; font-size: 15px; flex-shrink: 0;
}
.mic-btn.recording { background: #dce8f5; border-color: #1a3a5c; }
.mic-status { font-size: 11px; color: #2e6da4; min-height: 13px; margin-top: 2px; }
.pain-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
input[type=range] { accent-color: #1a3a5c; flex: 1; }
.lang-bar {
    background: #1a3a5c; color: white; padding: 8px 14px;
    border-radius: 6px; font-size: 12px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;
}
.lang-row { display: flex; gap: 24px; margin-bottom: 16px; }
.lang-row label { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #1a3a5c; font-weight: 600; cursor: pointer; }
.error-msg {
    color: #1a3a5c; background: #dce8f5; border-left: 4px solid #1a3a5c;
    border-radius: 6px; padding: 10px 14px; font-size: 13px; display: none; margin-bottom: 10px;
}
</style>

<div class="banner">
    <div class="title">🏥 PhysioAI — Clinical Assessment Tool</div>
    <div class="subtitle">AI-assisted physiotherapy screening</div>
</div>

<div class="grid-2">
  <div>
    <div class="section-bar">① Patient Profile</div>
    <div class="grid-4">
      <div class="field"><label>Age</label><input type="number" id="age" value="45" min="1" max="120" oninput="sync()"></div>
      <div class="field"><label>Gender</label>
        <select id="gender" onchange="sync()">
          <option>Male</option><option selected>Female</option>
          <option>Non-binary</option><option>Prefer not to say</option>
        </select>
      </div>
      <div class="field"><label>Weight (kg)</label><input type="number" id="weight" value="68" oninput="sync()"></div>
      <div class="field"><label>Height (cm)</label><input type="number" id="height" value="165" oninput="sync()"></div>
    </div>
    <div class="field">
      <label>Occupation</label>
      <div class="mic-row">
        <input type="text" id="occupation" placeholder="e.g. Office worker, nurse..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_occupation" onclick="toggleMic('occupation')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_occupation"></div>
    </div>
    <div class="field">
      <label>Physical Activity Level</label>
      <div class="mic-row">
        <input type="text" id="physical_activity" placeholder="e.g. Sedentary, walks daily..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_physical_activity" onclick="toggleMic('physical_activity')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_physical_activity"></div>
    </div>
    <div class="section-bar" style="margin-top:8px;">③ Symptoms</div>
    <div class="pain-row">
      <input type="checkbox" id="has_pain" checked onchange="togglePain(); sync()">
      <label for="has_pain" style="font-size:13px;color:#1a3a5c;font-weight:600;">Pain is present</label>
    </div>
    <div id="pain_block" class="field">
      <label>Pain Intensity: <span id="pain_val">5</span>/10</label>
      <input type="range" id="pain_intensity" min="0" max="10" value="5"
        oninput="document.getElementById('pain_val').innerText=this.value; sync()">
    </div>
    <div class="field">
      <label>What makes it worse?</label>
      <div class="mic-row">
        <input type="text" id="aggravating" placeholder="e.g. Walking, sitting too long..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_aggravating" onclick="toggleMic('aggravating')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_aggravating"></div>
    </div>
    <div class="field">
      <label>What makes it better?</label>
      <div class="mic-row">
        <input type="text" id="relieving" placeholder="e.g. Rest, heat, ice..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_relieving" onclick="toggleMic('relieving')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_relieving"></div>
    </div>
  </div>

  <div>
    <div class="section-bar">② Main Complaint</div>
    <div class="field">
      <label>Describe the patient's main problem *</label>
      <div class="mic-row">
        <input type="text" id="main_complaint" placeholder="e.g. Difficulty walking after knee surgery..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_main_complaint" onclick="toggleMic('main_complaint')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_main_complaint"></div>
    </div>
    <div class="field">
      <label>Body Area Affected *</label>
      <div class="mic-row">
        <input type="text" id="body_area" placeholder="e.g. Left knee, lower back..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_body_area" onclick="toggleMic('body_area')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_body_area"></div>
    </div>
    <div class="grid-2-inner">
      <div class="field">
        <label>How long has this problem existed?</label>
        <div class="mic-row">
          <input type="text" id="problem_duration" placeholder="e.g. 2 weeks, 6 months..." autocomplete="new-password" oninput="sync()">
          <button class="mic-btn" id="mic_problem_duration" onclick="toggleMic('problem_duration')" title="Speak">🎤</button>
        </div>
        <div class="mic-status" id="st_problem_duration"></div>
      </div>
      <div class="field">
        <label>How did the problem start?</label>
        <select id="problem_onset" onchange="sync()">
          <option>Sudden (accident / injury)</option>
          <option>Gradual (developed over time)</option>
          <option>After surgery</option>
          <option>After illness</option>
          <option>Unknown / no clear cause</option>
        </select>
      </div>
    </div>
    <div class="section-bar" style="margin-top:8px;">④ Clinical History</div>
    <div class="field">
      <label>Previous injuries, surgeries or medical conditions</label>
      <div class="mic-row">
        <input type="text" id="previous_history" placeholder="e.g. Knee surgery 2022, diabetes..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_previous_history" onclick="toggleMic('previous_history')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_previous_history"></div>
    </div>
    <div class="field">
      <label>Current treatments or medications</label>
      <div class="mic-row">
        <input type="text" id="current_treatments" placeholder="e.g. Taking ibuprofen, wearing a brace..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_current_treatments" onclick="toggleMic('current_treatments')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_current_treatments"></div>
    </div>
    <div class="field">
      <label>Any other relevant information</label>
      <div class="mic-row">
        <input type="text" id="additional_info" placeholder="e.g. Patient goals, sport they want to return to..." autocomplete="new-password" oninput="sync()">
        <button class="mic-btn" id="mic_additional_info" onclick="toggleMic('additional_info')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_additional_info"></div>
    </div>
  </div>
</div>

<div class="lang-bar">⑤ Response Language</div>
<div class="lang-row">
  <label><input type="radio" name="lang" value="English" checked onchange="sync()"> English</label>
  <label><input type="radio" name="lang" value="Spanish" onchange="sync()"> Spanish</label>
  <label><input type="radio" name="lang" value="Finnish" onchange="sync()"> Finnish</label>
</div>
<div class="error-msg" id="error_msg">⚠️ Please fill in Main Complaint and Body Area Affected.</div>

<script>
var activeRec = null;
var activeField = null;

function togglePain() {
    document.getElementById('pain_block').style.display =
        document.getElementById('has_pain').checked ? 'block' : 'none';
}

// Sync all values to sessionStorage continuously
function sync() {
    var data = {
        age:               document.getElementById('age').value,
        gender:            document.getElementById('gender').value,
        weight:            document.getElementById('weight').value,
        height:            document.getElementById('height').value,
        occupation:        document.getElementById('occupation').value,
        physical_activity: document.getElementById('physical_activity').value,
        main_complaint:    document.getElementById('main_complaint').value,
        body_area:         document.getElementById('body_area').value,
        problem_duration:  document.getElementById('problem_duration').value,
        problem_onset:     document.getElementById('problem_onset').value,
        has_pain:          document.getElementById('has_pain').checked ? '1' : '0',
        pain_intensity:    document.getElementById('pain_intensity').value,
        aggravating:       document.getElementById('aggravating').value,
        relieving:         document.getElementById('relieving').value,
        previous_history:  document.getElementById('previous_history').value,
        current_treatments:document.getElementById('current_treatments').value,
        additional_info:   document.getElementById('additional_info').value,
        language:          (document.querySelector('input[name=lang]:checked') || {value:'English'}).value
    };
    window.parent.postMessage({type: 'physio_data', data: data}, '*');
}

// Sync on load
window.onload = function() { sync(); };

function toggleMic(fieldId) {
    if (activeRec) {
        activeRec.stop();
        activeRec = null;
        if (activeField !== fieldId) { startMic(fieldId); }
        return;
    }
    startMic(fieldId);
}

function startMic(fieldId) {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        document.getElementById('st_' + fieldId).innerText = '⚠️ Use Chrome or Edge';
        return;
    }
    var SR  = window.SpeechRecognition || window.webkitSpeechRecognition;
    var rec = new SR();
    rec.lang = navigator.language || 'en-US';
    rec.continuous = true;
    rec.interimResults = true;
    activeRec = rec;
    activeField = fieldId;

    var btn    = document.getElementById('mic_' + fieldId);
    var status = document.getElementById('st_' + fieldId);
    var field  = document.getElementById(fieldId);
    var existing = field.value;

    btn.innerText = '⏹';
    btn.classList.add('recording');
    status.innerText = '🔴 Listening... click ⏹ to stop';

    rec.onresult = function(e) {
        var interim = '', final = '';
        for (var i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) final += e.results[i][0].transcript;
            else interim += e.results[i][0].transcript;
        }
        var sep = (existing && !existing.endsWith(' ')) ? ' ' : '';
        field.value = existing + sep + final;
        if (final) { existing = field.value; sync(); }
        status.innerText = interim ? '💬 ' + interim : '🔴 Listening...';
    };

    rec.onend = function() {
        activeRec = null; activeField = null;
        btn.innerText = '🎤';
        btn.classList.remove('recording');
        status.innerText = '✅ Done';
        sync();
        setTimeout(function() { status.innerText = ''; }, 2000);
    };

    rec.onerror = function(e) {
        activeRec = null; activeField = null;
        btn.innerText = '🎤';
        btn.classList.remove('recording');
        status.innerText = '⚠️ ' + e.error;
    };

    rec.start();
}
</script>
"""

# ── SESSION STATE FOR FORM DATA ───────────────────────────
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# ── JAVASCRIPT BRIDGE: receive form data via postMessage ──
st.markdown("""
<script>
window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'physio_data') {
        // Store in parent sessionStorage as bridge
        window.sessionStorage.setItem('physio_form', JSON.stringify(e.data.data));
    }
});
</script>
""", unsafe_allow_html=True)

# ── RENDER FORM ───────────────────────────────────────────
components.html(FORM_HTML, height=1000, scrolling=False)

# ── STREAMLIT BUTTON (outside iframe — always works) ──────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run = st.button("🔍 Run AI Assessment", type="primary")

# ── READ DATA FROM QUERY PARAMS OR SESSION STATE ──────────
if run:
    # Read values from st.session_state keys set by the form
    d = st.session_state.form_data

    # Fallback: try query params
    p = st.query_params
    age               = int(p.get("age", d.get("age", 45)))
    gender            = p.get("gender", d.get("gender", ""))
    weight            = float(p.get("weight", d.get("weight", 70)))
    height_val        = float(p.get("height", d.get("height", 170)))
    occupation        = p.get("occupation", d.get("occupation", ""))
    physical_activity = p.get("physical_activity", d.get("physical_activity", ""))
    main_complaint    = p.get("main_complaint", d.get("main_complaint", ""))
    body_area         = p.get("body_area", d.get("body_area", ""))
    problem_duration  = p.get("problem_duration", d.get("problem_duration", ""))
    problem_onset     = p.get("problem_onset", d.get("problem_onset", ""))
    has_pain          = p.get("has_pain", d.get("has_pain", "1")) == "1"
    pain_intensity    = int(p.get("pain_intensity", d.get("pain_intensity", 5)))
    aggravating       = p.get("aggravating", d.get("aggravating", ""))
    relieving         = p.get("relieving", d.get("relieving", ""))
    previous_history  = p.get("previous_history", d.get("previous_history", ""))
    current_treatments= p.get("current_treatments", d.get("current_treatments", ""))
    additional_info   = p.get("additional_info", d.get("additional_info", ""))
    language          = p.get("language", d.get("language", "English"))

    if not str(main_complaint).strip() or not str(body_area).strip():
        st.markdown("""
        <div style="background:#dce8f5; border-left:4px solid #1a3a5c; border-radius:6px;
                    padding:12px 16px; color:#1a3a5c; font-size:14px; text-align:center;">
            ⚠️ Please fill in <strong>Main Complaint</strong> and <strong>Body Area Affected</strong>
            in the form above, then click the button again.
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
                    <div style="background:linear-gradient(135deg,#1a3a5c,#2e6da4); padding:16px 24px;
                                border-radius:10px; margin-bottom:20px; margin-top:16px;">
                        <div style="color:white; font-size:18px; font-weight:700;">📋 AI Assessment Results</div>
                    </div>
                    """, unsafe_allow_html=True)

                    conf = data.get("confidence", "High")
                    conf_bg = {"High": "#1a3a5c", "Medium": "#2e6da4", "Low": "#6699cc"}.get(conf, "#1a3a5c")
                    st.markdown(f"""
                    <div style="background:#eaf1fb; border:1px solid #b8cfe8; border-radius:10px; padding:20px; margin-bottom:16px;">
                        <div style="font-size:11px; font-weight:700; color:#2e6da4; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">Primary Diagnosis</div>
                        <div style="font-size:22px; font-weight:700; color:#1a3a5c; margin-bottom:8px;">{data.get('primary_diagnosis', '')}</div>
                        <div style="font-size:14px; color:#3a5a7c; line-height:1.6; margin-bottom:12px;">{data.get('diagnosis_reasoning', '')}</div>
                        <span style="background:{conf_bg}; color:white; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600;">Confidence: {conf}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    red_flags = data.get("red_flags", [])
                    if red_flags:
                        flags_html = "".join(f"<li>{f}</li>" for f in red_flags)
                        st.markdown(f"""
                        <div style="background:#dce8f5; border:1px solid #1a3a5c; border-radius:8px; padding:14px 18px; margin-bottom:16px;">
                            <div style="font-weight:700; color:#1a3a5c; margin-bottom:6px;">⚠️ Red Flags Identified</div>
                            <ul style="margin:0; padding-left:18px; color:#1a3a5c; font-size:14px;">{flags_html}</ul>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background:#eaf1fb; border:1px solid #b8cfe8; border-radius:8px; padding:12px 18px; margin-bottom:16px; color:#1a3a5c; font-size:14px;">
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
