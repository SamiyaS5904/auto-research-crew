import streamlit as st

from crew import run

st.set_page_config(page_title="Auto Research Crew")
st.title("Auto Research Crew")
st.caption("Every figure sourced, nothing invented.")
st.write(
    "Answers vehicle questions from live web search. Every figure is shown with the "
    "source it came from, and anything the search could not find is said so."
)

question = st.text_input(
    "Vehicle question",
    placeholder="Compare the Tata Nexon and Maruti Brezza on price and mileage",
)

if st.button("Ask", disabled=not question.strip()):
    with st.spinner("Searching, reconciling, writing"):
        result = run(question)

    st.subheader("Answer")
    st.text(result.raw)

    # Only two names, so zip drops the writer's output: it is the answer shown above.
    for name, task in zip(["Sources found", "Reconciled figures"], result.tasks_output):
        with st.expander(name):
            st.text(task.raw)
