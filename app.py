from azure_agent_worker import run_agent
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Feedback Analyzer", layout="wide")
st.title("Feedback Analyzer with Azure Foundry Agent")

st.sidebar.header("Azure Agent Configuration")
agent_id_input = st.sidebar.text_input("AGENT_ID", value="")
project_endpoint_input = st.sidebar.text_input("PROJECT_ENDPOINT", value="")
st.sidebar.markdown("If you prefer, set `AGENT_ID` and `PROJECT_ENDPOINT` as environment variables instead.")

uploaded_file = st.file_uploader("Upload your feedback CSV", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a CSV file from Microsoft Forms to start.")
else:
    try:
        df = pd.read_csv(uploaded_file, encoding="windows-1252", sep=";")
    except Exception as e:
        st.error(f"Failed to parse CSV: {e}")
        st.stop()

    st.write("Preview of uploaded data (first 5 rows):")
    st.dataframe(df.head())

    # Column selector
    cols = list(df.columns)
    if not cols:
        st.error("No columns found in the uploaded CSV.")
        st.stop()

    selected_col = st.selectbox("Select column with feedback text", cols)

    run_button = st.button("Send to model")

    if run_button:
        try:
            texts = df[selected_col].dropna().astype(str).tolist()
            if len(texts) == 0:
                st.error("Selected column is empty. Choose another column with text values.")
                st.stop()
        except Exception as e:
            st.error(f"Failed to extract column data: {e}")
            st.stop()

        # Use sidebar values if provided, otherwise rely on environment variables
        agent_id = agent_id_input.strip() or None
        project_endpoint = project_endpoint_input.strip() or None

        with st.spinner("Sending data to the model and waiting for response..."):
            try:
                result = run_agent(texts, agent_id=agent_id, project_endpoint=project_endpoint)
                st.success("Model returned a response:")
                st.code(result, "markdown", wrap_lines=True)
            except Exception as e:
                st.error(e)


st.sidebar.markdown("---")
st.sidebar.markdown("Quick run: `python -m streamlit run app.py`")
