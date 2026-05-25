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

st.title("🏥 PhysioAI — Clinical Assessment Tool")
st.caption("AI-assisted physiotherapy screening powered by Databricks GPT")

st.markdown("""
    <style>
    input[type=text], textarea { autocomplete: off !important; }
    </style>
    <script>
    setTimeout(function() {
        document.querySelectorAll('input, textarea').forEach(function(el) {
            el.setAttribute('autocomplete', 'new-password');
        });
    }, 500);
    </script>
""", unsafe_allow_html=True)

st.divider()

# ── VOICE INPUT COMPONENT ─────────────────────────────────
def voice_input(label, key, height=50, multiline=False, placeholder=""):
    """Renders a text field with a microphone button using Web Speech API."""
    tag = "textarea" if multiline else "input"
    textarea_style = "height:80px; resize:vertical;" if multiline else "height:38px;"

    html = f"""
    <div style="font-family: sans-serif; margin-bottom: 4px;">
        <label style="font-size:14px; font-weight:600; color:#31333f;">{label}</label>
        <div style="display:flex; align-items:flex-start; gap:6px; margin-top:4px;">
            {"<textarea" if multiline else "<input type='text'"} 
                id="field_{key}"
                placeholder="{placeholder}"
                style="
                    flex:1; padding:8px 10px; border:1px solid #ccc; border-radius:6px;
                    font-size:14px; font-family:sans-serif; color:#31333f;
                    background:white; outline:none; {textarea_style}
                "
                oninput="sendValue('{key}')"
            {">" if multiline else ">"}
            {"</textarea>" if multiline else ""}
            <button id="btn_{key}" onclick="toggleMic('{key}', {'true' if multiline else 'false'})"
                title="Click to speak"
                style="
                    padding:8px 10px; background:#f0f2f6; border:1px solid #ccc;
                    border-radius:6px; cursor:pointer; font-size:18px;
                    flex-shrink:0; height:38px; display:flex; align-items:center;
                ">🎤</button>
        </div>
        <div id="status_{key}" style="font-size:11px; color:#888; margin-top:2px; height:14px;"></div>
    </div>

    <script>
    var recognizers = {{}};

    function sendValue(key) {{
        var val = document.getElementById('field_' + key).value;
        window.parent.postMessage({{type: 'voice_input', key: key, value: val}}, '*');
    }}

    function toggleMic(key, multiline) {{
        if (recognizers[key] && recognizers[key].running) {{
            recognizers[key].stop();
            return;
        }}

        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            document.getElementById('status_' + key).innerText = '⚠️ Speech not supported in this browser. Use Chrome or Edge.';
            return;
        }}

        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var rec = new SpeechRecognition();
        rec.lang = navigator.language || 'en-US';
        rec.continuous = false;
        rec.interimResults = true;
        rec.running = true;
        recognizers[key] = rec;

        var btn = document.getElementById('btn_' + key);
        var status = document.getElementById('status_' + key);
        var field = document.getElementById('field_' + key);
        var existingText = field.value;

        btn.innerText = '⏹';
        btn.style.background = '#ffe0e0';
        status.innerText = '🔴 Listening...';

        rec.onresult = function(event) {{
            var interim = '';
            var final = '';
            for (var i = event.resultIndex; i < event.results.length; i++) {{
                if (event.results[i].isFinal) {{
                    final += event.results[i][0].transcript;
                }} else {{
                    interim += event.results[i][0].transcript;
                }}
            }}
            var separator = (existingText && !existingText.endsWith(' ')) ? ' ' : '';
            field.value = existingText + separator + final + interim;
            status.innerText = interim ? '💬 ' + interim : '🔴 Listening...';
        }};

        rec.onend = function() {{
            rec.running = false;
            btn.innerText = '🎤';
            btn.style.background = '#f0f2f6';
            existingText = field.value;
            status.innerText = '✅ Done';
            setTimeout(function() {{ status.innerText = ''; }}, 2000);
            sendValue(key);
        }};

        rec.onerror = function(e) {{
            rec.running = false;
            btn.innerText = '🎤';
            btn.style.background = '#f0f2f6';
            status.innerText = '⚠️ Error: ' + e.error;
        }};

        rec.start();
    }}
    </script>
    """

    # Render component and capture value via session state
    components.html(html, height=height, scrolling=False)

    # Read value posted from iframe via query params workaround
    if key not in st.session_state:
        st.session_state[key] = ""

    return st.session_state.get(key, "")


# ── JAVASCRIPT BRIDGE: receive voice values ───────────────
# We use a hidden text_input to bridge voice → session state
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'voice_input') {
        // Store in localStorage as bridge
        localStorage.setItem('voice_' + event.data.key, event.data.value);
    }
});
</script>
""", unsafe_allow_html=True)


# ── HELPER: text input with mic ───────────────────────────
def mic_text_input(label, key, placeholder="", default=""):
    """A standard st.text_input with a voice note displayed below it."""
    col_input, col_mic = st.columns([11, 1])
    with col_input:
        val = st.text_input(label, key=key, placeholder=placeholder, value=default)
    with col_mic:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        components.html(f"""
        <button id="btn_{key}" onclick="toggleMic_{key}()"
            title="Click to speak"
            style="padding:6px 10px; background:#f0f2f6; border:1px solid #ccc;
                   border-radius:6px; cursor:pointer; font-size:18px; width:100%;">🎤</button>
        <div id="status_{key}" style="font-size:10px; color:#888; text-align:center;"></div>
        <script>
        function toggleMic_{key}() {{
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                document.getElementById('status_{key}').innerText = '⚠️ Use Chrome';
                return;
            }}
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            var rec = new SpeechRecognition();
            rec.lang = navigator.language || 'en-US';
            rec.continuous = false;
            rec.interimResults = false;
            var btn = document.getElementById('btn_{key}');
            var status = document.getElementById('status_{key}');
            btn.innerText = '⏹';
            btn.style.background = '#ffe0e0';
            status.innerText = '🔴 ...';
            rec.onresult = function(e) {{
                var text = e.results[0][0].transcript;
                window.parent.postMessage({{type:'streamlit:setComponentValue', key:'{key}', value:text}}, '*');
                status.innerText = '✅';
                btn.innerText = '🎤';
                btn.style.background = '#f0f2f6';
            }};
            rec.onend = function() {{
                btn.innerText = '🎤';
                btn.style.background = '#f0f2f6';
                setTimeout(function(){{status.innerText='';}}, 2000);
            }};
            rec.onerror = function(e) {{
                btn.innerText = '🎤';
                btn.style.background = '#f0f2f6';
                status.innerText = '⚠️';
            }};
            rec.start();
        }}
        </script>
        """, height=70)
    return val


# ── BUILD THE FULL VOICE-ENABLED FORM ─────────────────────
# Because Streamlit's component iframe communication is one-way,
# we use a self-contained HTML form for all voice fields,
# and sync to Streamlit via a single hidden submit.

FORM_HTML = """
<style>
* { box-sizing: border-box; font-family: sans-serif; }
.section-title {
    font-size: 17px; font-weight: 700; color: #1f77b4;
    border-bottom: 2px solid #1f77b4; padding-bottom: 6px;
    margin: 18px 0 12px 0;
}
.row { display: flex; gap: 16px; margin-bottom: 10px; }
.field { flex: 1; display: flex; flex-direction: column; }
label { font-size: 13px; font-weight: 600; color: #31333f; margin-bottom: 4px; }
input[type=text], input[type=number], select, textarea {
    padding: 8px 10px; border: 1px solid #ccc; border-radius: 6px;
    font-size: 14px; color: #31333f; background: white;
    width: 100%; outline: none; autocomplete: off;
}
textarea { resize: vertical; }
.mic-row { display: flex; gap: 6px; align-items: flex-start; }
.mic-row input, .mic-row textarea { flex: 1; }
.mic-btn {
    padding: 7px 10px; background: #f0f2f6; border: 1px solid #ccc;
    border-radius: 6px; cursor: pointer; font-size: 16px;
    flex-shrink: 0; white-space: nowrap;
}
.mic-btn.recording { background: #ffe0e0; }
.mic-status { font-size: 11px; color: #888; height: 14px; margin-top: 2px; }
.submit-btn {
    margin-top: 20px; padding: 12px 28px; background: #1f77b4;
    color: white; border: none; border-radius: 8px; font-size: 15px;
    font-weight: 600; cursor: pointer; display: block;
}
.submit-btn:hover { background: #1560a0; }
.lang-radio { display: flex; gap: 20px; margin-top: 6px; }
.lang-radio label { font-weight: 400; display: flex; align-items: center; gap: 6px; cursor: pointer; }
</style>

<div class="section-title">① Patient Profile &nbsp; + &nbsp; ② Main Complaint</div>
<div class="row">
  <!-- LEFT: Patient Profile -->
  <div style="flex:1">
    <div class="row">
      <div class="field">
        <label>Age (years)</label>
        <input type="number" id="age" value="45" min="1" max="120">
      </div>
      <div class="field">
        <label>Gender</label>
        <select id="gender">
          <option>Male</option><option selected>Female</option>
          <option>Non-binary</option><option>Prefer not to say</option>
        </select>
      </div>
      <div class="field">
        <label>Weight (kg)</label>
        <input type="number" id="weight" value="68" min="1" max="300">
      </div>
      <div class="field">
        <label>Height (cm)</label>
        <input type="number" id="height" value="165" min="50" max="250">
      </div>
    </div>
    <div class="field" style="margin-bottom:10px">
      <label>Occupation</label>
      <div class="mic-row">
        <input type="text" id="occupation" placeholder="e.g. Office worker, nurse, athlete...">
        <button class="mic-btn" onclick="mic('occupation', false)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_occupation"></div>
    </div>
    <div class="field">
      <label>Physical Activity Level</label>
      <div class="mic-row">
        <input type="text" id="physical_activity" placeholder="e.g. Sedentary, walks daily, plays football...">
        <button class="mic-btn" onclick="mic('physical_activity', false)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_physical_activity"></div>
    </div>
  </div>

  <!-- RIGHT: Main Complaint -->
  <div style="flex:1">
    <div class="field" style="margin-bottom:10px">
      <label>Describe the patient's main problem *</label>
      <div class="mic-row">
        <textarea id="main_complaint" rows="4" placeholder="e.g. Difficulty walking after knee surgery, loss of balance, limited shoulder mobility..."></textarea>
        <button class="mic-btn" onclick="mic('main_complaint', true)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_main_complaint"></div>
    </div>
    <div class="field" style="margin-bottom:10px">
      <label>Body Area Affected *</label>
      <div class="mic-row">
        <input type="text" id="body_area" placeholder="e.g. Left knee, lower back, right shoulder...">
        <button class="mic-btn" onclick="mic('body_area', false)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_body_area"></div>
    </div>
    <div class="row">
      <div class="field">
        <label>How long has this problem existed?</label>
        <div class="mic-row">
          <input type="text" id="problem_duration" placeholder="e.g. 2 weeks, 6 months...">
          <button class="mic-btn" onclick="mic('problem_duration', false)" title="Speak">🎤</button>
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
  </div>
</div>

<div class="section-title">③ Symptoms &nbsp; + &nbsp; ④ Clinical History</div>
<div class="row">
  <!-- LEFT: Symptoms -->
  <div style="flex:1">
    <div class="field" style="margin-bottom:10px">
      <label><input type="checkbox" id="has_pain" checked onchange="togglePain()"> &nbsp; Pain is present</label>
      <div id="pain_intensity_block" style="margin-top:8px;">
        <label>Pain Intensity: <span id="pain_val">5</span>/10</label>
        <input type="range" id="pain_intensity" min="0" max="10" value="5"
          oninput="document.getElementById('pain_val').innerText=this.value"
          style="width:100%; accent-color:#1f77b4;">
      </div>
    </div>
    <div class="field" style="margin-bottom:10px">
      <label>What makes it worse?</label>
      <div class="mic-row">
        <input type="text" id="aggravating" placeholder="e.g. Walking, sitting too long, lifting...">
        <button class="mic-btn" onclick="mic('aggravating', false)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_aggravating"></div>
    </div>
    <div class="field">
      <label>What makes it better?</label>
      <div class="mic-row">
        <input type="text" id="relieving" placeholder="e.g. Rest, heat, ice, specific positions...">
        <button class="mic-btn" onclick="mic('relieving', false)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_relieving"></div>
    </div>
  </div>

  <!-- RIGHT: Clinical History -->
  <div style="flex:1">
    <div class="field" style="margin-bottom:10px">
      <label>Previous injuries, surgeries or medical conditions</label>
      <div class="mic-row">
        <textarea id="previous_history" rows="3" placeholder="e.g. Knee surgery 2022, diabetes, herniated disc..."></textarea>
        <button class="mic-btn" onclick="mic('previous_history', true)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_previous_history"></div>
    </div>
    <div class="field" style="margin-bottom:10px">
      <label>Current treatments or medications</label>
      <div class="mic-row">
        <textarea id="current_treatments" rows="3" placeholder="e.g. Taking ibuprofen, wearing a brace..."></textarea>
        <button class="mic-btn" onclick="mic('current_treatments', true)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_current_treatments"></div>
    </div>
    <div class="field">
      <label>Any other relevant information</label>
      <div class="mic-row">
        <textarea id="additional_info" rows="3" placeholder="e.g. Patient goals, sport they want to return to..."></textarea>
        <button class="mic-btn" onclick="mic('additional_info', true)" title="Speak">🎤</button>
      </div>
      <div class="mic-status" id="st_additional_info"></div>
    </div>
  </div>
</div>

<div class="section-title">⑤ Response Language</div>
<div class="lang-radio">
  <label><input type="radio" name="language" value="English" checked> English</label>
  <label><input type="radio" name="language" value="Spanish"> Spanish</label>
  <label><input type="radio" name="language" value="Finnish"> Finnish</label>
</div>

<button class="submit-btn" onclick="submitForm()">🔍 Run AI Assessment</button>
<div id="form_error" style="color:red; margin-top:8px; font-size:13px;"></div>

<script>
// ── AUTOCOMPLETE OFF ──────────────────────────────────────
document.querySelectorAll('input, textarea').forEach(function(el) {
    el.setAttribute('autocomplete', 'new-password');
});

// ── PAIN TOGGLE ───────────────────────────────────────────
function togglePain() {
    var block = document.getElementById('pain_intensity_block');
    block.style.display = document.getElementById('has_pain').checked ? 'block' : 'none';
}

// ── MICROPHONE ────────────────────────────────────────────
var activeRec = null;

function mic(fieldId, isTextarea) {
    var btn = event.target;
    var status = document.getElementById('st_' + fieldId);
    var field = document.getElementById(fieldId);

    if (activeRec) {
        activeRec.stop();
        activeRec = null;
        return;
    }

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        status.innerText = '⚠️ Use Chrome or Edge';
        return;
    }

    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var rec = new SpeechRecognition();
    rec.lang = navigator.language || 'en-US';
    rec.continuous = true;
    rec.interimResults = true;
    activeRec = rec;

    var existing = field.value;
    btn.innerText = '⏹';
    btn.classList.add('recording');
    status.innerText = '🔴 Listening... (click ⏹ to stop)';

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
        activeRec = null;
        btn.innerText = '🎤';
        btn.classList.remove('recording');
        status.innerText = '✅ Done';
        setTimeout(function() { status.innerText = ''; }, 2000);
    };

    rec.onerror = function(e) {
        activeRec = null;
        btn.innerText = '🎤';
        btn.classList.remove('recording');
        status.innerText = '⚠️ ' + e.error;
    };

    rec.start();
}

// ── SUBMIT FORM ───────────────────────────────────────────
function submitForm() {
    var main_complaint = document.getElementById('main_complaint').value.trim();
    var body_area = document.getElementById('body_area').value.trim();

    if (!main_complaint || !body_area) {
        document.getElementById('form_error').innerText = '⚠️ Please fill in Main Complaint and Body Area Affected.';
        return;
    }
    document.getElementById('form_error').innerText = '';

    var data = {
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
        has_pain:          document.getElementById('has_pain').checked,
        pain_intensity:    document.getElementById('pain_intensity').value,
        aggravating:       document.getElementById('aggravating').value,
        relieving:         document.getElementById('relieving').value,
        previous_history:  document.getElementById('previous_history').value,
        current_treatments:document.getElementById('current_treatments').value,
        additional_info:   document.getElementById('additional_info').value,
        language:          document.querySelector('input[name=language]:checked').value
    };

    window.parent.postMessage({type: 'physio_submit', data: data}, '*');
}
</script>
"""

# ── RENDER FORM ───────────────────────────────────────────
components.html(FORM_HTML, height=1000, scrolling=False)

# ── RECEIVE FORM DATA VIA QUERY PARAMS ────────────────────
# Since postMessage can't directly trigger Streamlit reruns,
# we use a st.text_area as hidden bridge + a listener button
st.markdown("---")
st.markdown("##### Or paste/type data manually and submit below:")

with st.expander("📝 Manual text entry (fallback if voice is not available)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=45)
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
        weight = st.number_input("Weight (kg)", min_value=1, max_value=300, value=68)
        height_val = st.number_input("Height (cm)", min_value=50, max_value=250, value=165)
        occupation = st.text_input("Occupation", key="occ")
        physical_activity = st.text_input("Physical Activity", key="pa")
        main_complaint = st.text_area("Main Complaint *", key="mc", height=80)
        body_area = st.text_input("Body Area *", key="ba")
    with col2:
        problem_duration = st.text_input("Duration", key="pd")
        problem_onset = st.selectbox("Onset", ["Sudden (accident / injury)", "Gradual (developed over time)", "After surgery", "After illness", "Unknown / no clear cause"])
        has_pain = st.checkbox("Pain present", value=True)
        pain_intensity = st.slider("Pain Intensity", 0, 10, 5) if has_pain else 0
        aggravating = st.text_input("Aggravating factors", key="ag")
        relieving = st.text_input("Relieving factors", key="re")
        previous_history = st.text_area("Previous history", key="ph", height=60)
        current_treatments = st.text_area("Current treatments", key="ct", height=60)
        additional_info = st.text_area("Additional info", key="ai_info", height=60)
        language = st.radio("Language", ["English", "Spanish", "Finnish"], horizontal=True)

    run = st.button("🔍 Run AI Assessment", type="primary")

    if run:
        if not main_complaint.strip() or not body_area.strip():
            st.error("⚠️ Please fill in Main Complaint and Body Area.")
        else:
            # Build prompt and call API
            symptoms_text = f"Pain intensity {pain_intensity}/10" if has_pain else "No pain"

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

            with st.spinner("🤖 Analyzing patient data..."):
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

                        # ── DISPLAY RESULTS ───────────────────────────────
                        st.divider()
                        st.subheader("📋 AI Assessment Results")

                        confidence_color = {"High": "green", "Medium": "orange", "Low": "red"}.get(data.get("confidence", ""), "green")
                        st.markdown(f"""
                        <div style="background:#f0f8ff; padding:20px; border-radius:10px; border-left:6px solid #1f77b4; margin-bottom:16px">
                            <h2 style="margin:0; color:#1f77b4;">🔍 {data.get('primary_diagnosis', '')}</h2>
                            <p style="margin:8px 0 4px 0; color:#333;">{data.get('diagnosis_reasoning', '')}</p>
                            <span style="background:{confidence_color}; color:white; padding:3px 12px; border-radius:20px; font-size:13px;">
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
                                <div style="background:#f9f9f9; border-radius:8px; padding:12px; margin-bottom:8px; border-left:4px solid #aaa;">
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
                                <div style="background:#f0fff0; border-radius:10px; padding:14px; border-top:4px solid #2ca02c;">
                                    <strong>💪 {ex.get('name', '')}</strong><br><br>
                                    <span style="font-size:13px; color:#333;">{ex.get('description', '')}</span><br><br>
                                    <span style="font-size:12px; color:#2ca02c;">🕐 {ex.get('frequency', '')}</span>
                                </div>
                                """, unsafe_allow_html=True)

                        st.divider()
                        st.warning("⚠️ AI-assisted screening only. Must be reviewed by a qualified physiotherapist.")

                    else:
                        st.error("API Error: " + json.dumps(result, indent=2))

                except json.JSONDecodeError:
                    st.error("Could not parse AI response. Please try again.")
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")
