# ============================================================
# Anti-Fraud SMS Detector (Placeholder Version)
# Uses pre-trained models so the UI can be tested before
# fine-tuning is complete.
# ============================================================
import streamlit as st
from transformers import pipeline


# -----------------------------------------------------------
# Function: load_models
# Purpose: Load placeholder models (replace with your fine-tuned
#          models once training is done)
# -----------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_models():
    """Load placeholder models for UI testing."""
    # Placeholder binary classifier (spam vs ham)
    binary_classifier = pipeline(
        "text-classification",
        model="mrm8488/bert-tiny-finetuned-sms-spam-detection",
    )
    # Placeholder multi-class classifier (temporary)
    type_classifier = pipeline(
        "text-classification",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )
    return binary_classifier, type_classifier


# -----------------------------------------------------------
# Function: analyze_sms
# Purpose: Run both models on the input SMS text
# -----------------------------------------------------------
def analyze_sms(text, binary_classifier, type_classifier):
    """Return binary result and, if fraud, scam type."""
    binary_result = binary_classifier(text)[0]
    label = binary_result["label"].upper()

    # The placeholder model uses LABEL_0 / LABEL_1
    # Adjust this logic when you swap in your own model
    is_fraud = label in ["LABEL_1", "SPAM", "FRAUD"]

    result = {
        "is_fraud": is_fraud,
        "binary_label": binary_result["label"],
        "binary_score": binary_result["score"],
        "type_label": None,
        "type_score": None,
    }

    if is_fraud:
        type_result = type_classifier(text)[0]
        result["type_label"] = type_result["label"]
        result["type_score"] = type_result["score"]

    return result


# -----------------------------------------------------------
# Function: main
# Purpose: Build the Streamlit UI
# -----------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Anti-Fraud SMS Detector",
        page_icon="🛡️",
        layout="centered",
    )

    st.title("🛡️ Anti-Fraud SMS Detector")
    st.caption(
        "Paste a suspicious SMS and AI will analyze it "
        "for fraud risk and scam type."
    )

    # Load models
    with st.spinner("Loading models..."):
        try:
            binary_classifier, type_classifier = load_models()
            st.success("✅ Models loaded successfully")
        except Exception as e:
            st.error(f"❌ Model loading failed: {str(e)}")
            st.stop()

    # Input
    sms_text = st.text_area(
        "Paste the SMS content",
        height=150,
        placeholder="e.g., Congratulations! You have won a prize. Click the link to claim...",
    )

    if st.button("Start Analysis", type="primary"):
        if not sms_text.strip():
            st.warning("⚠️ Please enter SMS content first.")
        else:
            with st.spinner("Analyzing..."):
                result = analyze_sms(
                    sms_text, binary_classifier, type_classifier
                )

            st.divider()
            st.subheader("📊 Analysis Result")

            # Binary result
            if result["is_fraud"]:
                st.error(
                    f"🔴 Fraud detected "
                    f"(confidence: {result['binary_score']:.1%})"
                )
            else:
                st.success(
                    f"🟢 Normal message "
                    f"(confidence: {result['binary_score']:.1%})"
                )

            # Scam type
            if result["is_fraud"] and result["type_label"]:
                st.subheader("🏷️ Scam Type")
                st.info(
                    f"**{result['type_label']}** "
                    f"(confidence: {result['type_score']:.1%})"
                )

            # Advice
            st.subheader("💡 Recommendations")
            st.markdown("""
            - Do not click any links in the message
            - Do not reply or share personal information
            - Verify through official channels
            - Report to your bank if you already responded
            """)

    st.divider()
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **Two Pipelines**:
        1. `text-classification` (binary): mrm8488/bert-tiny-finetuned-sms-spam-detection
        2. `text-classification` (multi-class): distilbert-base-uncased-finetuned-sst-2-english

        **Note**: These are placeholder models. Replace them with your own
        fine-tuned models once training is complete.

        **Flow**: `SMS input` → `Binary check` → `Scam type check` → `Result`
        """)


if __name__ == "__main__":
    main()
