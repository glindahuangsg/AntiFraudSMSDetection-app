# ============================================================
# Anti-Fraud SMS Detection App
# Two fine-tuned models: binary classification + scam type
# ============================================================
import streamlit as st
from transformers import pipeline

# -----------------------------------------------------------
# Function: load_models
# Purpose: Load and cache both fine-tuned models
# -----------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_models():
    """Load both fine-tuned models from Hugging Face Hub."""
    binary_classifier = pipeline(
        "text-classification",
        model="your-username/anti-fraud-binary",
    )
    type_classifier = pipeline(
        "text-classification",
        model="your-username/anti-fraud-type",
    )
    return binary_classifier, type_classifier


# -----------------------------------------------------------
# Function: analyze_sms
# Purpose: Run both models on the input SMS text
# -----------------------------------------------------------
def analyze_sms(text, binary_classifier, type_classifier):
    """Return binary result and, if fraud, scam type."""
    binary_result = binary_classifier(text)[0]
    is_fraud = binary_result["label"].lower() in ["spam", "label_1", "1"]

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
        1. `text-classification` (binary): your-username/anti-fraud-binary
        2. `text-classification` (multi-class): your-username/anti-fraud-type

        **Flow**: `SMS input` → `Binary check` → `Scam type check` → `Result`
        """)


if __name__ == "__main__":
    main()
