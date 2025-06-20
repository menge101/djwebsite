from invoke import Collection, Task, task
from typing import cast, Optional

from lib import toast, web


@task
def create(_c, table_name: str, session_id: str, message: str, level: Optional[str] = None) -> bool:
    c_thread = web.get_table_connection(table_name)
    toast.create(c_thread, session_id=session_id, message=message, level=level)
    print(f"Successfully created toast for session {session_id} with message {message}")
    return True


@task
def test(_c, table_name: str, session_id: str) -> bool:
    c_thread = web.get_table_connection(table_name)
    toast.create(c_thread, session_id=session_id, message="success", level="success")
    toast.create(c_thread, session_id=session_id, message="info", level="info")
    toast.create(c_thread, session_id=session_id, message="warning", level="warning")
    toast.create(c_thread, session_id=session_id, message="error", level="error")
    toast.create(c_thread, session_id=session_id, message="none")
    return True


toasts = Collection("toast")
toasts.add_task(cast(Task, create))
toasts.add_task(cast(Task, test))
