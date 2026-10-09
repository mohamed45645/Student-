from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from storage import add_session, add_task, delete_task, get_summary, init_db, list_sessions, list_tasks, update_task

st.set_page_config(page_title="StudyFlow", page_icon="📚", layout="wide")
init_db()

WORDS = {
    "English": {
        "title": "StudyFlow", "subtitle": "A calm, practical workspace for planning study and seeing your progress.",
        "dashboard": "Overview", "tasks": "Study plan", "sessions": "Focus sessions", "settings": "About",
        "tasks_total": "Open tasks", "hours": "Study time (hours)", "completed": "Tasks completed", "streak": "Sessions this week",
        "add_task": "Add a study task", "subject": "Subject", "task": "Task", "due": "Due date", "priority": "Priority", "add": "Add task",
        "all_tasks": "Your plan", "status": "Status", "open": "Open", "doing": "In progress", "done": "Completed", "save": "Save status", "remove": "Delete task",
        "log": "Log a focus session", "minutes": "Minutes studied", "notes": "Notes (optional)", "save_session": "Save session", "recent": "Recent sessions",
        "weekly": "Study minutes by day", "by_subject": "Time by subject", "empty_tasks": "No tasks yet. Add one in the Study plan tab.", "empty_sessions": "No sessions logged yet.",
        "export": "Download your data", "data_note": "Your records are stored locally in a SQLite database. Keep a backup before moving or deleting the database file.",
        "urgent": "Overdue", "due_soon": "Due soon", "on_track": "On track", "no_subject": "Enter a subject", "delete_confirm": "Delete selected task? This cannot be undone.",
        "minutes_error": "Enter a duration between 1 and 600 minutes.", "project": "A local-first study planner built with Streamlit and SQLite.",
    },
    "العربية": {
        "title": "StudyFlow — مخطط المذاكرة", "subtitle": "مساحة بسيطة لتنظيم المذاكرة ومتابعة تقدمك.",
        "dashboard": "نظرة عامة", "tasks": "خطة المذاكرة", "sessions": "جلسات التركيز", "settings": "عن التطبيق",
        "tasks_total": "مهام مفتوحة", "hours": "وقت المذاكرة (ساعة)", "completed": "مهام مكتملة", "streak": "جلسات هذا الأسبوع",
        "add_task": "أضف مهمة مذاكرة", "subject": "المادة", "task": "المهمة", "due": "موعد التسليم", "priority": "الأولوية", "add": "إضافة المهمة",
        "all_tasks": "خطتك", "status": "الحالة", "open": "لم تبدأ", "doing": "قيد التنفيذ", "done": "مكتملة", "save": "حفظ الحالة", "remove": "حذف المهمة",
        "log": "سجّل جلسة تركيز", "minutes": "مدة المذاكرة بالدقائق", "notes": "ملاحظات (اختياري)", "save_session": "حفظ الجلسة", "recent": "أحدث الجلسات",
        "weekly": "دقائق المذاكرة خلال الأسبوع", "by_subject": "الوقت حسب المادة", "empty_tasks": "لا توجد مهام بعد. أضف مهمة من تبويب خطة المذاكرة.", "empty_sessions": "لم تسجل جلسات بعد.",
        "export": "تنزيل بياناتك", "data_note": "تُحفظ بياناتك محليًا في قاعدة SQLite. احتفظ بنسخة احتياطية قبل نقل ملف قاعدة البيانات أو حذفه.",
        "urgent": "متأخرة", "due_soon": "قريبة الموعد", "on_track": "على المسار", "no_subject": "اكتب اسم المادة", "delete_confirm": "حذف المهمة المحددة؟ لا يمكن التراجع عن ذلك.",
        "minutes_error": "أدخل مدة بين دقيقة و600 دقيقة.", "project": "مخطط مذاكرة محلي باستخدام Streamlit وSQLite.",
    },
}

with st.sidebar:
    lang = st.radio("Language / اللغة", ["English", "العربية"], horizontal=True)
    T = WORDS[lang]

st.markdown("""
<style>
.stApp{background:radial-gradient(ellipse at 15% 0%,#213756 0%,#101a2a 42%,#0a101a 100%);color:#eef3fb}
[data-testid="stSidebar"]{background:#0e1725;border-right:1px solid #27364b}
.block-container{max-width:1240px;padding-top:1.7rem}
.hero{padding:1.55rem 1.8rem;border:1px solid #30435c;border-radius:22px;background:linear-gradient(120deg,rgba(40,77,89,.78),rgba(17,28,44,.94));margin-bottom:1.1rem}
.hero h1{font-size:2.25rem;margin:0;letter-spacing:-.04em}.hero p{color:#b8c6d6;margin:.5rem 0 0}
[data-testid="stMetric"]{border:1px solid #2b3a50;border-radius:16px;padding:.9rem 1rem;background:rgba(17,28,44,.83)}
div[data-testid="stForm"]{border:1px solid #2a3a50;border-radius:16px;padding:1.1rem;background:rgba(17,28,44,.7)}
</style>
""", unsafe_allow_html=True)
if lang == "العربية":
    st.markdown("<style>.block-container{direction:rtl;text-align:right}</style>", unsafe_allow_html=True)

st.markdown(f'<div class="hero"><h1>📚 {T["title"]}</h1><p>{T["subtitle"]}</p></div>', unsafe_allow_html=True)

summary = get_summary()
a, b, c, d = st.columns(4)
a.metric(T["tasks_total"], summary["open_tasks"])
b.metric(T["hours"], f'{summary["total_minutes"] / 60:.1f}')
c.metric(T["completed"], summary["completed_tasks"])
d.metric(T["streak"], summary["week_sessions"])

tab_dash, tab_tasks, tab_sessions, tab_about = st.tabs([T["dashboard"], T["tasks"], T["sessions"], T["settings"]])

with tab_dash:
    left, right = st.columns(2)
    with left:
        st.subheader(T["weekly"])
        sessions = list_sessions(days=7)
        if sessions.empty:
            st.info(T["empty_sessions"])
        else:
            sessions["date"] = pd.to_datetime(sessions["created_at"]).dt.date
            by_day = sessions.groupby("date", as_index=False)["minutes"].sum()
            calendar = pd.DataFrame({"date": [date.today() - timedelta(days=i) for i in range(6, -1, -1)]})
            by_day = calendar.merge(by_day, on="date", how="left").fillna({"minutes": 0})
            fig = px.bar(by_day, x="date", y="minutes", color_discrete_sequence=["#54d6c8"])
            fig.update_layout(margin=dict(l=8, r=8, t=10, b=8), xaxis_title=None, yaxis_title="Minutes", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader(T["by_subject"])
        if sessions.empty:
            st.info(T["empty_sessions"])
        else:
            by_subject = sessions.groupby("subject", as_index=False)["minutes"].sum().sort_values("minutes", ascending=False)
            fig = px.pie(by_subject, names="subject", values="minutes", hole=.55, color_discrete_sequence=["#54d6c8", "#8396ff", "#f7bd70", "#f27f9a", "#82d694"])
            fig.update_layout(margin=dict(l=8, r=8, t=10, b=8), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    tasks = list_tasks()
    if not tasks.empty:
        st.subheader(T["all_tasks"])
        view = tasks[tasks["status"] != "Completed"].copy()
        view["deadline"] = pd.to_datetime(view["deadline"]).dt.date
        view["attention"] = view["deadline"].apply(lambda x: T["urgent"] if x < date.today() else (T["due_soon"] if x <= date.today()+timedelta(days=2) else T["on_track"]))
        st.dataframe(view[["subject", "title", "deadline", "priority", "status", "attention"]], use_container_width=True, hide_index=True)

with tab_tasks:
    with st.form("new_task", clear_on_submit=True):
        st.subheader(T["add_task"])
        x, y = st.columns(2)
        subject = x.text_input(T["subject"])
        title = y.text_input(T["task"])
        deadline = x.date_input(T["due"], value=date.today() + timedelta(days=7))
        priority = y.selectbox(T["priority"], ["High", "Medium", "Low"])
        submitted = st.form_submit_button(T["add"], type="primary", use_container_width=True)
    if submitted:
        if not subject.strip() or not title.strip():
            st.error(T["no_subject"])
        else:
            add_task(subject.strip(), title.strip(), deadline.isoformat(), priority)
            st.success(T["add"])
            st.rerun()
    tasks = list_tasks()
    st.subheader(T["all_tasks"])
    if tasks.empty:
        st.info(T["empty_tasks"])
    else:
        task_ids = tasks["id"].tolist()
        selected = st.selectbox("Task", task_ids, format_func=lambda i: f"{tasks.loc[tasks.id == i, 'subject'].iloc[0]} · {tasks.loc[tasks.id == i, 'title'].iloc[0]}")
        current = tasks.loc[tasks["id"] == selected].iloc[0]
        with st.form("edit_task"):
            chosen = st.selectbox(T["status"], [T["open"], T["doing"], T["done"]], index={"Open": 0, "In progress": 1, "Completed": 2}[current["status"]])
            save = st.form_submit_button(T["save"])
        if save:
            status_value = {T["open"]: "Open", T["doing"]: "In progress", T["done"]: "Completed"}[chosen]
            update_task(int(selected), status_value)
            st.rerun()
        if st.button(T["remove"], type="secondary"):
            st.session_state["confirm_delete"] = True
        if st.session_state.get("confirm_delete"):
            st.warning(T["delete_confirm"])
            confirm_col, cancel_col = st.columns(2)
            if confirm_col.button("Confirm / تأكيد", type="primary"):
                delete_task(int(selected))
                st.session_state["confirm_delete"] = False
                st.rerun()
            if cancel_col.button("Cancel / إلغاء"):
                st.session_state["confirm_delete"] = False
                st.rerun()
        st.dataframe(tasks.drop(columns=["id"]), use_container_width=True, hide_index=True)

with tab_sessions:
    st.subheader(T["log"])
    with st.form("session_form", clear_on_submit=True):
        subject = st.text_input(T["subject"])
        minutes = st.number_input(T["minutes"], min_value=1, max_value=600, value=25, step=5)
        notes = st.text_area(T["notes"], max_chars=500)
        logged = st.form_submit_button(T["save_session"], type="primary", use_container_width=True)
    if logged:
        if not subject.strip():
            st.error(T["no_subject"])
        elif not 1 <= minutes <= 600:
            st.error(T["minutes_error"])
        else:
            add_session(subject.strip(), int(minutes), notes.strip())
            st.success(T["save_session"])
            st.rerun()
    st.subheader(T["recent"])
    sessions = list_sessions(limit=100)
    if sessions.empty:
        st.info(T["empty_sessions"])
    else:
        st.dataframe(sessions[["created_at", "subject", "minutes", "notes"]], use_container_width=True, hide_index=True)

with tab_about:
    st.subheader(T["export"])
    tasks = list_tasks()
    sessions = list_sessions(days=None, limit=100000)
    col1, col2 = st.columns(2)
    col1.download_button("Tasks CSV", tasks.drop(columns=["id"], errors="ignore").to_csv(index=False).encode("utf-8"), "studyflow_tasks.csv", "text/csv")
    col2.download_button("Sessions CSV", sessions.drop(columns=["id"], errors="ignore").to_csv(index=False).encode("utf-8"), "studyflow_sessions.csv", "text/csv")
    st.info(T["data_note"])
    st.caption(T["project"])
