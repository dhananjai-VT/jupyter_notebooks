schedule_query = """SELECT
	employee_directory.mgr_name  AS "mgr_name",
	employee_directory.sub_group  AS "sub_group",
	employee_directory.supervisor  AS "rd",
	employee_directory.mgr_id  AS "mgr_id",
    users.id as user_id,
	CONVERT_TIMEZONE('UTC', 'America/Chicago', gpc_wfm_schedules.schedule_start ) AS "schedule_start_time",
	CONVERT_TIMEZONE('UTC', 'America/Chicago', gpc_wfm_schedules.schedule_end ) AS "schedule_end_time"
FROM  genesys.wfm2_schedules  AS gpc_wfm_schedules
LEFT JOIN genesys.wfm2_activity_codes  AS gpc_wfm_activity_codes ON gpc_wfm_schedules.activity_code_id = gpc_wfm_activity_codes.id
        AND (TRIM(gpc_wfm_schedules.business_unit_id)) = gpc_wfm_activity_codes.business_unit_id
LEFT JOIN public.employee_directory  AS employee_directory ON employee_directory.mgr_id=gpc_wfm_schedules.manager_id
      AND TO_DATE((DATE(employee_directory.updated_at )),'YYYY-MM')=TO_DATE((DATE(CONVERT_TIMEZONE('UTC', 'America/Chicago', gpc_wfm_schedules.schedule_start ))),'YYYY-MM')
LEFT JOIN users on users.manager_id = employee_directory.mgr_id
WHERE date(CONVERT_TIMEZONE('UTC', 'America/Chicago', gpc_wfm_schedules.schedule_start)) = date(GETDATE())
AND TRIM(gpc_wfm_activity_codes.category) = 'OnQueueWork'
and employee_directory.work_group in ('EW','GW main','SEC','Learning Differences')
AND employee_directory.mgr_name  IN ({rep_list})
order by 1 desc,5 desc"""