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
        eng_explanation = "### 👋 Welcome & Overview\nHello Rahul, your brain MRI is normal.\n\n### 🧠 What They Found\nThere is mild swelling in your sinuses.\n\n### 💬 Medical Terms Dictionary\n- Maxillary sinus: Air pockets behind cheeks.\n\n### 🌱 Reassurance & Next Steps\nSpeak with your doctor."
        hin_explanation = "### 👋 स्वागत और संक्षिप्त विवरण\nनमस्ते राहुल जी, आपके दिमाग का स्कैन सामान्य है।\n\n### 🧠 रिपोर्ट में क्या मिला?\nआपके चेहरे के साइनस में हल्की सूजन है।\n\n### 💬 मुख्य चिकित्सा शब्दों का अर्थ\n- मैक्सिलरी साइनस: गालों के पीछे हवा की थैलियां।\n\n### 🌱 आश्वासन और अगले कदम\nचिकित्सक से परामर्श लें।"
        return eng_explanation, hin_explanation

    if not settings.GEMINI_API_KEY:
        raise GeminiAPIError("Gemini API Key is not configured. Please add GEMINI_API_KEY to your .env file.")

    if not extracted_text.strip():
        return "No text available to explain.", "विवरण के लिए कोई टेक्स्ट उपलब्ध नहीं है।"

    # Define an empathetic layman explanation prompt for both English and Hindi
    prompt = (
        "You are an empathetic, warm, and highly experienced patient communicator. Your task is to translate the following "
        "extracted medical report text into clear, comforting, and simple explanations that the patient can easily understand. "
        "You must generate BOTH an English explanation and a Hindi explanation.\n\n"
        
        "You MUST format the output exactly as follows with the two sections separated by the specified markers. Do not include any introductory or concluding conversational text outside the markers:\n\n"
        
        "=== ENGLISH PATIENT EXPLANATION ===\n"
        "### 👋 Welcome & Overview\n"
        "- A brief, warm greeting explaining what this report is about in simple terms.\n\n"
        "### 🧠 What They Found (In Plain English)\n"
        "- Explain the main findings using everyday analogies and layperson terms. Absolutely avoid complex medical jargon "
        "without immediately translating or explaining it simply. (e.g. explain 'microvascular ischemic changes' as 'tiny wear-and-tear changes in blood vessels').\n\n"
        "### 💬 Medical Terms Dictionary\n"
        "- Pick 3-5 complex medical terms found in the report and define them in extremely simple, friendly terms.\n\n"
        "### 🌱 Reassurance & Next Steps\n"
        "- Provide warm reassurance. Emphasize that they should discuss these findings with their doctor for professional guidance. "
        "Suggest simple questions they might want to ask their doctor.\n\n"
        
        "=== HINDI PATIENT EXPLANATION ===\n"
        "Here, write the explanation in simple, everyday Hindi (written in Devanagari script). It must be easily understandable by non-medical users, "
        "avoid unnecessary medical jargon, and explain findings clearly. Ensure you:\n"
        "- Explain what they found in clear, daily-use Hindi.\n"
        "- Mention if findings appear normal.\n"
        "- Emphasize reassurance and advise doctor consultation. Use the following style as a guideline:\n"
        "\"इस रिपोर्ट में दिमाग से जुड़ी कोई गंभीर समस्या नहीं मिली है।\n"
        "नाक के आसपास की साइनस गुहाओं में हल्की सूजन दिखाई दे रही है। यह एलर्जी या संक्रमण के कारण हो सकती है।\n"
        "अधिक जानकारी के लिए अपने डॉक्टर से सलाह लें।\"\n"
        "- Never create diagnoses that are not present in the report.\n\n"
        
        "**Strict Guidelines for both:**\n"
        "- Keep the tone comforting, clear, and supportive. Empathize and reduce anxiety, but do not hide abnormal results—instead, explain them gently.\n"
        "- Do not diagnose or prescribe treatment.\n\n"
        
        f"--- EXTRACTED MEDICAL REPORT TEXT ---\n{extracted_text}\n--------------------------------------"
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
