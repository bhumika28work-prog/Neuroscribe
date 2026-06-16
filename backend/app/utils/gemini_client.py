"""
=============================================================
  app/utils/gemini_client.py — Google Gemini API Client
=============================================================

📌 WHAT IS THIS FILE?
  This is the utility module for communicating with the Google Gemini API.
  It configures the SDK and performs prompt engineering to generate:
  1. A structured clinical summary for doctors.
  2. An empathetic plain-language explanation for patients.

📌 PRIMARY MODEL: gemini-3.5-flash
  Gemini 3.5 Flash is highly fast, extremely accurate, and ideal for 
  document analysis and summarization.

📌 CLEAN ARCHITECTURE ROLE:
  Utility layer. Service layer handles the database session, while this 
  module deals only with external API communication.
"""

import google.generativeai as genai
import logging
from app.core.config import settings

# Set up standard logger
logger = logging.getLogger("gemini_client")


class GeminiAPIError(Exception):
    """Custom exception raised when the Gemini API call fails."""
    pass


# ──────────────────────────────────────────────
# SDK CONFIGURATION
# ──────────────────────────────────────────────

# We check if the GEMINI_API_KEY is configured in the environment settings.
# If missing, we log a warning. Note that we don't crash on startup so that
# health check or non-AI routes can still run without an API key.
if settings.GEMINI_API_KEY:
    try:
        logger.info("Initializing Google Generative AI client...")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Generative AI client successfully configured.")
    except Exception as e:
        logger.error(f"Failed to configure Generative AI client: {str(e)}", exc_info=True)
else:
    logger.warning(
        "⚠️ GEMINI_API_KEY is not configured in settings! "
        "AI Summarization requests will fail until a valid key is provided in .env."
    )


# ──────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────

def generate_clinical_summaries(extracted_text: str) -> tuple[str, str]:
    """
    Generate a highly structured clinical summary for healthcare professionals
    in both English and clinical Hindi using a single Gemini API call.
    """
    import os
    if os.environ.get("MOCK_GEMINI", "true").lower() == "true":
        eng_summary = "### 📋 Patient & Study Information\n- **Name**: Rahul Sharma\n- **Age**: 35\n- **Gender**: Male\n\n### 🔍 Key Findings & Observations\n- Mild mucosal thickening is present in the maxillary sinuses.\n\n### ⚠️ Critical Concerns\n- No acute abnormal findings identified.\n\n### 💡 Clinical Impression & Next Steps\n- Correlate with clinical findings."
        hin_summary = "### 📋 रोगी एवं अध्ययन विवरण\n- **नाम**: राहुल शर्मा\n- **आयु**: 35\n- **लिंग**: पुरुष\n\n### 🔍 मुख्य निष्कर्ष\n- मैक्सिलरी साइनस में हल्की म्यूकोसल सूजन देखी गई है।\n\n### ⚠️ गंभीर चिंताएं\n- कोई तीव्र असामान्य निष्कर्ष नहीं मिले।\n\n### 💡 नैदानिक प्रभाव एवं अगले कदम\n- चिकित्सक से परामर्श लें।"
        return eng_summary, hin_summary

    if not settings.GEMINI_API_KEY:
        raise GeminiAPIError("Gemini API Key is not configured. Please add GEMINI_API_KEY to your .env file.")

    if not extracted_text.strip():
        return "No text available to summarize.", "विवरण के लिए कोई टेक्स्ट उपलब्ध नहीं है।"

    # Define structured clinical prompt for both English and Hindi
    prompt = (
        "You are an expert medical AI assistant. Your task is to analyze the following extracted text "
        "from a medical report and generate a highly professional, structured clinical summary for doctors. "
        "You must generate BOTH an English clinical summary and a Hindi clinical summary.\n\n"
        
        "You MUST format the output exactly as follows with the two sections separated by the specified markers. Do not include any introductory or concluding conversational text outside the markers:\n\n"
        
        "=== ENGLISH CLINICAL SUMMARY ===\n"
        "Please format the response in clean Markdown using the following exact sections:\n"
        "### 📋 Patient & Study Information\n"
        "- Name, Age, Gender, Date of Study, Referring Physician (if mentioned, otherwise mark 'Not Specified').\n\n"
        "### 🔍 Key Findings & Observations\n"
        "- Summarize all primary findings, measurements, and clinical observations from the report clearly.\n\n"
        "### ⚠️ Critical Concerns\n"
        "- Highlight any abnormal findings, acute pathologies, red flags, or areas requiring immediate clinical attention. "
        "If everything is normal, state 'No acute abnormal findings identified.'\n\n"
        "### 💡 Clinical Impression & Next Steps\n"
        "- Summarize the primary clinical impression and any recommended follow-up tests, consultations, or monitoring.\n\n"
        
        "=== HINDI CLINICAL SUMMARY ===\n"
        "Here, write the summary in clinical Hindi (written in Devanagari script). Ensure it:\n"
        "- Is concise and shorter than a patient explanation.\n"
        "- Preserves precise medical meaning.\n"
        "- Does not oversimplify clinical findings.\n"
        "- Follows the same clinical sections structure (translated to Hindi, e.g. रोगी एवं अध्ययन विवरण, मुख्य निष्कर्ष, गंभीर चिंताएं, नैदानिक प्रभाव एवं अगले कदम).\n"
        "- Use the following style as a guideline:\n"
        "\"दोनों मैक्सिलरी साइनस में हल्की सूजन पाई गई है। मस्तिष्क में कोई गंभीर या आपातकालीन असामान्यता नहीं मिली।\"\n\n"
        
        "**Strict Guidelines for both:**\n"
        "- Maintain absolute clinical accuracy. Do not make up or assume any data not directly mentioned or strongly implied.\n"
        "- Keep the tone professional, objective, and clinical.\n\n"
        
        f"--- EXTRACTED MEDICAL REPORT TEXT ---\n{extracted_text}\n--------------------------------------"
    )

    try:
        logger.info("Calling Gemini API to generate clinical summaries (English & Hindi)...")
        model = genai.GenerativeModel("gemini-3.5-flash")
        
        # Call the API with generation parameters
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Low temperature for highly deterministic/factual clinical results
            )
        )
        
        if not response.text:
            raise GeminiAPIError("Received an empty response from the Gemini API.")

        logger.info("Successfully generated clinical summaries.")
        text = response.text.strip()
        
        # Parse the English and Hindi parts using markers
        eng_marker = "=== ENGLISH CLINICAL SUMMARY ==="
        hin_marker = "=== HINDI CLINICAL SUMMARY ==="
        
        english_summary = ""
        hindi_summary = ""
        
        if eng_marker in text and hin_marker in text:
            eng_idx = text.find(eng_marker)
            hin_idx = text.find(hin_marker)
            if eng_idx < hin_idx:
                english_summary = text[eng_idx + len(eng_marker):hin_idx].strip()
                hindi_summary = text[hin_idx + len(hin_marker):].strip()
            else:
                hindi_summary = text[hin_idx + len(hin_marker):eng_idx].strip()
                english_summary = text[eng_idx + len(eng_marker):].strip()
        elif hin_marker in text:
            parts = text.split(hin_marker)
            english_summary = parts[0].replace(eng_marker, "").strip()
            hindi_summary = parts[1].strip()
        else:
            english_summary = text
            hindi_summary = "Hindi summary not generated."
            
        return english_summary, hindi_summary

    except Exception as e:
        error_msg = f"Gemini API clinical summaries generation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise GeminiAPIError(error_msg)


def generate_clinical_summary(extracted_text: str) -> str:
    """
    Generate a highly structured clinical summary for healthcare professionals (English only).
    Maintained for backward compatibility.
    """
    eng, _ = generate_clinical_summaries(extracted_text)
    return eng


def generate_patient_explanations(extracted_text: str) -> tuple[str, str]:
    """
    Generate an empathetic, layman-friendly explanation of findings for the patient
    in both English and simple everyday Hindi using a single Gemini API call.
    """
    import os
    if os.environ.get("MOCK_GEMINI", "true").lower() == "true":
        eng_explanation = "### Summary\nThe brain MRI shows normal findings overall.\n\n### What this is\nA brain MRI is an imaging scan that creates pictures of the brain.\n\n### Common symptoms\nYou may notice headaches or sinus pressure, but these are not severe.\n\n### Why it happens\nMild sinus swelling can be due to allergies or a minor infection.\n\n### Why we are concerned\nThere are no serious concerns, but monitor any worsening symptoms.\n\n### Tests and results\nThe MRI did not find any acute abnormalities.\n\n### Treatment plan\nNo specific treatment needed; consider allergy management if symptoms persist.\n\n### What to expect next\nSymptoms should improve; follow up with your doctor if they worsen.\n\n### Lifestyle changes\nStay hydrated, use saline nasal sprays, and avoid known allergens.\n\n### Red flags\nSeek medical attention if you develop severe headache, vision changes, or fever.\n\n### Questions to ask your doctor\n- Should I take any medication for sinus swelling?\n- What signs indicate I need further testing?\n- How can I prevent future sinus issues?"
        
        hin_explanation = "### सारांश\nदिमाग की MRI में कुल मिलाकर कोई असामान्य चीज़ नहीं मिली है।\n\n### यह क्या है\nMRI एक ऐसी इमेजिंग स्कैन है जो दिमाग की तस्वीरें बनाती है।\n\n### सामान्य लक्षण\nआपको सिर में दर्द या साइनस का दबाव महसूस हो सकता है, पर यह गंभीर नहीं है।\n\n### कारण\nहल्का साइनस सूजन एलर्जी या मामूली संक्रमण के कारण हो सकती है।\n\n### चिंता क्यों?\nकोई गंभीर समस्या नहीं है, फिर भी यदि लक्षण बिगड़ें तो देखना जरूरी है।\n\n### परीक्षण और परिणाम\nMRI में कोई तात्कालिक असामान्य नहीं मिला।\n\n### उपचार योजना\nविशेष उपचार आवश्यक नहीं है; यदि लक्षण जारी रहें तो एलर्जी का प्रबंधन करें।\n\n### आगे क्या उम्मीद करें\nलक्षण सुधरने चाहिए; यदि बदतर हों तो डॉक्टर से मिलें।\n\n### जीवनशैली परिवर्तन\nपानी अधिक पिएँ, नमकिंट स्प्रे उपयोग करें, और ज्ञात एलर्जियों से बचें।\n\n### चेतावनी संकेत\nतीव्र सिर दर्द, दृष्टि में बदलाव या बुखार हो तो तुरंत डॉक्टर से मिलें।\n\n### डॉक्टर से पूछने वाले प्रश्न\n- क्या मुझे साइनस की सूजन के लिये दवा लेनी चाहिए?\n- किन संकेतों से आगे की जांच की आवश्यकता है?\n- भविष्य में साइनस की समस्या रोकने के लिये क्या करूँ?"
        
        return eng_explanation, hin_explanation

    if not settings.GEMINI_API_KEY:
        raise GeminiAPIError("Gemini API Key is not configured. Please add GEMINI_API_KEY to your .env file.")

    if not extracted_text.strip():
        return "No text available to explain.", "विवरण के लिए कोई टेक्स्ट उपलब्ध नहीं है."

    # Define an empathetic layman explanation prompt for both English and Hindi
    prompt = (
    "You are an empathetic, warm, and highly experienced patient communicator. Your task is to translate the following "
    "extracted medical report text into clear, comforting, and simple explanations that the patient can easily understand. "
    "You must generate BOTH an English explanation and a Hindi explanation.\n\n"
    "\n"
    "You MUST format the output exactly as follows with the two sections separated by the specified markers. Do not include any introductory or concluding conversational text outside the markers:\n\n"
    "\n"
    "=== ENGLISH PATIENT EXPLANATION ===\n"
    "### 👋 Welcome & Overview\n"
    "- Greet the patient warmly and give a brief overview of what this report covers.\n\n"
    "### 📄 What the Report Means\n"
    "- Explain in plain language what the main findings indicate, using everyday analogies.\n\n"
    "### 🤒 Common Symptoms\n"
    "- List typical symptoms related to the findings, described in simple terms.\n\n"
    "### 🧬 Why It Happens\n"
    "- Provide a brief explanation of the underlying reasons or causes in layman terms.\n\n"
    "### ⚠️ Why We Are Concerned\n"
    "- Discuss why these findings matter for the patient's health, stressing any important implications.\n\n"
    "### 🧪 Tests and Results\n"
    "- Summarize any tests performed and what the results show, avoiding technical jargon.\n\n"
    "### 💊 Treatment Plan\n"
    "- Outline recommended treatments or next steps in clear, actionable language.\n\n"
    "### 📅 What to Expect Next\n"
    "- Explain the likely course of action and timeline for follow‑up.\n\n"
    "### 🏃‍♀️ Lifestyle Changes\n"
    "- Suggest practical lifestyle adjustments that can help, described simply.\n\n"
    "### 🚨 Red Flags\n"
    "- Highlight warning signs that should prompt the patient to seek immediate medical attention.\n\n"
    "### ❓ Questions to Ask Your Doctor\n"
    "- Provide a short list of helpful questions the patient might want to discuss with their physician.\n\n"
    "### 📚 Medical Terms Dictionary\n"
    "- Pick 3‑5 complex terms from the report and define them in extremely simple, friendly language.\n\n"
    "### 🌱 Reassurance & Next Steps\n"
    "- Offer comforting reassurance and encourage follow‑up with their doctor, including suggested questions.\n\n"
    "\n"
    "=== HINDI PATIENT EXPLANATION ===\n"
    "Here, write the explanation in simple, everyday Hindi (Devanagari script). It must be easily understandable by non‑medical users, avoid jargon, and follow the same section structure as English. Use these guidelines:\n"
    "- प्रत्येक सेक्शन को ऊपर बताए गए अंग्रेजी सेक्शन के समान क्रम में लिखें।\n"
    "- सरल शब्दों में समझाएँ, जैसे सामान्य रोग की लक्षण, कारण, उपचार आदि।\n"
    "- आश्वासन दें और डॉक्टर से मिलने की सलाह दें।\n"
    "- महत्वपूर्ण बातों को उजागर करने के लिए लाल झंडे (Red Flags) का उल्लेख करें।\n"
    "- डॉक्टर से पूछने योग्य प्रश्नों की सूची दें।\n"
    "\n"
    "--- EXTRACTED MEDICAL REPORT TEXT ---\n{extracted_text}\n--------------------------------------"
)

    try:
        logger.info("Calling Gemini API to generate patient explanations (English & Hindi)...")
        model = genai.GenerativeModel("gemini-3.5-flash")
        
        # Call the API with generation parameters
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,  # Slightly higher temperature for warmer, more natural human tone
            )
        )
        
        if not response.text:
            raise GeminiAPIError("Received an empty response from the Gemini API.")

        logger.info("Successfully generated patient explanations.")
        text = response.text.strip()
        
        # Parse the English and Hindi parts using markers
        eng_marker = "=== ENGLISH PATIENT EXPLANATION ==="
        hin_marker = "=== HINDI PATIENT EXPLANATION ==="
        
        english_explanation = ""
        hindi_explanation = ""
        
        if eng_marker in text and hin_marker in text:
            eng_idx = text.find(eng_marker)
            hin_idx = text.find(hin_marker)
            if eng_idx < hin_idx:
                english_explanation = text[eng_idx + len(eng_marker):hin_idx].strip()
                hindi_explanation = text[hin_idx + len(hin_marker):].strip()
            else:
                hindi_explanation = text[hin_idx + len(hin_marker):eng_idx].strip()
                english_explanation = text[eng_idx + len(eng_marker):].strip()
        elif hin_marker in text:
            parts = text.split(hin_marker)
            english_explanation = parts[0].replace(eng_marker, "").strip()
            hindi_explanation = parts[1].strip()
        else:
            english_explanation = text
            hindi_explanation = "Hindi explanation not generated."
            
        return english_explanation, hindi_explanation

    except Exception as e:
        error_msg = f"Gemini API patient explanations generation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise GeminiAPIError(error_msg)


def generate_patient_explanation(extracted_text: str) -> str:
    """
    Generate an empathetic, layman-friendly explanation of findings for the patient (English only).
    Maintained for backward compatibility.
    """
    eng, _ = generate_patient_explanations(extracted_text)
    return eng
