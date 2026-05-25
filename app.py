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

# ── PATIENT DATA FORM ─────────────────────────────────────
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
    occupation = st.text_input("Occupation", placeholder="e.g. Office worker, nurse, athlete...")
with col6:
    physical_activity = st.text_input("Physical Activity", placeholder="e.g. Running 3x/week, sedentary...")

st.divider()
st.subheader("② Pain Assessment")

col7, col8 = st.columns(2)
with col7:
    pain_location = st.text_input("Pain Location", placeholder="e.g. Lower back, left knee, right shoulder...")
with col8:
    pain_duration = st.text_input("Pain Duration", placeholder="e.g. 3 weeks, 6 months...")

pain_intensity = st.slider("Pain Intensity (0 = no pain, 10 = worst possible)", 0, 10, 5)

col9, col10 = st.columns(2)
with col9:
    pain_character = st.text_input("Pain Character", placeholder="e.g. Sharp, dull, burning, throbbing...")
with col10:
    aggravating_factors = st.text_input("Aggravating Factors", placeholder="e.g. Sitting, bending, climbing stairs...")

relieving_factors = st.text_input("Relieving Factors", placeholder="e.g. Rest, heat, ice, walking...")

st.divider()
st.subheader("③ Clinical History")

previous_history = st.text_area("Previous Injuries / Medical History",
    placeholder="e.g. Herniated disc 2019, diabetes, knee surgery...", height=80)
additional_symptoms = st.text_area("Additional Symptoms",
    placeholder="e.g. Numbness, tingling, weakness, swelling...", height=80)

st.divider()

# ── LANGUAGE SELECTOR ─────────────────────────────────────
st.subheader("④ Response Language")
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
    if not pain_location:
        st.error("Please enter the pain location before running the assessment.")
    else:
        prompt = f"""You are an expert physiotherapist assistant. Analyze the following patient data and provide a structured clinical assessment.

PATIENT:
- Age: {age} | Gender: {gender}
- Weight: {weight} kg | Height: {height} cm
- Occupation: {occupation}
- Physical activity: {physical_activity}

PAIN PRESENTATION:
- Location: {pain_location}
- Duration: {pain_duration}
- Intensity: {pain_intensity}/10
- Character: {pain_character}
- Aggravating factors: {aggravating_factors}
- Relieving factors: {relieving_factors}

CLINICAL HISTORY:
- Background: {previous_history}
- Additional symptoms: {additional_symptoms}

Please provide:
1. MOST LIKELY DIAGNOSIS – with brief clinical reasoning
2. DIFFERENTIAL DIAGNOSES – 2 or 3 alternatives to consider
3. RED FLAGS – list any that are present, or state "None identified"
4. TREATMENT PLAN – broken into phases (Acute / Recovery / Functional)
5. HOME EXERCISES – 3 to 5 specific exercises
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

                    # ── DISPLAY RESULTS ───────────────────────────────
                    st.divider()
                    st.subheader("📋 AI Assessment Results")
                    st.success(f"Assessment complete — response in {language}")
                    st.markdown(answer)
                    st.divider()
                    st.warning("⚠️ AI-assisted screening only. Must be reviewed by a qualified physiotherapist.")

                else:
                    st.error("API Error: " + json.dumps(result, indent=2))

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
