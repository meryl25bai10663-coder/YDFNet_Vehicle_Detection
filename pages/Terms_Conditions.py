"""EmergeRoute Terms and Conditions."""
import streamlit as st

st.set_page_config(page_title="Terms & Conditions | EmergeRoute", page_icon="assets/emerge_route_favicon.svg", layout="wide")

st.title("Terms & Conditions")
st.caption("EmergeRoute")

st.header("1. Purpose")
st.write("EmergeRoute is provided as a traffic analysis, simulation, and decision-support application. It is not a system for automatically controlling real-world traffic infrastructure.")

st.header("2. Decision support only")
st.write("Simulation results, predictions, rankings, and recommendations are analytical outputs. They should be reviewed by a qualified operator before any real-world operational decision is made.")

st.header("3. Uploaded content")
st.write("You are responsible for ensuring that you have the necessary rights and authorization to upload videos, datasets, maps, or other material to the application.")

st.header("4. Accuracy and availability")
st.write("The application depends on its configured models, simulation environment, datasets, mapping services, and runtime environment. Results can therefore vary and are not guaranteed to be complete, accurate, or suitable for a particular operational decision.")

st.header("5. Third-party services")
st.write("External services used by a deployment may have separate terms, limitations, and availability requirements. Those terms apply when the relevant service is used.")

st.header("6. Responsible use")
st.write("Do not use the application to make unsafe, unlawful, discriminatory, or otherwise harmful decisions. Protect credentials, private datasets, and deployment infrastructure appropriately.")

st.header("7. Changes")
st.write("These terms may be updated when the application, deployment, or applicable requirements change.")

st.caption("Last updated: October 2026")
