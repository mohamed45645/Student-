import storage


def test_tasks_and_study_sessions_are_persisted(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "studyflow.sqlite")
    storage.init_db()

    task_id = storage.add_task("Math", "Review derivatives", "2030-06-10", "High")
    storage.update_task(task_id, "In progress")
    task = storage.list_tasks().iloc[0]
    assert task["title"] == "Review derivatives"
    assert task["status"] == "In progress"

    storage.add_session("Math", 30, "Practice problems")
    summary = storage.get_summary()
    assert summary["open_tasks"] == 1
    assert summary["completed_tasks"] == 0
    assert summary["total_minutes"] == 30
    assert summary["week_sessions"] == 1

    storage.update_task(task_id, "Completed")
    assert storage.get_summary()["completed_tasks"] == 1
    storage.delete_task(task_id)
    assert storage.list_tasks().empty


def test_session_duration_is_validated(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "studyflow.sqlite")
    storage.init_db()
    try:
        storage.add_session("Physics", 0)
    except ValueError as exc:
        assert "between 1 and 600" in str(exc)
    else:
        raise AssertionError("Invalid duration should be rejected")
