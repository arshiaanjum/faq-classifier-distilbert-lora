import streamlit as st
import time
import os
import re
from inference import FAQClassifier

# Set page title and configuration
st.set_page_config(
    page_title="College FAQ Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session States
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Custom premium styling (Vibrant colors, neon glow cards, mobile responsive)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap');
    
    /* Main container and text */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: #FAF9F5;
        color: #374151;
    }
    
    [data-testid="stHeader"] {
        background: rgba(250, 249, 245, 0.9);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F3F1ED;
        border-right: 1px solid #E4E2DE;
    }
    
    /* Titles and Headings */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        color: #4C1D95;
        text-align: center;
    }
    
    /* Answer Card with soft lavender background and clean left border */
    .answer-card {
        background: #F5F3FF;
        border: 1px solid #E9E3FF;
        border-left: 5px solid #8B5CF6;
        border-radius: 14px;
        padding: 26px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.04);
        color: #3B0764;
    }
    .answer-card h3 {
        color: #4C1D95 !important;
    }
    .answer-card li, .answer-card ul, .answer-card b {
        color: #3B0764 !important;
    }
    
    /* Technical Metrics Cards */
    .metric-card {
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    
    /* Metrics Color Coding */
    .metric-blue {
        background-color: #EFF6FF;
        border: 1px solid #DBEAFE;
    }
    .metric-blue .metric-value { color: #1E40AF !important; }
    .metric-blue .metric-label { color: #1D4ED8 !important; }
    
    .metric-gold {
        background-color: #FEF3C7;
        border: 1px solid #FDE68A;
    }
    .metric-gold .metric-value { color: #92400E !important; }
    .metric-gold .metric-label { color: #B45309 !important; }
    
    .metric-green {
        background-color: #DCFCE7;
        border: 1px solid #A7F3D0;
    }
    .metric-green .metric-value { color: #065F46 !important; }
    .metric-green .metric-label { color: #15803D !important; }
    
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Confidence Badge */
    .conf-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    /* Related Questions Pills */
    .related-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #4B5563;
        margin-top: 20px;
        margin-bottom: 10px;
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
        color: #4B5563;
    }
    
    /* Custom footer */
    .footer {
        text-align: center;
        padding: 60px 0 20px 0;
        color: #9CA3AF;
        font-size: 0.85rem;
        border-top: 1px solid #E5E7EB;
        margin-top: 50px;
    }
    
    /* Mobile responsiveness queries */
    @media (max-width: 640px) {
        .metric-value { font-size: 1.1rem; }
        .metric-label { font-size: 0.7rem; }
        .answer-card { padding: 18px; }
        h1 { font-size: 2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Answers Database -----------------
ANSWERS = {
    "Fees": """<h3 style="color:#4C1D95; margin-top:0; font-family:'Space Grotesk',sans-serif;">💰 Fees & Scholarships Details</h3>
<ul style="line-height: 1.6; margin-bottom: 0;">
    <li><b>Tuition Fees:</b> B.Tech tuition fee is <b>1,25,000 INR per semester</b>. MBA is <b>1,50,000 INR per semester</b>.</li>
    <li><b>Payment Modes:</b> Online via NetBanking, Credit/Debit cards, UPI, or offline via Demand Draft.</li>
    <li><b>Late Payments:</b> A penalty fine of <b>500 INR</b> applies if submitted after the semester deadline.</li>
    <li><b>Scholarships:</b>
        <ul>
            <li><b>Merit-Based:</b> Up to 50% tuition fee waiver for academic performance (&gt;90% marks).</li>
            <li><b>Need-Based:</b> Financial aid for economically weaker sections (EWS) upon document submission.</li>
        </ul>
    </li>
</ul>""",
    "Admissions": """<h3 style="color:#4C1D95; margin-top:0; font-family:'Space Grotesk',sans-serif;">📝 Admission & Eligibility</h3>
<ul style="line-height: 1.6; margin-bottom: 0;">
    <li><b>Application Deadline:</b> The deadline to apply online for the upcoming academic session is <b>July 31st</b>.</li>
    <li><b>Eligibility Criteria:</b>
        <ul>
            <li><b>B.Tech:</b> Minimum 60% aggregate in 12th standard (Physics, Chemistry, Mathematics).</li>
            <li><b>MBA / MCA:</b> Graduation with &gt;50% marks + qualifying score in CAT/MAT entrance exams.</li>
        </ul>
    </li>
    <li><b>Selection Process:</b> Standard document verification followed by cut-off based counseling slots.</li>
</ul>""",
    "Hostel": """<h3 style="color:#4C1D95; margin-top:0; font-family:'Space Grotesk',sans-serif;">🏠 Hostel & Mess Facilities</h3>
<ul style="line-height: 1.6; margin-bottom: 0;">
    <li><b>Accommodation:</b> Options for single, double, and triple sharing rooms (AC and Non-AC variants).</li>
    <li><b>Hostel Fees:</b> Starts at <b>85,000 INR per year</b> (includes room allotment, electricity, and 3 meals/day in the mess).</li>
    <li><b>Amenities:</b> High-speed Wi-Fi, laundry facilities, gym access, and sports equipment.</li>
    <li><b>Curfew & Rules:</b> Curfew is strictly <b>9:30 PM</b> for security reasons. Visitors are only allowed in the lobby.</li>
</ul>""",
    "Exams": """<h3 style="color:#4C1D95; margin-top:0; font-family:'Space Grotesk',sans-serif;">📅 Exams, Results & Backlogs</h3>
<ul style="line-height: 1.6; margin-bottom: 0;">
    <li><b>Timetable:</b> Semester-end theory examinations start on <b>December 5th</b>. Date sheets are published on the portal 15 days prior.</li>
    <li><b>Hall Tickets:</b> Downloadable from your student dashboard 1 week before exams.</li>
    <li><b>Assessments:</b> Mid-term internal exams count for 30% of the total grade; end-sem count for 70%.</li>
    <li><b>Backlogs & Revaluation:</b> Backlog clearing exams are held during summer breaks. Paper re-checks can be filed within 10 days of results.</li>
</ul>""",
    "Placement": """<h3 style="color:#4C1D95; margin-top:0; font-family:'Space Grotesk',sans-serif;">💼 Campus Placements & Internships</h3>
<ul style="line-height: 1.6; margin-bottom: 0;">
    <li><b>Average Package:</b> The average package for computer science placements is <b>8.5 LPA</b>. The highest package reached <b>44 LPA</b> this year.</li>
    <li><b>Recruitment Partners:</b> Amazon, Microsoft, Adobe, Deloitte, TCS, Infosys, and 120+ other companies.</li>
    <li><b>Placement Success:</b> Over <b>92%</b> placement rate for eligible students in the last academic year.</li>
    <li><b>Internships:</b> the Placement Cell organizes 3rd-year summer internship drives with average stipends of <b>25,000 INR/month</b>.</li>
</ul>""",
    "Other": """<h3 style="color:#4C1D95; margin-top:0; font-family:'Space Grotesk',sans-serif;">🌐 Campus Life & General Help</h3>
<ul style="line-height: 1.6; margin-bottom: 0;">
    <li><b>Library Timings:</b> Open <b>8:00 AM to 10:00 PM</b> on weekdays, and <b>9:00 AM to 5:00 PM</b> on weekends.</li>
    <li><b>Wi-Fi Access:</b> Register your laptop's MAC address at the IT Department block.</li>
    <li><b>Medical Care:</b> A 24/7 medical clinic with an ambulance and general practitioners is situated near the hostel block.</li>
    <li><b>Student Clubs:</b> 25+ clubs across robotics, drama, sports, and entrepreneurship.</li>
</ul>"""
}

RELATED_QUESTIONS = {
    "Fees": [
        "What are the criteria for merit-based scholarships?",
        "Can I pay the fees in installments?",
        "How do I request a refund if I withdraw?"
    ],
    "Admissions": [
        "What cut-off rank is required for B.Tech admission?",
        "Which entrance exams are accepted for MBA?",
        "What documents are needed for admission registration?"
    ],
    "Hostel": [
        "What amenities are provided in hostal double sharing?",
        "Is hostel accommodation mandatory for outstation students?",
        "Whom do I contact for hostel room allotment?"
    ],
    "Exams": [
        "How do I apply for revaluation of exam marks?",
        "What happens if I miss an exam due to medical reasons?",
        "What is the GPA scale structure?"
    ],
    "Placement": [
        "What companies visit for CSE placement drives?",
        "Does the college offer placement training/mock interviews?",
        "Are internship opportunities paid?"
    ],
    "Other": [
        "How do I register for campus Wi-Fi?",
        "What are the library hours on Sundays?",
        "Are there gym facilities or sports courts?"
    ]
}

# ----------------- Load Model Cache -----------------
@st.cache_resource
def get_classifier():
    model_dir = "./best_model"
    if not os.path.exists(model_dir):
        return None
    return FAQClassifier(model_dir=model_dir)

classifier = get_classifier()

# ----------------- Sidebar (Chat History) -----------------
with st.sidebar:
    st.image("https://img.icons8.com/nolan/64/chat.png", width=50)
    st.markdown("### 📜 Search History")
    
    if not st.session_state.chat_history:
        st.write("Your recent questions will appear here.")
    else:
        for idx, item in enumerate(reversed(st.session_state.chat_history)):
            # Show truncated query button
            lbl = item["query"]
            short_lbl = lbl[:28] + "..." if len(lbl) > 28 else lbl
            if st.button(f"🔍 {short_lbl}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.user_input = lbl
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ----------------- Main App UI Layout -----------------
st.title("🎓 College FAQ Assistant")
st.write("Ask a question about fees, admissions, hostel, exams, or placements to get an instant answer.")

if classifier is None:
    st.error("🚨 **Model checkpoints not found!** Run training first.")
    st.stop()

# FAQ Examples Row
st.write("**Quick Example Searches:**")
cols = st.columns(3)
examples = [
    "what is the average package for computer science placements",
    "What is the total fee structure for B.Tech?",
    "Is curfew time different for girls and boys hostel?"
]

if cols[0].button("💼 Average Package?", use_container_width=True):
    st.session_state.user_input = examples[0]
if cols[1].button("💰 B.Tech Fees?", use_container_width=True):
    st.session_state.user_input = examples[1]
if cols[2].button("🏠 Hostel Curfew?", use_container_width=True):
    st.session_state.user_input = examples[2]

# Search Bar Area with Search button next to it
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_query = st.text_input(
        "Enter your question:",
        value=st.session_state.user_input,
        placeholder="Type your question here (e.g. what are the document requirements for admission?)...",
        label_visibility="collapsed"
    )
with col_btn:
    search_clicked = st.button("🔍 Search", use_container_width=True)

# Run classification on query submission or button click
if user_query or search_clicked:
    with st.spinner("Finding answer..."):
        # Make prediction
        result = classifier.predict(user_query)
        predicted_cat = result['predicted_label']
        conf = result['confidence']
        
        # Save to chat history if not already the last one
        if not st.session_state.chat_history or st.session_state.chat_history[-1]["query"] != user_query:
            st.session_state.chat_history.append({
                "query": user_query,
                "category": predicted_cat,
                "confidence": conf
            })
            # Limit history to 8 items
            if len(st.session_state.chat_history) > 8:
                st.session_state.chat_history.pop(0)
        
        # Determine confidence colors and labels
        if conf >= 0.8:
            badge_bg = "rgba(16, 185, 129, 0.15)"
            badge_border = "#10b981"
            badge_lbl = "High Confidence"
        elif conf >= 0.5:
            badge_bg = "rgba(245, 158, 11, 0.15)"
            badge_border = "#f59e0b"
            badge_lbl = "Medium Confidence"
        else:
            badge_bg = "rgba(239, 68, 68, 0.15)"
            badge_border = "#ef4444"
            badge_lbl = "Low Confidence"
            
        # Display answer card
        answer_text = ANSWERS.get(predicted_cat, "No information available for this category.")
        st.markdown(f"""<div class="answer-card">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
<span class="conf-badge" style="background: {badge_bg}; border: 1px solid {badge_border}; color: {badge_border};">
{badge_lbl} ({conf * 100:.1f}%)
</span>
<span style="font-size: 0.85rem; color: #64748b; margin-bottom: 15px;">
Category: <b>{predicted_cat}</b>
</span>
</div>
{answer_text}
</div>""", unsafe_allow_html=True)
        
        # Action Buttons (👍 / 👎 / Copy)
        col_fb1, col_fb2, col_copy = st.columns([1, 1, 4])
        with col_fb1:
            if st.button("👍 Useful", key="like_btn"):
                st.toast("Thank you for your feedback!", icon="💖")
        with col_fb2:
            if st.button("👎 Not Useful", key="dislike_btn"):
                st.toast("Feedback recorded. We will improve this response.", icon="📝")
        with col_copy:
            # Render plain text formatted code block for one-click copy button
            plain_answer = answer_text.replace("<b>", "").replace("</b>", "").replace("<u>", "").replace("</u>", "").replace("<h3>", "### ").replace("</h3>", "\n").replace("<li>", "* ").replace("</li>", "\n").replace("<ul>", "").replace("</ul>", "")
            plain_answer = re.sub('<[^<]+?>', '', plain_answer).strip()
            with st.expander("📋 Copy Plain Text Answer"):
                st.code(plain_answer, language="markdown")
                
        # Related Questions Section
        related_qs = RELATED_QUESTIONS.get(predicted_cat, [])
        if related_qs:
            st.markdown('<div class="related-title">Related Questions:</div>', unsafe_allow_html=True)
            col_rel1, col_rel2, col_rel3 = st.columns(3)
            if col_rel1.button(related_qs[0], use_container_width=True, key="rel1"):
                st.session_state.user_input = related_qs[0]
                st.rerun()
            if col_rel2.button(related_qs[1], use_container_width=True, key="rel2"):
                st.session_state.user_input = related_qs[1]
                st.rerun()
            if col_rel3.button(related_qs[2], use_container_width=True, key="rel3"):
                st.session_state.user_input = related_qs[2]
                st.rerun()
        
        # Collapsible technical details
        with st.expander("🛠️ Show AI Model Technical Details"):
            st.markdown(f"**Predicted Intent:** `{predicted_cat}`")
            
            # Technical Metrics Columns
            col_perf1, col_perf2, col_perf3 = st.columns(3)
            with col_perf1:
                st.markdown(f"""
                <div class="metric-card metric-blue">
                    <div class="metric-value">{result['confidence'] * 100:.1f}%</div>
                    <div class="metric-label">Confidence</div>
                </div>
                """, unsafe_allow_html=True)
            with col_perf2:
                st.markdown(f"""
                <div class="metric-card metric-gold">
                    <div class="metric-value">{result['latency_ms']:.2f} ms</div>
                    <div class="metric-label">Latency</div>
                </div>
                """, unsafe_allow_html=True)
            with col_perf3:
                st.markdown(f"""
                <div class="metric-card metric-green">
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
