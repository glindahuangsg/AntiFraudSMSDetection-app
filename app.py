# ============================================================
# Anti-Fraud SMS Detector (Placeholder Version)
# Uses pre-trained models so the UI can be tested before
# fine-tuning is complete.
# ============================================================
import traceback
import streamlit as st
from transformers import pipeline


# -----------------------------------------------------------
# Function: load_models
# Purpose: Load placeholder models for UI testing
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
            st.code(traceback.format_exc())
            st.stop()

    # Input: bind to session state with a unique key
    sms_text = st.text_area(
        "Paste the SMS content",
        height=150,
        placeholder="e.g., Congratulations! You have won a prize. Click the link to claim...",
        key="sms_input",
    )

    # Example buttons to quickly fill the input
    st.caption("Quick examples:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📱 Lottery Scam"):
            st.session_state.sms_input = (
                "Congratulations! You've won a $1000 gift card. "
                "Click here to claim now: http://bit.ly/win-prize"
            )
    with col2:
        if st.button("🏦 Bank Scam"):
            st.session_state.sms_input = (
                "URGENT: Your account has been suspended. "
                "Verify your identity immediately at http://secure-bank-verify.com"
            )
    with col3:
        if st.button("📦 Delivery Scam"):
            st.session_state.sms_input = (
                "We tried to deliver your parcel but no one was home. "
                "Reschedule here: http://track-parcel.info"
            )

    # Analyze button
    if st.button("Start Analysis", type="primary"):
        print("=== Button clicked ===")
        print(f"Input text: {sms_text}")

        if not sms_text.strip():
            st.warning("⚠️ Please enter SMS content first.")
        else:
            try:
                with st.spinner("Analyzing..."):
                    print("Calling model...")
                    result = analyze_sms(
                        sms_text, binary_classifier, type_classifier
                    )
                    print(f"Result: {result}")

                # Display results (inside the button block)
                st.divider()
                st.subheader("📊 Analysis Result")

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

                if result["is_fraud"] and result["type_label"]:
                    st.subheader("🏷️ Scam Type")
                    st.info(
                        f"**{result['type_label']}** "
                        f"(confidence: {result['type_score']:.1%})"
                    )

                st.subheader("💡 Recommendations")
                st.markdown("""
                - Do not click any links in the message
                - Do not reply or share personal information
                - Verify through official channels
                - Report to your bank if you already responded
                """)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.code(traceback.format_exc())

    # Footer
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
