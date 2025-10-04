import streamlit as st
import time
import re
import json
import os

# --- Load Data from JSON File ---
DATA_FILE = "data.json"

#@st.cache_resource
def load_data():
    """Loads the college data from the external JSON file."""
    if not os.path.exists(DATA_FILE):
        st.error(f"Data file '{DATA_FILE}' not found. Please create it with the provided JSON content.")
        return {}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from '{DATA_FILE}'. Please check the file format.")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred while loading data: {e}")
        return {}

DATA_STORE = load_data()

st.title("👨‍🎓 College Helpdesk Chatbot")
st.markdown("Ask me for **timetables**, **PYQs**, **faculty contacts**, or the **holiday list**!")

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Function to use the internal data store ---
def get_chatbot_response(user_input):
    """
    Processes user input and returns the relevant information from the DATA_STORE.
    """
    input_lower = user_input.lower()
    
    if not DATA_STORE:
        return "❌ Data is not available or failed to load. Please check `data.json`."

    # ---------------- Timetable ----------------
    if "timetable" in input_lower or "routine" in input_lower or "time table" in input_lower:
        timetable_link = DATA_STORE.get("timetables", {}).get("general_timetable_link")
        if timetable_link:
            return f"Here is the **General Timetable** link:\n- [College Timetable]({timetable_link})"
        return "Timetable data not available."

    # ---------------- PYQs ----------------
    elif "pyq" in input_lower or "past paper" in input_lower or "pyqs" in input_lower:
        
        # Access the PYQ list using the "DEPTPYQ" key
        pyqs_list = DATA_STORE.get("pyqs", {}).get("deptpyq",[])
        
        if not pyqs_list:
            return "Data is not available"

        # Extract specific years mentioned in the query
        years_requested = re.findall(r"\b(20\d{2})\b", input_lower)

        response_text = "Here are the Past Year Question Papers I found:\n"
        found_any = False

        # Sort the list by 'year' in reverse chronological order (newest first)
        try:
            sorted_pyqs = sorted(pyqs_list, key=lambda x: x.get("year", ""), reverse=True)
        except Exception:
            # Fallback in case of unexpected data structure
            sorted_pyqs = pyqs_list

        for item in sorted_pyqs:
            year = item.get("year")
            url = item.get("url")
            
            # Construct a descriptive title since your JSON lacks a 'title' field
            title = f"All Subjects PYQs of {year}" if year else "PYQ Link"

            if year and url:
                # Filter by requested years if specified in the user prompt
                if years_requested and year not in years_requested:
                    continue

                response_text += f"- [{title}]({url})\n"
                found_any = True

        if found_any:
            return response_text

        if years_requested:
            return f"No PYQs found for the requested year(s): {', '.join(years_requested)}."
        
        return "No PYQs found."


    # ---------------- Faculty ----------------
    elif "faculty" in input_lower or "contact" in input_lower or "staff" in input_lower:
        # Access the list using the "department_pages" key
        departments = DATA_STORE.get("faculty", {}).get("department_pages", [])
        
        if departments:
            # Check for specific department mention (e.g., "faculty of CSE")
            found_depts = [d for d in departments if d['department'].lower() in input_lower]
            
            response_text = ""
            if found_depts:
                # Provide links for specific departments
                response_text = "Here is the faculty info for the requested department(s):\n"
                for dept in found_depts:
                    response_text += f"- **{dept['department']}**: [Link]({dept['url']})\n"
            else:
                # Provide links for all departments if none were specified
                response_text = "Here are all department pages for faculty contacts. Please specify a department (e.g., CSE, ECE) for a direct link:\n"
                for dept in departments:
                    response_text += f"- **{dept['department']}**: [Link]({dept['url']})\n"
                    
            return response_text
        return "Faculty contact data not available."

    # ---------------- Holidays ----------------
    elif "holiday" in input_lower or "break" in input_lower:
        holidays_pdf = DATA_STORE.get("holidays", {}).get("yearly_list_pdf", "")
        if holidays_pdf:
            return f"Here is the **Yearly Holiday List** (PDF):\n- [Holiday List]({holidays_pdf})"
        return "Holiday list not available."

    # ---------------- Default ----------------
    else:
        return "I can help with: **timetables**, **PYQs**, **faculty contacts**, and **holidays**."


# --- Chat input and message handling ---
if prompt := st.chat_input("Ask a question about the college..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching data..."):
            time.sleep(0.5)
            response = get_chatbot_response(prompt)
            st.markdown(response)
            
        # Append assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})