upcoming_appointments_today = """select id as preassigned_todo_id, 
convert_timezone('UTC','America/Chicago', todo_time) as "interval", 
assigned_to_user_id as user_id
from todos 
where date(convert_timezone('UTC','America/Chicago', todo_time)) = date(getdate())
and completed_at is null 
and deleted_at is null
and assigned_to_user_id is not null
and todo_type=21"""