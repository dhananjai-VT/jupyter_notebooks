subject_query = """WITH subjects AS (SELECT DISTINCT
         contacts.id AS Contact_ID
         ,scl.campaign_id as Adword_Campaign_ID
         ,scl.campaign_name AS Adword_Campaign
         ,scl.subject AS Adword_Subject
         ,scl.subject_type AS Adword_Subject_Type
         ,scl.location AS Adword_Location
         ,scl.ad_group_name AS Adword_Ad_Group_Name
         ,scl.ad_group_id AS Adword_Ad_Group_ID
         ,scl.account_id AS Adword_Account_ID
         ,subject_groups.subject_group AS Adword_Subject_Group
         FROM
         contacts
         LEFT JOIN lead_source ON (lead_source.lead_id=contacts.id)
         LEFT JOIN vtbid.subject_campaign_lookup scl ON (scl.ad_group_id=lead_source.ad_group_id)
         LEFT JOIN (SELECT DISTINCT
        ad_group_name
        ,subject_group
      FROM vtbid.adword_subject_groups) as subject_groups ON subject_groups.ad_group_name = scl.ad_group_name)
  ,  contact_lfs_callback AS (with todo_data as (
                            select parent_entity_id as contact_id,
                            todos.todo_time,
                            todo_type,
                            todos.id as todo_id,
                            row_number() over(partition by parent_entity_id order by todos.id asc) as first_todo_rank
                            from todos
                            where parent_entity_type = 'Contact'
                            and deleted_at is null
                            )

                select
                contacts.id as contact_id,
                contacts.created_at as contact_created_at,
                todo_data.todo_time,
                todo_data.todo_type,
                todo_data.first_todo_rank,
                todo_data.todo_id,
                case when todo_type=21 then 'LFS callback' else 'Regular' end as first_interaction_type,
                datediff(days, convert_timezone('UTC', 'America/Chicago', contacts.created_at), convert_timezone('UTC', 'America/Chicago', todo_time)) as days_delay,
                case when first_interaction_type = 'Regular' then 'A: Same Day (Regular lead)'
                   when first_interaction_type = 'LFS callback' and days_delay <1 then 'B: Same day (LFS callback)'
                   when first_interaction_type = 'LFS callback' and days_delay =1 then 'C: Next day (LFS callback)'
                   when first_interaction_type = 'LFS callback' and days_delay =2 then 'D: 2 days later (LFS callback)'
                   when first_interaction_type = 'LFS callback' and days_delay >2 then 'E: >2 days (LFS callback)'
                   else 'F: Other (LFS callback)' end as callback_when
                from contacts
                left join todo_data on contacts.id  = todo_data.contact_id and first_todo_rank=1
                order by contacts.id desc)
  ,  subject_campaign_lookup AS (SELECT scl.*,
                subject_groups.subject_group
         From vtbid.subject_campaign_lookup scl
         LEFT JOIN (SELECT DISTINCT
        ad_group_name
        ,subject_group
      FROM vtbid.adword_subject_groups) as subject_groups ON subject_groups.ad_group_name = scl.ad_group_name)
SELECT
	contacts.id  AS "contact_id",
	CONVERT_TIMEZONE('UTC', 'America/Chicago', contacts.created_at ) AS "contact_created_date",
	contact_lfs_callback.first_interaction_type  AS "first_interaction_type",
	subject_campaign_lookup.subject_group  AS "subject_group",
    contact_lfs_callback.todo_id as callback_todo_id,
	CASE WHEN (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) IN ('Tutor','Tutoring','tutor','Tutors') THEN 'Tutor'
              WHEN (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) IN ('Prep','prep') THEN 'Prep'
              WHEN (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) IN ('Class','class','Classes') THEN 'Class'
              WHEN (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) IN ('Course','course','Courses') THEN 'Course'
              WHEN (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) IN ('Lesson','lesson') THEN 'Lesson'
              WHEN (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) IN ('Material','Materials') THEN 'Material'
              WHEN (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) IN ('Program','Programs') THEN 'Program'
              ELSE (CASE WHEN subjects.adword_subject_type = 'tutor' THEN 'Tutor'
              WHEN subjects.adword_subject_type = 'class' THEN 'Class'
              WHEN subjects.adword_subject_type = 'course' THEN 'Course'
              WHEN subjects.adword_subject_type = 'lesson' THEN 'Lesson'
              WHEN subjects.adword_subject_type = 'prep' THEN 'Prep'
              ELSE subjects.adword_subject_type END) END AS "adword_subject_type_2",
	CONVERT_TIMEZONE('UTC', 'America/Chicago', contact_lfs_callback.todo_time) AS "callback_at_time",
	tags.name  AS "tags_name"
FROM contacts
LEFT JOIN subjects ON subjects.contact_id=contacts.id
LEFT JOIN public.clients  AS clients ON clients.id=contacts.client_id
LEFT JOIN public.b2b_instant_only_temp  AS b2b_instant_only_temp ON b2b_instant_only_temp.client_id=clients.id
LEFT JOIN contact_lfs_callback ON contact_lfs_callback.contact_id = contacts.id
LEFT JOIN public.taggings  AS taggings ON taggings.taggable_id=contacts.id
      AND taggings.taggable_type = 'Contact'
LEFT JOIN public.tags  AS tags ON tags.id=taggings.tag_id
LEFT JOIN subject_campaign_lookup ON subject_campaign_lookup.ad_group_id=(CASE
         WHEN contacts.page LIKE ('%adgroupid=%') THEN SPLIT_PART(SPLIT_PART(contacts.page,'adgroupid=',2),'&',1)
         ELSE NULL END)

WHERE (((CASE WHEN contacts.spam > 0 OR (CASE
         WHEN contacts.invalid_lead_reason=-1 THEN 'Valid Lead'
         WHEN contacts.invalid_lead_reason=1 THEN 'Spam'
         WHEN contacts.invalid_lead_reason=10 THEN 'Duplicate'
         WHEN contacts.invalid_lead_reason=20 THEN 'Current Client'
         WHEN contacts.invalid_lead_reason=30 THEN 'Current Lead'
         WHEN contacts.invalid_lead_reason=40 THEN 'Current Tutor'
         WHEN contacts.invalid_lead_reason=50 THEN 'Invalid Phone #'
        END
) = 'Spam' THEN 'Yes' ELSE 'No' END
) ILIKE 'No')
) AND ((CASE WHEN b2b_instant_only_temp.client_id IS NOT NULL THEN 'Yes' ELSE 'No' END) ILIKE 'No')
AND date(CONVERT_TIMEZONE('UTC','America/Chicago', contact_lfs_callback.todo_time)) = date(CONVERT_TIMEZONE('UTC', 'America/Chicago', getdate()))
AND contact_lfs_callback.first_interaction_type = 'LFS callback' 
AND tags.name in ('EW','GW main')
AND subject_campaign_lookup.subject_group in ({sub_list})
"""