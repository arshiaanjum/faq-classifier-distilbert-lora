# College FAQ Classifier (PEFT-LoRA)

A parameter-efficient text classification system that takes a college FAQ-style question as input and predicts its category (Fees, Admissions, Hostel, Exams, Placement, or Other). It fine-tunes only LoRA adapter weights on a pretrained `distilbert-base-uncased` model, achieving 98%+ storage savings compared to full fine-tuning.

---

## Project Structure
```
faq-classifier-distilbert-lora/
├── data/
│   └── faq_dataset.csv          # Generated/Cleaned FAQ pairs
├── scripts/
│   └── generate_data.py         # Script to synthesize the dataset
├── train.py                     # LoRA training & evaluation pipeline
├── inference.py                 # Inference helper & latency benchmarking
├── app.py                       # Streamlit UI for interactive demo
├── requirements.txt             # Project dependencies
└── README.md                    # Setup and guide (this file)
```

---

## Step-by-Step Local Setup

Follow these steps in your terminal to set up the project on your local machine.

### 1. Set Up a Virtual Environment (Recommended)
Open your terminal and navigate to the project directory, then run:

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Project Dependencies
Install all the required packages using pip:

```bash
pip install -r requirements.txt
```

### 3. Generate the Dataset
Create the synthetic FAQ dataset containing 510 balanced questions across 6 categories:

```bash
python scripts/generate_data.py
```

### 4. Run the Training Pipeline
Start the training and evaluation loop. This script automatically detects if a GPU (CUDA) or Apple Silicon (MPS) is available, falling back to CPU if not:

```bash
python train.py
```

### 5. Launch the Streamlit App
Once training finishes and the adapter is saved under `./best_model/`, launch the interactive web interface:

```bash
streamlit run app.py
```

---

## LoRA Efficiency & Key Outcome

### 1. Parameter Reduction
Instead of fine-tuning all **66 Million parameters** of DistilBERT:
* **Trainable parameters:** ~628,230 (only **0.93%** of the base model).
* **Saved Weight Size:** The fine-tuned LoRA adapter files are only **~3.2 MB**, compared to **~268 MB** for a full model checkpoint.
* **Storage reduction:** **98.8%** reduction in storage costs.

### 2. Average Latency
* **CPU Inference Latency:** ~45-70 milliseconds per query.
* **MPS (Apple Silicon) / GPU Latency:** ~15-25 milliseconds per query.

---

## Running in Google Colab (Free GPU Training)

If training is slow on your local CPU, you can run training on a free T4 GPU in Google Colab:

1. Create a new Google Colab notebook.
2. Upload the `data/faq_dataset.csv` file, `train.py`, and `requirements.txt` to your Colab session.
3. Install the dependencies:
   ```python
   !pip install -r requirements.txt
   ```
4. Run the training script:
   ```python
   !python train.py
   ```
5. Download the `./best_model` folder generated in Colab back to your local project directory to run `inference.py` and `app.py`.

---

## Git & GitHub Commands Guide

To push this project to your GitHub repository:

### 1. Initialize Git in the Project Directory
Run these commands in your local project root:

```bash
# Initialize a local git repository
git init

# Add a .gitignore file to prevent uploading large cache files or virtual environments
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "results/" >> .gitignore
echo ".DS_Store" >> .gitignore

# Add all files to staging
git add .

# Create the initial commit
git commit -m "Initial commit: DistilBERT LoRA FAQ Classifier structure"
```

### 2. Connect to GitHub and Push
Go to [GitHub](https://github.com), create a new repository (e.g. `faq-classifier-distilbert-lora`), and do **not** initialize it with a README. Copy the repository URL, then run:

```bash
# Rename the default branch to main
git branch -M main

# Add your GitHub repository as a remote named 'origin'
# (Replace your-username with your actual GitHub username)
git remote add origin https://github.com/your-username/faq-classifier-distilbert-lora.git

# Push the code to GitHub
git push -u origin main
```
