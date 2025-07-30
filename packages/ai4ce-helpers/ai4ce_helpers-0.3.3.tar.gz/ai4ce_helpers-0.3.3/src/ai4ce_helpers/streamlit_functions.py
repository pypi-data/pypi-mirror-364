from .functions import get_list_of_all_project_infos, get_recent_project
import streamlit as st
import warnings
from deprecated import deprecated

@deprecated(reason="This function is deprecated. Please use st_project_selector() instead.", category=DeprecationWarning)   
def load_project():
    warnings.warn("This function is deprecated. Please use st_project_selector() instead.", DeprecationWarning, stacklevel=2)
    return st_project_selector()

def st_project_selector():

    # first row with the project selector
    if 'project_name' not in st.session_state:
        st.session_state['project_name'] = "None Selected"
        st.session_state['project_id'] = None
        st.session_state["modified"] = None

    projects_simple_list = get_list_of_all_project_infos()

    col01, col02, col03, col04 = st.columns([5, 1, 2, 2])
    with col01:
        st.title("Load or Create a new CubeSat project")
        # st.title(
        #     f"Summary of the System Generation for {st.session_state['project_name']}")

    with col02:
        (st.session_state["project_id"],
             st.session_state["project_name"],
             st.session_state["modified"]) = get_recent_project()
        if st.button("Get recent project"):
            (st.session_state["project_id"],
             st.session_state["project_name"],
             st.session_state["modified"]) = get_recent_project()
    with col03:
        # Let the user select a project from the list of projects in the project DB
        selected_project = st.selectbox("Select a project",
                                        projects_simple_list,
                                        index=None,
                                        placeholder=st.session_state["project_name"])
        if selected_project is not None:
            st.session_state["project_id"] = selected_project[1]
            st.session_state["project_name"] = selected_project[2]
    with col04:
        st.metric(label=f"Active project ID: {st.session_state['project_id']}",
                  value=f"ID: {st.session_state['project_id']} - {st.session_state['project_name']}")
