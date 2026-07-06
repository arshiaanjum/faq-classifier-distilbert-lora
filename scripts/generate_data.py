import os
import random
import pandas as pd

# Define classes
CATEGORIES = ["Fees", "Admissions", "Hostel", "Exams", "Placement", "Other"]

# Courses list for template filling
COURSES = ["B.Tech", "M.Tech", "MBA", "MCA", "B.Sc", "B.Com", "PhD", "BBA", "M.Sc", "engineering", "management", "computer science"]
CRITERIA = ["merit-based", "need-based", "sports quota", "SC/ST/OBC", "economically weaker section", "academic performance"]
PAYMENT_METHODS = ["online banking", "credit/debit card", "UPI", "demand draft", "net banking", "installments"]
ROOM_TYPES = ["single room", "double sharing", "triple sharing", "AC room", "non-AC room"]
SEMESTERS = ["first semester", "second semester", "final year", "odd semester", "even semester"]

# Question templates per category to generate diverse samples
TEMPLATES = {
    "Fees": [
        "What is the total fee structure for {course}?",
        "How much do I need to pay for the {semester} fees?",
        "Are there any {criteria} scholarships available?",
        "Can I pay my tuition fees via {payment}?",
        "What is the last date to submit the academic fees for {course}?",
        "Is there a penalty or late fee fine if I miss the deadline?",
        "Can the semester fees be paid in installments?",
        "How do I request a refund of my admission fees if I withdraw?",
        "Are exam fees included in the tuition fee or charged separately?",
        "Is there any financial aid or fee waiver for {criteria} students?",
        "How can I download the fee receipt for my payment?",
        "What are the extra charges apart from tuition fees?",
        "Is there a different fee structure for NRI or international students?",
        "Whom should I contact in the accounts department regarding fee discrepancies?",
        "How much is the laboratory and library security deposit fee?",
        "Does the college offer a discount on prepaying the annual fees?"
    ],
    "Admissions": [
        "What is the admission eligibility criteria for {course}?",
        "How can I apply for admission to the {course} program?",
        "When is the application deadline for the upcoming academic year?",
        "Which entrance exam score is required for {course} admissions?",
        "What was the cutoff rank or percentage for {course} last year?",
        "What documents do I need to upload during the application process?",
        "Is there a direct admission process or management quota?",
        "How can I check the status of my admission application?",
        "Is the admission registration fee refundable?",
        "When will the first merit list for {course} be released?",
        "How do I book a slot for the document verification process?",
        "Can I change my branch or specialization after taking admission?",
        "Are lateral entry admissions open for diploma holders?",
        "What is the intake capacity for the {course} course?",
        "Whom should I reach out to for admission helpline queries?",
        "Is the entrance exam mandatory for all applicants?"
    ],
    "Hostel": [
        "What are the hostel charges for a {room}?",
        "Is hostel accommodation compulsory for all {course} students?",
        "What basic amenities are provided in the {room}?",
        "How is the quality of food in the hostel mess?",
        "What is the daily curfew time for the student hostel?",
        "Is there high-speed Wi-Fi and laundry service in the hostel?",
        "How do I apply for hostel room allotment?",
        "Are parents or visitors allowed to visit the hostel rooms?",
        "What is the refund policy for hostel and mess deposits?",
        "Is there a separate hostel building for freshers?",
        "Are there separate girls and boys hostels on campus?",
        "What are the rules and regulations regarding hostel safety?",
        "Whom do I contact in case of maintenance issues in my hostel room?",
        "Is gym access included in the hostel fee?",
        "What happens if I want to leave the hostel mid-semester?",
        "Are students allowed to keep personal vehicles in the hostel?"
    ],
    "Exams": [
        "When are the final semester exams scheduled to begin?",
        "How can I download my exam hall ticket or admit card?",
        "What is the minimum passing percentage for the semester exams?",
        "How do I submit an application for paper revaluation or rechecking?",
        "What is the procedure to clear backlogs or reappear in a failed exam?",
        "How much weightage do internal mid-term assessments carry?",
        "What is the process if I miss an exam due to a medical emergency?",
        "When will the official results for the {semester} be declared?",
        "Is there a maximum number of backlogs allowed to move to the next year?",
        "What is the grading scale used for GPA calculation?",
        "How do I apply for an official transcript of my marksheet?",
        "Are external practical exams held before or after theory exams?",
        "What is the fee for appearing in a supplementary exam?",
        "Can I view my evaluated answer sheets?",
        "Where can I find the exam timetable and date sheet online?",
        "What is the passing criteria for practical lab sessions?"
    ],
    "Placement": [
        "Which top companies visit the campus for {course} placements?",
        "What is the average and highest salary package offered in placements?",
        "Does the college offer placement preparation classes or mock interviews?",
        "What percentage of {course} students got placed last year?",
        "Does the placement cell assist in securing internships?",
        "What are the eligibility criteria for participating in campus placements?",
        "How do I register with the university placement cell?",
        "Are off-campus placement drives supported by the college?",
        "Do companies offer pre-placement offers (PPOs) during internships?",
        "How many companies visit the campus annually for recruitment?",
        "Is there a placement policy regarding accepting multiple offers?",
        "Whom should I contact to get updates from the placement coordinators?",
        "Does the placement cell support entrepreneurship or startups?",
        "Are there placements for postgraduate courses like {course}?",
        "What domain-specific training is provided before placement drives?",
        "Are international job opportunities offered during placements?"
    ],
    "Other": [
        "What are the operating hours of the central library?",
        "How do I register my laptop for the campus Wi-Fi network?",
        "What student clubs or extracurricular activities can I join?",
        "What emergency medical services are available on campus?",
        "Does the college provide bus routes or transport facilities?",
        "Where is the campus lost and found office located?",
        "Who is the main contact person for student grievances?",
        "Does the campus have a gymnasium or indoor sports complex?",
        "Is there a cafeteria or food court on campus, and what are its timings?",
        "How can I apply for an duplicate student identity card?",
        "What is the address and location map of the campus?",
        "Are there guest house facilities available for visiting parents?",
        "How do I book the seminar hall or auditorium for student events?",
        "What security measures are in place across the campus?",
        "Is the campus wheelchair accessible?",
        "Who manages the alumni association and how do I join?"
    ]
}

def generate_data(samples_per_category=85):
    """
    Generates synthetic college FAQ dataset using predefined templates,
    random slot filling, and dynamic prefixes/suffixes to maximize variety.
    """
    prefixes = [
        "", "", "", # High probability of empty prefix for natural questions
        "Can you tell me ",
        "Could you please inform me ",
        "Do you know ",
        "Please let me know ",
        "I want to know ",
        "Can anyone tell me ",
        "I have a query about: ",
        "Quick question: "
    ]
    
    suffixes = [
        "?", "?", "?", # High probability of standard question mark
        " for the upcoming batch?",
        " for this academic year?",
        " for new admissions?",
        " as soon as possible?",
        " for international students?",
        " for the next semester?",
        "?"
    ]

    data = []
    
    for category, templates in TEMPLATES.items():
        generated_set = set()
        attempts = 0
        max_attempts = samples_per_category * 50
        
        while len(generated_set) < samples_per_category and attempts < max_attempts:
            template = random.choice(templates)
            formatted_q = template.format(
                course=random.choice(COURSES),
                criteria=random.choice(CRITERIA),
                payment=random.choice(PAYMENT_METHODS),
                room=random.choice(ROOM_TYPES),
                semester=random.choice(SEMESTERS)
            )
            
            # Add random variation using prefix and suffix
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            
            # Adjust capitalization if prefix is added
            if prefix:
                # lowercase the first letter of the formatted question if it's not a proper noun
                first_char = formatted_q[0].lower()
                rest = formatted_q[1:]
                # strip standard question mark from original if we add suffix
                if formatted_q.endswith("?"):
                    formatted_q = formatted_q[:-1]
                question = f"{prefix}{first_char}{rest}{suffix}"
            else:
                question = formatted_q
                
            generated_set.add(question.strip())
            attempts += 1
            
        for q in generated_set:
            data.append({"question": q, "label": category})
            
    df = pd.DataFrame(data)
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df

if __name__ == "__main__":
    print("Generating FAQ dataset...")
    df = generate_data(samples_per_category=85) # 85 * 6 = 510 sample questions
    
    # Create data/ directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    csv_path = "data/faq_dataset.csv"
    
    df.to_csv(csv_path, index=False)
    print(f"Dataset generated successfully! Saved {len(df)} samples to {csv_path}")
    print("\nClass Distribution:")
    print(df["label"].value_counts())
