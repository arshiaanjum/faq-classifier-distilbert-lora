import streamlit as st
import time
import os
from inference import FAQClassifier

# Set page title and configuration
st.set_page_config(
    page_title="College FAQ Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom premium styling (Vibrant colors, dark mode look, clean fonts, simplified UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap');
    
    /* Main container and text */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0d0f16;
        color: #e2e8f0;
    }
    
    /* Titles and Headings */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    /* Answer Card */
    .answer-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 5px solid #a855f7;
        border-radius: 12px;
        padding: 24px;
        margin-top: 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #fff;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Probabilities list */
    .prob-bar-container {
        margin-bottom: 8px;
    }
    .prob-label {
        font-size: 0.85rem;
        margin-bottom: 2px;
        display: flex;
        justify-content: space-between;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 50px 0 20px 0;
        color: #64748b;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Answers Database -----------------
ANSWERS = {
    "Fees": """### 💰 Fees & Scholarships Details

* **Tuition Fees:** B.Tech tuition fee is **1,25,000 INR per semester**. MBA is **1,50,000 INR per semester**.
* **Payment Modes:** Online via NetBanking, Credit/Debit cards, UPI, or offline via Demand Draft.
* **Late Payments:** A penalty fine of **500 INR** applies if submitted after the semester deadline.
* **Scholarships:**
  * **Merit-Based:** Up to 50% tuition fee waiver for academic performance (>90% marks).
  * **Need-Based:** Financial aid for economically weaker sections (EWS) upon document submission.
""",
    "Admissions": """### 📝 Admission & Eligibility

* **Application Deadline:** The deadline to apply online for the upcoming academic session is **July 31st**.
* **Eligibility Criteria:**
  * **B.Tech:** Minimum 60% aggregate in 12th standard (Physics, Chemistry, Mathematics).
  * **MBA / MCA:** Graduation with >50% marks + qualifying score in CAT/MAT entrance exams.
* **Selection Process:** Standard document verification followed by cut-off based counseling slots.
""",
    "Hostel": """### 🏠 Hostel & Mess Facilities

* **Accommodation:** Options for single, double, and triple sharing rooms (AC and Non-AC variants).
* **Hostel Fees:** Starts at **85,000 INR per year** (includes room allotment, electricity, and 3 meals/day in the mess).
* **Amenities:** High-speed Wi-Fi, laundry facilities, gym access, and sports equipment.
* **Curfew & Rules:** Curfew is strictly **9:30 PM** for security reasons. Visitors are only allowed in the lobby.
""",
    "Exams": """### 📅 Exams, Results & Backlogs

* **Timetable:** Semester-end theory examinations start on **December 5th**. Date sheets are published on the portal 15 days prior.
* **Hall Tickets:** Downloadable from your student dashboard 1 week before exams.
* **Assessments:** Mid-term internal exams count for 30% of the total grade; end-sem count for 70%.
* **Backlogs & Revaluation:** Backlog clearing exams are held during summer breaks. Paper re-checks can be filed within 10 days of results.
""",
    "Placement": """### 💼 Campus Placements & Internships

* **Average Package:** The average package for computer science placements is **8.5 LPA**. The highest package reached **44 LPA** this year.
* **Recruitment Partners:** Amazon, Microsoft, Adobe, Deloitte, TCS, Infosys, and 120+ other companies.
* **Placement Success:** Over **92%** placement rate for eligible students in the last academic year.
* **Internships:** The Placement Cell organizes 3rd-year summer internship drives with average stipends of **25,000 INR/month**.
""",
    "Other": """### 🌐 Campus Life & General Help

* **Library Timings:** Open **8:00 AM to 10:00 PM** on weekdays, and **9:00 AM to 5:00 PM** on weekends.
* **Wi-Fi Access:** Register your laptop's MAC address at the IT Department block.
* **Medical Care:** A 24/7 medical clinic with an ambulance and general practitioners is situated near the hostel block.
* **Student Clubs:** 25+ clubs across robotics, drama, sports, and entrepreneurship.
"""
}

# ----------------- Load Model Cache -----------------
@st.cache_resource
def get_classifier():
    model_dir = "./best_model"
    if not os.path.exists(model_dir):
        return None
    return FAQClassifier(model_dir=model_dir)

classifier = get_classifier()

# Header
st.title("🎓 College FAQ Assistant")
st.write("Ask a question about fees, admissions, hostel, exams, or placements to get an instant answer.")

if classifier is None:
    st.error("🚨 **Model checkpoints not found!** Run training first.")
    st.stop()

# Examples Row (Simplified Layout)
st.write("**Frequently Asked Questions:**")
cols = st.columns(3)
examples = [
    "What is the average package for computer science placements?",
    "What is the total fee structure for B.Tech?",
    "Is curfew time different for girls and boys hostel?"
]

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if cols[0].button("💼 Average Package?", use_container_width=True):
    st.session_state.user_input = examples[0]
if cols[1].button("💰 B.Tech Fees?", use_container_width=True):
    st.session_state.user_input = examples[1]
if cols[2].button("🏠 Hostel Curfew?", use_container_width=True):
    st.session_state.user_input = examples[2]

# Input area
user_query = st.text_input(
    "Enter your question:",
    value=st.session_state.user_input,
    placeholder="Type your question here (e.g. what are the document requirements for admission?)...",
    label_visibility="collapsed"
)

# Run classification on query input
if user_query:
    with st.spinner("Finding answer..."):
        # Make prediction
        result = classifier.predict(user_query)
        predicted_cat = result['predicted_label']
        
        # Display the actual answer card (main priority)
        answer_text = ANSWERS.get(predicted_cat, "No information available for this category.")
        st.markdown(f"""
        <div class="answer-card">
            {answer_text}
        </div>
        """, unsafe_allow_html=True)
        
        # Collapse all the technical and model performance metrics to reduce clutter
        with st.expander("🛠️ Show AI Model Technical Details"):
            st.markdown(f"**Predicted Category:** `{predicted_cat}`")
            
            # Technical Metrics Columns
            col_perf1, col_perf2, col_perf3 = st.columns(3)
            with col_perf1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{result['confidence'] * 100:.1f}%</div>
                    <div class="metric-label">Confidence</div>
                </div>
                """, unsafe_allow_html=True)
            with col_perf2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{result['latency_ms']:.2f} ms</div>
                    <div class="metric-label">Latency</div>
                </div>
                """, unsafe_allow_html=True)
            with col_perf3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">PEFT-LoRA</div>
                    <div class="metric-label">Model Type</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>**Probability Breakdown:**", unsafe_allow_html=True)
            sorted_probs = sorted(result['class_probabilities'].items(), key=lambda x: x[1], reverse=True)
            for cat, prob in sorted_probs:
                st.markdown(f"""
                <div class="prob-bar-container">
                    <div class="prob-label">
                        <span>{cat}</span>
                        <span>{prob * 100:.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(prob)

st.markdown("""
<div class="footer">
    FAQ Classifier App | Parameter-Efficient Fine-Tuning using Hugging Face PEFT/LoRA & Streamlit
</div>
""", unsafe_allow_html=True)
