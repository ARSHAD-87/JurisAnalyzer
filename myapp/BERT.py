from transformers import BertTokenizer, BertModel
import torch
import PyPDF2
from docx import Document as DocxDocument
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
import os

# Download required NLTK data at runtime if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')  # For newer NLTK versions
except LookupError:
    nltk.download('punkt_tab')

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() for page in reader.pages])
    elif file_path.endswith('.docx'):
        doc = DocxDocument(file_path)
        text = ' '.join([para.text for para in doc.paragraphs])
    else:
        with open(file_path, 'r') as file:
            text = file.read()
    return text

def analyze_document(file_path):
    text = extract_text(file_path)
    summary, risks = analyze_document_text(text)
    return summary, risks

def analyze_document_text(text, summary_sentences=100, risk_keywords=None):
    if not text or not isinstance(text, str):
        return "Error: Invalid input text", "No risks analyzed"

    if risk_keywords is None:
        risk_keywords = [
            "dispute", "liability", "breach", "penalty", "violation", 
            "lawsuit", "non-compliance", "risk", "default", "termination"
        ]

    # Split text into sentences
    sentences = sent_tokenize(text)
    if len(sentences) < 1:
        return "Error: No sentences detected", "No risks analyzed"

    # Generate BERT embeddings for each sentence
    sentence_embeddings = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True, max_length=1024)
        with torch.no_grad():
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
        sentence_embeddings.append(embedding)

    sentence_embeddings = np.array(sentence_embeddings)

    # Compute sentence importance scores
    doc_embedding = np.mean(sentence_embeddings, axis=0)
    similarity_scores = [
        np.dot(sent_emb, doc_embedding) / (np.linalg.norm(sent_emb) * np.linalg.norm(doc_embedding))
        for sent_emb in sentence_embeddings
    ]

    # Select top sentences for summary
    ranked_indices = np.argsort(similarity_scores)[::-1]
    top_indices = ranked_indices[:min(int(len(sentences)*(0.50)), len(sentences))]
    top_indices = sorted(top_indices)
    summary = " ".join([sentences[i] for i in top_indices])
    print(f"\n\nSummary\n\n{summary}\n\n")
    # Identify risks
    risk_sentences = []
    for i, sentence in enumerate(sentences):
        if any(keyword.lower() in sentence.lower() for keyword in risk_keywords):
            risk_sentences.append(sentence)

    risks = "\n".join(risk_sentences) if risk_sentences else "No risks identified"
    print(f"\n\nRisk\n\n{risks}\n\n")

    return summary, risks


def handle_uploaded_file(file_path):
    # Process the file and generate summary and risks
    summary, risks = analyze_document(file_path)

    # Ensure the summary and risks are returned as lists of sentences
    formatted_summary = [
        sentence for sentence in sent_tokenize(summary) if len(sentence.split()) >= 3
    ]  # Filter out sentences with fewer than 3 words
    formatted_risks = [
        sentence for sentence in sent_tokenize(risks) if len(sentence.split()) >= 3
    ]  # Filter out sentences with fewer than 3 words

    # Generate a PDF file for the result
    pdf_file_path = generate_pdf(formatted_summary, formatted_risks)

    return {
        "summary": formatted_summary,
        "risks": formatted_risks,
        "pdf_file": pdf_file_path  # Return the path to the generated PDF
    }
    
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import os

def generate_pdf(summary, risks):
    # Define the output PDF file path
    pdf_file_path = os.path.join("outputs", "analysis_result.pdf")
    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)  # Ensure the outputs directory exists

    # Create a canvas for the PDF
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    width, height = letter

    # Set font
    font_path = os.path.join("C:\\Pro\\project\\myapp\\fonts\\dejavu-fonts-ttf-2.37\\ttf", "DejaVuSans.ttf")
    c.setFont("Helvetica", 12)  # Use a default font for now

    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Analysis Result")

    # Add summary section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 80, "Summary:")
    c.setFont("Helvetica", 10)
    y_position = height - 100
    for line in summary:
        wrapped_lines = simpleSplit(f"• {line}", "Helvetica", 10, width - 100)
        for wrapped_line in wrapped_lines:
            c.drawString(50, y_position, wrapped_line)
            y_position -= 12
            if y_position < 50:  # Add a new page if space runs out
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - 50

    # Add risks section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position - 20, "Risks:")
    c.setFont("Helvetica", 10)
    y_position -= 40
    for line in risks:
        wrapped_lines = simpleSplit(f"• {line}", "Helvetica", 10, width - 100)
        for wrapped_line in wrapped_lines:
            c.drawString(50, y_position, wrapped_line)
            y_position -= 12
            if y_position < 50:  # Add a new page if space runs out
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - 50

    # Save the PDF
    c.save()

    return pdf_file_path