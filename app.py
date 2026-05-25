import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="PhysioAI Assessment",
    page_icon="🏥",
    layout="wide"
)

# ── GLOBAL STYLE ──────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
.stApp { background-color: #f4f7fb; }
hr { border-color: #b8cfe8 !important; }
</style>
""", unsafe_allow_html=True)

# ── READ QUERY PARAMS (submitted from HTML form) ──────────
params = st.query_params

# ── HTML FORM WITH MIC ────────────────────────────────────
FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
body { background: #f4f7fb; padding: 0; }

.banner {
    background: linear-gradient(135deg,#1a3a5c,#2e6da4);
    padding: 24px 28px; border-radius: 12px; margin-bottom: 24px;
}
.banner .title { color: #ffffff; font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.banner .subtitle { color: #b8d4f0; font-size: 13px; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }

.section-bar {
    background: #1a3a5c; color: white; padding: 8px 14px;
    border-radius: 6px; font-size: 12px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 14px;
}

.field { margin-bottom: 13px; }
.field label {
    display: block; font-size: 12px; font-weight: 700;
    color: #1a3a5c; margin-bottom: 4px;
}

.mic-row { display: flex; gap: 6px; align-items: center; }
.mic-row input, .mic-row select { flex: 1; }

input[type=text], input[type=number], select {
    width: 100%; padding: 8px 10px; border: 1px solid #b8cfe8;
    border-radius: 6px; font-size: 13px; color: #1a3a5c;
    background: white; outline: none;
}
input:focus, select:focus { border-color: #1a3a5c; }

.grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; }
.grid-2-inner { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.mic-btn {
    padding: 7px 10px; background: #eaf1fb; border: 1px solid #b8cfe8;
    border-radius: 6px; cursor: pointer; font-size: 15px; flex-shrink: 0;
    transition: background 0.2s; line-height: 1;
}
.mic-btn:hover { background: #d0e3f5; }
.mic-btn.recording { background: #dce8f5; border-color: #1a3a5c; }
.mic-status { font-size: 11px; color: #2e6da4; min-height: 13px; margin-top: 2px; }

.pain-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.pain-row label { font-size: 13px; color: #1a3a5c; font-weight: 600; }
input[type=range] { accent-color: #1a3a5c; flex: 1; }
.pain-val { font-weight: 700; color: #1a3a5c; font-size: 13px; min-width: 30px; }

.lang-section { margin-bottom: 16px; }
.lang-title {
    font-size: 12px; font-weight: 700; color: white;
    background: #1a3a5c; padding: 8px 14px; border-radius: 6px;
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;
}
.lang-row { display: flex; gap: 24px; }
.lang-row label {
    display: flex; align-items: center; gap: 6px;
    font-size: 13px; color: #1a3a5c; cursor: pointer; font-weight: 600;
}

.run-btn {
    padding: 12px 32px; background: #1a3a5c; color: white;
    border: none; border-radius: 8px; font-size: 14px; font-weight: 700;
    cursor: pointer; transition: background 0.2s; letter-spacing: 0.5px;
}
.run-btn:hover { background: #0f2540; }

.error-msg {
    color: #1a3a5c; background: #dce8f5; border-left: 4px solid #1a3a5c;
    border-radius: 6px; padding: 10px 14px; font-size: 13px;
    margin-top: 10px; display: none;
}
</style>
</head>
<body>

<div class="banner">
    <div class="title">🏥 PhysioAI — Clinical Assessment Tool</div>
    <div class="subtitle">AI-assisted physiotherapy screening</div>
</div>

<div class="grid-2">
  <!-- LEFT COLUMN -->
  <div>
    <div class="section-bar">① Patient Profile</div>
    <div class="grid-4">
      <div class="field"><label>Age (years)</label><input type="number" id="age" value="45" min="1" max="120"></div>
      <div class="field"><label>Gender</label>
        <select id="gender">
          <option>Male</option><option selected>Female</option>
          <option>Non-binary</option><option>Prefer not to say</option>
        </select>
      </div>
      <div class="field"><label>Weight (kg)</label><input type="number" id="weight" value="68" min="1" max="300"></div>
      <div class="field"><label>Height (cm)</label><input type="number" id="height" value="165" min="50" max="250"></div>
    </div>
    <div class="field">
      <label>Occupation</label>
      <div class="mic-row">
        <input type="text" id="occupation" placeholder="e.g. Office worker, nurse, athlete..." autocomplete="off">
        <button class="mic-btn" id="mic_occupation" onclick="toggleMic('occupation')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_occupation"></div>
    </div>
    <div class="field">
      <label>Physical Activity Level</label>
      <div class="mic-row">
        <input type="text" id="physical_activity" placeholder="e.g. Sedentary, walks daily, plays football..." autocomplete="off">
        <button class="mic-btn" id="mic_physical_activity" onclick="toggleMic('physical_activity')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_physical_activity"></div>
    </div>

    <div class="section-bar" style="margin-top:8px;">③ Symptoms</div>
    <div class="pain-row">
      <input type="checkbox" id="has_pain" checked onchange="togglePain()">
      <label for="has_pain">Pain is present</label>
    </div>
    <div id="pain_block" class="field">
      <label>Pain Intensity: <span id="pain_val">5</span>/10</label>
      <input type="range" id="pain_intensity" min="0" max="10" value="5"
        oninput="document.getElementById('pain_val').innerText=this.value">
    </div>
    <div class="field">
      <label>What makes it worse?</label>
      <div class="mic-row">
        <input type="text" id="aggravating" placeholder="e.g. Walking, sitting too long, lifting..." autocomplete="off">
        <button class="mic-btn" id="mic_aggravating" onclick="toggleMic('aggravating')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_aggravating"></div>
    </div>
    <div class="field">
      <label>What makes it better?</label>
      <div class="mic-row">
        <input type="text" id="relieving" placeholder="e.g. Rest, heat, ice, specific positions..." autocomplete="off">
        <button class="mic-btn" id="mic_relieving" onclick="toggleMic('relieving')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_relieving"></div>
    </div>
  </div>

  <!-- RIGHT COLUMN -->
  <div>
    <div class="section-bar">② Main Complaint</div>
    <div class="field">
      <label>Describe the patient's main problem *</label>
      <div class="mic-row">
        <input type="text" id="main_complaint" placeholder="e.g. Difficulty walking after knee surgery, loss of balance..." autocomplete="off">
        <button class="mic-btn" id="mic_main_complaint" onclick="toggleMic('main_complaint')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_main_complaint"></div>
    </div>
    <div class="field">
      <label>Body Area Affected *</label>
      <div class="mic-row">
        <input type="text" id="body_area" placeholder="e.g. Left knee, lower back, right shoulder..." autocomplete="off">
        <button class="mic-btn" id="mic_body_area" onclick="toggleMic('body_area')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_body_area"></div>
    </div>
    <div class="grid-2-inner">
      <div class="field">
        <label>How long has this problem existed?</label>
        <div class="mic-row">
          <input type="text" id="problem_duration" placeholder="e.g. 2 weeks, 6 months..." autocomplete="off">
          <button class="mic-btn" id="mic_problem_duration" onclick="toggleMic('problem_duration')" title="Speak">🎤</button>
        </div>
        <div class="mic-status" id="st_problem_duration"></div>
      </div>
      <div class="field">
        <label>How did the problem start?</label>
        <select id="problem_onset">
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
        <input type="text" id="previous_history" placeholder="e.g. Knee surgery 2022, diabetes, herniated disc..." autocomplete="off">
        <button class="mic-btn" id="mic_previous_history" onclick="toggleMic('previous_history')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_previous_history"></div>
    </div>
    <div class="field">
      <label>Current treatments or medications</label>
      <div class="mic-row">
        <input type="text" id="current_treatments" placeholder="e.g. Taking ibuprofen, wearing a brace..." autocomplete="off">
        <button class="mic-btn" id="mic_current_treatments" onclick="toggleMic('current_treatments')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_current_treatments"></div>
    </div>
    <div class="field">
      <label>Any other relevant information</label>
      <div class="mic-row">
        <input type="text" id="additional_info" placeholder="e.g. Patient goals, sport they want to return to..." autocomplete="off">
        <button class="mic-btn" id="mic_additional_info" onclick="toggleMic('additional_info')" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_additional_info"></div>
    </div>
  </div>
</div>

<!-- LANGUAGE + BUTTON -->
<div class="lang-section">
  <div class="lang-title">⑤ Response Language</div>
  <div class="lang-row">
    <label><input type="radio" name="lang" value="English" checked> English</label>
    <label><input type="radio" name="lang" value="Spanish"> Spanish</label>
    <label><input type="radio" name="lang" value="Finnish"> Finnish</label>
  </div>
</div>
<button class="run-btn" onclick="submitForm()">🔍 Run AI Assessment</button>
<div class="error-msg" id="error_msg">⚠️ Please fill in Main Complaint and Body Area Affected.</div>

<script>
// ── AUTOCOMPLETE OFF ──────────────────────────────────────
document.querySelectorAll('input').forEach(function(el) {
    el.setAttribute('autocomplete', 'new-password');
});

// ── PAIN TOGGLE ───────────────────────────────────────────
function togglePain() {
    document.getElementById('pain_block').style.display =
        document.getElementById('has_pain').checked ? 'block' : 'none';
}

// ── MICROPHONE ────────────────────────────────────────────
var activeRec = null;
var activeField = null;

function toggleMic(fieldId) {
    // Stop current recording if active
    if (activeRec) {
        activeRec.stop();
        activeRec = null;
        if (activeField && activeField !== fieldId) {
            // Started a different field — restart for new field
            startMic(fieldId);
        }
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
    rec.lang           = navigator.language || 'en-US';
    rec.continuous     = true;
    rec.interimResults = true;
    activeRec   = rec;
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
        if (final) existing = field.value;
        status.innerText = interim ? '💬 ' + interim : '🔴 Listening...';
    };

    rec.onend = function() {
        activeRec   = null;
        activeField = null;
        btn.innerText = '🎤';
        btn.classList.remove('recording');
        status.innerText = '✅ Done';
        setTimeout(function() { status.innerText = ''; }, 2000);
    };

    rec.onerror = function(e) {
        activeRec   = null;
        activeField = null;
        btn.innerText = '🎤';
        btn.classList.remove('recording');
        status.innerText = '⚠️ ' + e.error;
    };

    rec.start();
}

// ── SUBMIT — send data to Streamlit via query params ──────
function submitForm() {
    var main_complaint = document.getElementById('main_complaint').value.trim();
    var body_area      = document.getElementById('body_area').value.trim();

    if (!main_complaint || !body_area) {
        document.getElementById('error_msg').style.display = 'block';
        return;
    }
    document.getElementById('error_msg').style.display = 'none';

    var params = new URLSearchParams({
        age:               document.getElementById('age').value,
        gender:            document.getElementById('gender').value,
        weight:            document.getElementById('weight').value,
        height:            document.getElementById('height').value,
        occupation:        document.getElementById('occupation').value,
        physical_activity: document.getElementById('physical_activity').value,
        main_complaint:    main_complaint,
        body_area:         body_area,
        problem_duration:  document.getElementById('problem_duration').value,
        problem_onset:     document.getElementById('problem_onset').value,
        has_pain:          document.getElementById('has_pain').checked ? '1' : '0',
        pain_intensity:    document.getElementById('pain_intensity').value,
        aggravating:       document.getElementById('aggravating').value,
        relieving:         document.getElementById('relieving').value,
        previous_history:  document.getElementById('previous_history').value,
        current_treatments:document.getElementById('current_treatments').value,
        additional_info:   document.getElementById('additional_info').value,
        language:          document.querySelector('input[name=lang]:checked').value,
        submitted:         '1'
    });

    // Update parent window URL with query params to trigger Streamlit rerun
    window.parent.location.href = window.parent.location.pathname + '?' + params.toString();
}
</script>
</body>
</html>
"""

# ── RENDER THE FORM ───────────────────────────────────────
components.html(FORM_HTML, height=820, scrolling=False)

# ── PROCESS WHEN SUBMITTED ────────────────────────────────
if params.get("submitted") == "1":

    age               = int(params.get("age", 45))
    gender            = params.get("gender", "")
    weight            = float(params.get("weight", 70))
    height_val        = float(params.get("height", 170))
    occupation        = params.get("occupation", "")
    physical_activity = params.get("physical_activity", "")
    main_complaint    = params.get("main_complaint", "")
    body_area         = params.get("body_area", "")
    problem_duration  = params.get("problem_duration", "")
    problem_onset     = params.get("problem_onset", "")
    has_pain          = params.get("has_pain", "0") == "1"
    pain_intensity    = int(params.get("pain_intensity", 5))
    aggravating       = params.get("aggravating", "")
    relieving         = params.get("relieving", "")
    previous_history  = params.get("previous_history", "")
    current_treatments= params.get("current_treatments", "")
    additional_info   = params.get("additional_info", "")
    language          = params.get("language", "English")

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

                # ── RESULTS ───────────────────────────────────────
                st.markdown("""
                <div style="background:linear-gradient(135deg,#1a3a5c,#2e6da4); padding:16px 24px;
                            border-radius:10px; margin-bottom:20px;">
                    <div style="color:white; font-size:18px; font-weight:700;">📋 AI Assessment Results</div>
                </div>
                """, unsafe_allow_html=True)

                # Primary diagnosis
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

                # Red flags
                red_flags = data.get("red_flags", [])
                if red_flags:
                    flags_html = "".join(f"<li>{f}</li>" for f in red_flags)
                    st.markdown(f"""
                    <div style="background:#dce8f5; border:1px solid #1a3a5c; border-radius:8px;
                                padding:14px 18px; margin-bottom:16px;">
                        <div style="font-weight:700; color:#1a3a5c; margin-bottom:6px;">⚠️ Red Flags Identified</div>
                        <ul style="margin:0; padding-left:18px; color:#1a3a5c; font-size:14px;">{flags_html}</ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background:#eaf1fb; border:1px solid #b8cfe8; border-radius:8px;
                                padding:12px 18px; margin-bottom:16px; color:#1a3a5c; font-size:14px;">
                        ✓ No red flags identified
                    </div>
                    """, unsafe_allow_html=True)

                col_diag, col_ref = st.columns(2)

                with col_diag:
                    st.markdown("""<div style="font-size:11px; font-weight:700; color:#2e6da4;
                        letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                        Differential Diagnoses</div>""", unsafe_allow_html=True)
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
                    st.markdown("""<div style="font-size:11px; font-weight:700; color:#2e6da4;
                        letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                        Referral & Follow-up</div>""", unsafe_allow_html=True)
                    referral = data.get("referral", {})
                    ref_icon = "⚠️ Referral needed" if referral.get("needed") == "Yes" else "✓ No referral needed"
                    ref_reason = f"<div style='font-size:13px;color:#3a5a7c;margin-top:6px;'>{referral.get('reason','')}</div>" if referral.get("needed") == "Yes" else ""
                    st.markdown(f"""
                    <div style="background:#eaf1fb; border:1px solid #b8cfe8;
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

                # Treatment plan
                st.markdown("<div style='margin:20px 0 8px 0'></div>", unsafe_allow_html=True)
                st.markdown("""<div style="font-size:11px; font-weight:700; color:#2e6da4;
                    letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                    Treatment Plan</div>""", unsafe_allow_html=True)

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

                # Home exercises
                st.markdown("<div style='margin:20px 0 8px 0'></div>", unsafe_allow_html=True)
                st.markdown("""<div style="font-size:11px; font-weight:700; color:#2e6da4;
                    letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                    Home Exercise Program</div>""", unsafe_allow_html=True)

                exercises = data.get("home_exercises", [])
                cols = st.columns(len(exercises)) if exercises else []
                for col, ex in zip(cols, exercises):
                    with col:
                        st.markdown(f"""
                        <div style="background:#eaf1fb; border:1px solid #b8cfe8;
                                    border-top:4px solid #1a3a5c; border-radius:8px; padding:16px;">
                            <div style="font-weight:700; color:#1a3a5c; font-size:14px; margin-bottom:8px;">
                                {ex.get('name', '')}
                            </div>
                            <div style="font-size:13px; color:#3a5a7c; line-height:1.5; margin-bottom:10px;">
                                {ex.get('description', '')}
                            </div>
                            <div style="font-size:12px; color:#2e6da4; font-weight:600;">
                                🕐 {ex.get('frequency', '')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("""
                <div style="background:#dce8f5; border:1px solid #b8cfe8; border-radius:8px;
                            padding:12px 18px; font-size:13px; color:#1a3a5c; margin-top:20px;">
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
