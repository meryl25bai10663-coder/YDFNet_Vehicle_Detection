"""EmergeRoute Privacy Policy."""
import streamlit as st

st.set_page_config(page_title="Privacy Policy | EmergeRoute", page_icon="assets/emerge_route_favicon.svg", layout="wide")

st.title("Privacy Policy")
st.caption("EmergeRoute")

st.header("1. Scope")
st.write("This page describes how information is handled by the EmergeRoute application in its current project form. The application is a traffic analysis and simulation tool.")

st.header("2. Uploaded files")
st.write("Traffic videos or other files uploaded to the application are processed by the existing vehicle-detection pipeline. Do not upload personal, confidential, or sensitive material unless you are authorized to do so.")

st.header("3. Traffic and simulation data")
st.write("Traffic scenario logs, simulation outputs, and model inputs used by EmergeRoute are project data used to perform analysis. They may contain technical information about simulated networks and traffic conditions.")

st.header("4. Third-party services")
st.write("The application may use external mapping or data services where those services are part of the configured project pipeline. Their own privacy policies and terms may apply.")

st.header("5. Data retention")
st.write("Retention depends on how the application is deployed and where uploaded files and generated outputs are stored. The repository itself should not be treated as a location for private user data or secrets.")

st.header("6. Contact")
st.write("For questions about the deployment or handling of project data, contact the project owner or deployment administrator.")

st.caption("Last updated: October 2026")
