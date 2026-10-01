
import streamlit as st
import json
import csv
import io

from extractor import (
    extract_action_items,
    generate_summary,
    extract_key_decisions
)


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="AI Meeting Action-Item Extractor",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🤖 AI Meeting Action-Item Extractor")

st.write(
    "Upload a meeting transcript and let the AI identify "
    "action items, owners, deadlines, priorities, and more."
)

st.divider()


# =========================================================
# UPLOAD TRANSCRIPT
# =========================================================

st.subheader("📄 Upload Meeting Transcript")

uploaded_file = st.file_uploader(
    "Choose a transcript file",
    type=["txt"]
)


if uploaded_file is not None:

    transcript = uploaded_file.read().decode("utf-8")

    st.subheader("📖 Meeting Transcript")

    st.text_area(
        "Transcript",
        transcript,
        height=300
    )

    st.divider()

    if st.button("🚀 Extract Meeting Information"):

        action_items = extract_action_items(transcript)

        summary = generate_summary(transcript)

        decisions = extract_key_decisions(transcript)

        st.session_state["action_items"] = action_items
        st.session_state["summary"] = summary
        st.session_state["decisions"] = decisions


# =========================================================
# RESULTS
# =========================================================

if "action_items" in st.session_state:

    action_items = st.session_state["action_items"]

    summary = st.session_state["summary"]

    decisions = st.session_state["decisions"]


    # =====================================================
    # DASHBOARD METRICS
    # =====================================================

    total_tasks = len(action_items)

    high_priority = sum(
        1
        for item in action_items
        if item["priority"] == "High"
    )

    completed_tasks = sum(
        1
        for item in action_items
        if item["status"] == "Completed"
    )

    missing_owners = sum(
        1
        for item in action_items
        if item["missing_owner"]
    )

    missing_deadlines = sum(
        1
        for item in action_items
        if item["missing_deadline"]
    )

    duplicate_tasks = sum(
        1
        for item in action_items
        if item["duplicate"]
    )

    if total_tasks > 0:

        average_confidence = round(
            sum(
                item["confidence"]
                for item in action_items
            ) / total_tasks
        )

    else:

        average_confidence = 0


    st.subheader("📊 Meeting Dashboard")


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Total Tasks",
            total_tasks
        )


    with col2:

        st.metric(
            "High Priority",
            high_priority
        )


    with col3:

        st.metric(
            "Completed",
            completed_tasks
        )


    with col4:

        st.metric(
            "Avg Confidence",
            f"{average_confidence}%"
        )


    col5, col6, col7 = st.columns(3)


    with col5:

        st.metric(
            "Missing Owner",
            missing_owners
        )


    with col6:

        st.metric(
            "Missing Deadline",
            missing_deadlines
        )


    with col7:

        st.metric(
            "Duplicate Tasks",
            duplicate_tasks
        )


    st.divider()


    # =====================================================
    # MEETING SUMMARY
    # =====================================================

    st.subheader("📝 Meeting Summary")

    st.write(summary)

    st.divider()


    # =====================================================
    # KEY DECISIONS
    # =====================================================

    st.subheader("✅ Key Decisions")


    if len(decisions) > 0:

        for decision in decisions:

            st.write("• " + decision)

    else:

        st.write("No key decisions detected.")


    st.divider()


    # =====================================================
    # SPEAKER-WISE TASKS
    # =====================================================

    st.subheader("👥 Speaker-wise Tasks")

    speaker_tasks = {}


    for item in action_items:

        owner = item["owner"]


        if owner not in speaker_tasks:

            speaker_tasks[owner] = []


        speaker_tasks[owner].append(
            item["task"]
        )


    if len(speaker_tasks) > 0:

        for speaker, tasks in speaker_tasks.items():

            st.write("### 👤 " + speaker)


            for task in tasks:

                st.write("• " + task)

    else:

        st.write("No speaker-wise tasks found.")


    st.divider()


    # =====================================================
    # SEARCH AND FILTER
    # =====================================================

    st.subheader("🔎 Search & Filter Tasks")


    search_text = st.text_input(
        "Search tasks",
        placeholder="Example: website, content, testing..."
    )


    # OWNER FILTER

    owners = ["All"]


    for item in action_items:

        if item["owner"] not in owners:

            owners.append(
                item["owner"]
            )


    selected_owner = st.selectbox(
        "Filter by Owner",
        owners
    )


    # PRIORITY FILTER

    selected_priority = st.selectbox(
        "Filter by Priority",
        [
            "All",
            "High",
            "Medium"
        ]
    )


    # STATUS FILTER

    selected_status = st.selectbox(
        "Filter by Status",
        [
            "All",
            "Pending",
            "Completed"
        ]
    )


    # =====================================================
    # APPLY FILTERS
    # =====================================================

    filtered_items = []


    for index, item in enumerate(action_items):

        matches_search = (
            search_text.lower()
            in item["task"].lower()
        )


        matches_owner = (
            selected_owner == "All"
            or item["owner"] == selected_owner
        )


        matches_priority = (
            selected_priority == "All"
            or item["priority"] == selected_priority
        )


        matches_status = (
            selected_status == "All"
            or item["status"] == selected_status
        )


        if (
            matches_search
            and matches_owner
            and matches_priority
            and matches_status
        ):

            filtered_items.append(
                (index, item)
            )


    st.write(
        f"Showing {len(filtered_items)} "
        f"of {len(action_items)} tasks"
    )


    st.divider()


    # =====================================================
    # EDIT AND MANAGE TASKS
    # =====================================================

    st.subheader("✏️ Edit & Manage Tasks")


    if len(filtered_items) > 0:

        for index, item in filtered_items:

            st.write(
                "### Task " + str(index + 1)
            )


            # TASK

            edited_task = st.text_input(
                "Task",
                value=item["task"],
                key=f"task_{index}"
            )


            # OWNER

            edited_owner = st.text_input(
                "Owner",
                value=item["owner"],
                key=f"owner_{index}"
            )


            # DEADLINE

            edited_deadline = st.text_input(
                "Deadline",
                value=item["deadline"],
                key=f"deadline_{index}"
            )


            # PRIORITY

            edited_priority = st.selectbox(
                "Priority",
                [
                    "High",
                    "Medium"
                ],
                index=(
                    0
                    if item["priority"] == "High"
                    else 1
                ),
                key=f"priority_{index}"
            )


            # STATUS

            completed = st.checkbox(
                "✅ Mark task as completed",
                value=(
                    item["status"] == "Completed"
                ),
                key=f"completed_{index}"
            )


            if completed:

                edited_status = "Completed"

            else:

                edited_status = "Pending"


            # SAVE

            if st.button(
                "💾 Save Changes",
                key=f"save_{index}"
            ):

                action_items[index]["task"] = (
                    edited_task
                )

                action_items[index]["owner"] = (
                    edited_owner
                )

                action_items[index]["deadline"] = (
                    edited_deadline
                )

                action_items[index]["priority"] = (
                    edited_priority
                )

                action_items[index]["status"] = (
                    edited_status
                )


                # MISSING OWNER

                if edited_owner == "Not Assigned":

                    action_items[index][
                        "missing_owner"
                    ] = True

                else:

                    action_items[index][
                        "missing_owner"
                    ] = False


                # MISSING DEADLINE

                if edited_deadline == "Not specified":

                    action_items[index][
                        "missing_deadline"
                    ] = True

                else:

                    action_items[index][
                        "missing_deadline"
                    ] = False


                st.session_state[
                    "action_items"
                ] = action_items


                st.success(
                    "Task updated successfully!"
                )


                st.rerun()


            st.divider()


    else:

        st.warning(
            "No tasks match your search/filter."
        )


    # =====================================================
    # DOWNLOAD RESULTS
    # =====================================================

    st.subheader("📥 Download Results")


    # -----------------------------------------------------
    # CSV
    # -----------------------------------------------------

    output = io.StringIO()


    if len(action_items) > 0:

        fieldnames = action_items[0].keys()


        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames
        )


        writer.writeheader()

        writer.writerows(action_items)


    csv_file = output.getvalue()


    st.download_button(
        label="📊 Download CSV",
        data=csv_file,
        file_name="meeting_action_items.csv",
        mime="text/csv"
    )


    # -----------------------------------------------------
    # JSON
    # -----------------------------------------------------

    json_file = json.dumps(
        action_items,
        indent=4
    )


    st.download_button(
        label="📄 Download JSON",
        data=json_file,
        file_name="meeting_action_items.json",
        mime="application/json"
    )