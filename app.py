import streamlit as st
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))
from run_pipeline import run_pipeline

st.set_page_config(page_title="App Compiler", page_icon="🤖", layout="wide")

st.title("🤖 App Compiler")
st.markdown("*Natural language → Full app specification*")
st.divider()

user_prompt = st.text_area(
    "Describe the app you want to build:",
    placeholder="e.g. Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    height=120
)

if st.button("🚀 Generate App Specification", type="primary"):
    if not user_prompt.strip():
        st.error("Please enter a prompt first.")
    else:
        with st.spinner("Running pipeline... this takes ~30 seconds"):
            try:
                result = run_pipeline(user_prompt)
                st.success("✅ Pipeline complete!")

                # Validation summary
                validation = result["final_schemas"].get("_validation", {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Issues Found", validation.get("repair_count", 0))
                with col2:
                    st.metric("Auto-Repaired", "Yes" if validation.get("repaired") else "No")
                with col3:
                    st.metric("Status", "✅ Valid")

                if validation.get("issues_found"):
                    with st.expander("⚠️ Issues detected and repaired"):
                        for issue in validation["issues_found"]:
                            st.write(f"- {issue}")

                st.divider()

                # Show each schema in its own tab
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🎯 Intent", "🏗️ System Design", "🗄️ Database", "🔌 API", "🖥️ UI & Auth"
                ])

                with tab1:
                    st.subheader("Extracted Intent")
                    st.json(result["intent"])

                with tab2:
                    st.subheader("System Design")
                    st.json(result["design"])

                with tab3:
                    st.subheader("Database Schema")
                    st.json(result["final_schemas"].get("db_schema", {}))

                with tab4:
                    st.subheader("API Schema")
                    st.json(result["final_schemas"].get("api_schema", {}))

                with tab5:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("UI Schema")
                        st.json(result["final_schemas"].get("ui_schema", {}))
                    with col2:
                        st.subheader("Auth Rules")
                        st.json(result["final_schemas"].get("auth_rules", {}))

                # Download button
                st.divider()
                st.download_button(
                    label="⬇️ Download Full Specification (JSON)",
                    data=json.dumps(result, indent=2),
                    file_name="app_specification.json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"Pipeline failed: {str(e)}")
                st.exception(e)