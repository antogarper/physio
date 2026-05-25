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

# ── SECTION 1: PATIENT PROFILE ────────────────────────────
st.subheader("① Patient Profile")
col1, col2, col3, col4 = st.columns(4)
with col1:
    age = st.number_input("Age (years)", min_value=1, max_value=120, value=45)
with col2:
    gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
with col3:
    weight = st.number_input("Weight (kg)", min_value=1, max_value=300, value=68)
with col4:
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=165)

col5, col6 = st.columns(2)
with col5:
    occupation = st.text_input("Occupation", placeholder="e.g. Office worker, nurse, construction worker...")
with col6:
    physical_activity = st.text_input("Physical Activity Level", placeholder="e.g. Sedentary, walks daily, plays football 2x/week...")

st.divider()

# ── SECTION 2: MAIN COMPLAINT ─────────────────────────────
st.subheader("② Main Complaint")

main_complaint = st.text_area(
    "Describe the patient's main problem *",
    placeholder="e.g. Difficulty walking after knee surgery, loss of balance when standing, limited shoulder mobility, weakness in left arm after stroke, numbness in hands...",
    height=100
)

col7, col8 = st.columns(2)
with col7:
    body_area = st.text_input("Body Area Affected *", placeholder="e.g. Left knee, lower back, right shoulder, both hands...")
with col8:
    problem_duration = st.text_input("How long has this problem existed?", placeholder="e.g. 2 weeks, 6 months, since birth...")

problem_onset = st.selectbox(
    "How did the problem start?",
    ["Sudden (accident / injury)", "Gradual (developed over time)", "After surgery", "After illness", "Unknown / no clear cause"]
)

st.divider()

# ── SECTION 3: SYMPTOMS ───────────────────────────────────
st.subheader("③ Symptoms")

col9, col10 = st.columns(2)
with col9:
    has_pain = st.checkbox("Pain is present", value=True)
with col10:
    if has_pain:
        pain_intensity = st.slider("Pain Intensity (0 = no pain, 10 = worst possible)", 0, 10, 5)
    else:
        pain_intensity = 0
        st.info("No pain reported")

symptoms = st.multiselect(
    "Select all symptoms that apply:",
    [
        "Pain", "Stiffness", "Limited range of motion", "Weakness / loss of strength",
        "Numbness / tingling", "Swelling / inflammation", "Loss of balance",
        "Difficulty walking", "Muscle spasms", "Fatigue", "Instability / giving way",
        "Clicking / popping sounds", "Difficulty with daily activities", "Poor posture"
    ]
)

aggravating_factors = st.text_input(
    "What makes it worse?",
    placeholder="e.g. Walking, sitting too long, lifting, certain movements, morning time..."
)
relieving_factors = st.text_input(
    "What makes it better?",
    placeholder="e.g. Rest, heat, ice, specific positions, movement..."
)

st.divider()

# ── SECTION 4: CLINICAL HISTORY ───────────────────────────
st.subheader("④ Clinical History")

col11, col12 = st.columns(2)
with col11:
    previous_history = st.text_area(
        "Previous injuries, surgeries or medical conditions",
        placeholder="e.g. Knee surgery 2022, diabetes, herniated disc, stroke, fractures...",
        height=80
    )
with col12:
    current_treatments = st.text_area(
        "Current treatments or medications",
        placeholder="e.g. Taking ibuprofen, wearing a brace, doing home exercises...",
        height=80
    )

additional_info = st.text_area(
    "Any other relevant information",
    placeholder="e.g. Patient goals, work requirements, sport they want to return to, daily life limitations...",
    height=80
)

st.divider()

# ── SECTION 5: LANGUAGE ───────────────────────────────────
st.subheader("⑤ Response Language")
language = st.radio(
    "Select the language for the AI assessment report:",
    options=["English", "Spanish", "Finnish"],
    horizontal=True
)

st.divider()

# ── RUN BUTTON ────────────────────────────────────────────
run = st.button("🔍 Run AI Assessment", type="primary", use_container_width=True)

# ── AI CALL ───────────────────────────────────────────────
if run:
    if not main_complaint.strip() or not body_area.strip():
        st.error("⚠️ Please fill in at least the Main Complaint and Body Area Affected fields.")
    else:
        symptoms_text = ", ".join(symptoms) if symptoms else "Not specified"

        prompt = f"""You are an expert physiotherapist assistant. Analyze the following patient data and provide a structured clinical assessment.

PATIENT PROFILE:
- Age: {age} | Gender: {gender}
- Weight: {weight} kg | Height: {height} cm
- Occupation: {occupation}
- Physical activity: {physical_activity}

MAIN COMPLAINT:
- Description: {main_complaint}
- Body area affected: {body_area}
- Duration: {problem_duration}
- Onset: {problem_onset}

SYMPTOMS:
- Pain present: {"Yes, intensity " + str(pain_intensity) + "/10" if has_pain else "No"}
- Symptoms reported: {symptoms_text}
- Aggravating factors: {aggravating_factors}
- Relieving factors: {relieving_factors}

CLINICAL HISTORY:
- Previous injuries / conditions: {previous_history}
- Current treatments / medications: {current_treatments}
- Additional information: {additional_info}

Please provide:
1. MOST LIKELY DIAGNOSIS – with brief clinical reasoning
2. DIFFERENTIAL DIAGNOSES – 2 or 3 alternatives to consider
3. RED FLAGS – list any that are present, or state "None identified"
4. TREATMENT PLAN – broken into phases (Acute / Recovery / Functional)
5. HOME EXERCISES OR ACTIVITIES – 3 to 5 specific recommendations
6. REFERRAL RECOMMENDATION – whether further imaging or specialist is needed

IMPORTANT: Please write your entire response in {language}.
"""

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
                        "max_tokens": 1500,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )

                result = response.json()

                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    if isinstance(content, list):
                        answer = " ".join(block["text"] for block in content if block.get("type") == "text")
                    else:
                        answer = content

                    st.divider()
                    st.subheader("📋 AI Assessment Results")
                    st.success(f"✅ Assessment complete — response in {language}")
                    st.markdown(answer)
                    st.divider()
                    st.warning("⚠️ AI-assisted screening only. Must be reviewed by a qualified physiotherapist.")

                else:
                    st.error("API Error: " + json.dumps(result, indent=2))

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
