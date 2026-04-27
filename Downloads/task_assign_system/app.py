import streamlit as st
import database as db
from datetime import datetime

st.set_page_config(layout="wide")
st.title(" Task Assignment System")

# ---------------- ROLE ----------------
role = st.selectbox("Select Role", ["Commander", "Member"])

# =====================================================
# 👤 SOLDIER VIEW
# =====================================================
if role == "Member":
    st.subheader("👤 Member Dashboard")

    name = st.text_input("Enter your name")

    if name:
        tasks = db.get_tasks()

        my_active = [t for t in tasks if t[4] == name and t[3] == "assigned"]
        my_completed = [t for t in tasks if t[4] == name and t[3] == "completed"]

        st.write(f"## 🪖 {name}")

        # Notification
        if my_active:
            st.warning(f"🔔 You have {len(my_active)} active tasks!")

        # Stats
        col1, col2 = st.columns(2)
        col1.metric("Active Tasks", len(my_active))
        col2.metric("Completed Tasks", len(my_completed))

        # Active Tasks
        st.subheader("🎯 Active Tasks")

        if my_active:
            for t in my_active:
                task_id, t_name, priority, status, assigned, start, end = t

                start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                duration = str(datetime.now() - start_time).split(".")[0]

                st.info(f"{t_name} ({priority})")
                st.write(f"⏱ Running Time: {duration}")

                if st.button(f"Complete {t_name}", key=task_id):
                    db.complete_task(task_id)
                    st.success("Task Completed")
                    st.rerun()
        else:
            st.write("No active tasks")

        # History
        st.subheader("📜 Task History")
        for t in my_completed:
            _, t_name, priority, status, assigned, start, end = t
            st.write(f"✅ {t_name} | {start} → {end}")

    st.stop()

# =====================================================
# 🪖 COMMANDER VIEW
# =====================================================

mode = st.radio("Assignment Mode", ["AUTO", "MANUAL"])

tasks = db.get_tasks()
members = db.get_members()

# ---------------- AUTO ASSIGN ----------------
def auto_assign():
    priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x[2], 3))

    for task in sorted_tasks:
        task_id, name, priority, status, assigned, start, end = task

        if status == "waiting":
            workload = {}
            for m in members:
                m_name = m[1]
                count = len([t for t in tasks if t[4] == m_name and t[3] == "assigned"])
                workload[m_name] = count

            if workload:
                best = min(workload, key=workload.get)
                db.assign_task(task_id, best)

if mode == "AUTO":
    auto_assign()

# ---------------- DASHBOARD ----------------
st.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Active", len([t for t in tasks if t[3] == "assigned"]))
col2.metric("Waiting", len([t for t in tasks if t[3] == "waiting"]))
col3.metric("Completed", len([t for t in tasks if t[3] == "completed"]))

# ---------------- ADD MEMBER ----------------
st.subheader("➕ Add Member")
name = st.text_input("Member Name")

if st.button("Add Member"):
    db.add_member(name)
    st.rerun()

# ---------------- ADD TASK ----------------
st.subheader("🎯 Create Task")
task_name = st.text_input("Task Name")
priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"])

if st.button("Add Task"):
    db.add_task(task_name, priority)
    st.rerun()

# ---------------- MANUAL ASSIGN ----------------
if mode == "MANUAL":
    st.subheader("🧠 Manual Assignment")

    waiting_tasks = [t for t in tasks if t[3] == "waiting"]
    soldier_names = [m[1] for m in members]

    if waiting_tasks:
        selected_tasks = st.multiselect(
            "Select Tasks",
            [f"{t[0]} - {t[1]}" for t in waiting_tasks]
        )

        selected_soldier = st.selectbox("Assign to", soldier_names)

        if st.button("Assign Tasks"):
            for item in selected_tasks:
                task_id = int(item.split(" - ")[0])
                db.assign_task(task_id, selected_soldier)

            st.success("Tasks assigned")
            st.rerun()

# ---------------- WORKLOAD ----------------
st.subheader("👥 Member Workload")

for m in members:
    m_name = m[1]

    active = [t for t in tasks if t[4] == m_name and t[3] == "assigned"]
    completed = [t for t in tasks if t[4] == m_name and t[3] == "completed"]

    st.markdown(f"### 🪖 {m_name}")
    st.write(f"Active: {len(active)} | Completed: {len(completed)}")

    for t in active:
        start = datetime.strptime(t[5], "%Y-%m-%d %H:%M:%S")
        duration = str(datetime.now() - start).split(".")[0]
        st.write(f"→ {t[1]} ({t[2]}) | ⏱ {duration}")

# ---------------- TASK SYSTEM ----------------
st.subheader("📋 Task Management")

tab1, tab2, tab3 = st.tabs(["⏳ Waiting", "⚙️ Active", "✅ Completed"])

with tab1:
    for t in tasks:
        if t[3] == "waiting":
            st.write(f"{t[1]} | {t[2]}")

with tab2:
    for t in tasks:
        if t[3] == "assigned":
            st.write(f"{t[1]} → {t[4]}")

with tab3:
    for t in tasks:
        if t[3] == "completed":
            st.write(f"{t[1]} ({t[5]} → {t[6]})")