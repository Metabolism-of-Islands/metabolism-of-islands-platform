# Renaming to be done right after the first wave of migrations; those in 0001_initial
new = [
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "auth_user",
    "auth_user_groups",
    "auth_user_user_permissions",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_session",
    "geography_columns",
    "geometry_columns",
    "main_activatedspace",
    "main_document",
    "main_emailquota",
    "main_libraryitem",
    "main_libraryitem_saved_by_users",
    "main_libraryitemtype",
    "main_license",
    "main_news",
    "main_optamosalternative",
    "main_optamosalternativevalue",
    "main_optamoscriteria",
    "main_optamoscriteriavalue",
    "main_optamosproject",
    "main_optamostag",
    "main_optamosuser",
    "main_people",
    "main_photo",
    "main_record",
    "main_record_spaces",
    "main_record_subscribers",
    "main_record_tags",
    "main_recordrelationship",
    "main_relationship",
    "main_tag",
    "main_video",
    "main_webpage",
    "main_zoterocollection",
    "main_zoteroitem",
    "spatial_ref_sys",
    "stafdb_referencespace ",

    "main_publicproject",
]

keep = [
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "auth_user",
    "auth_user_groups",
    "auth_user_user_permissions",
    "django_admin_log",
    "django_content_type",
    "django_cron_cronjoblock",
    "django_cron_cronjoblog",
    "django_migrations",
    "django_session",
    "django_site",
    "geography_columns",
    "geometry_columns",
    "spatial_ref_sys",
    "stafdb_referencespace",
]

old = [
    "core_activatedspace",
    "core_badge",
    "core_badge_projects",
    "core_badge_worktype",
    "core_blog",
    "core_chat",
    "core_course",
    "core_course_projects",
    "core_coursecontent",
    "core_coursemodule",
    "core_coursequestion",
    "core_coursequestionanswer",
    "core_dataarticle",
    "core_dataviz",
    "core_document",
    "core_emailquota",
    "core_event",
    "core_event_projects",
    "core_forumtopic",
    "core_language",
    "core_libraryitem",
    "core_libraryitem_geocodes",
    "core_libraryitem_saved_by_users",
    "core_libraryitemtype",
    "core_license",
    "core_message",
    "core_news",
    "core_news_projects",
    "core_notification",
    "core_optamosalternative",
    "core_optamosalternativevalue",
    "core_optamoscriteria",
    "core_optamoscriteriavalue",
    "core_optamosproject",
    "core_optamostag",
    "core_optamosuser",
    "core_organization",
    "core_people",
    "core_people_badges",
    "core_photo",
    "core_project",
    "core_projectdesign",
    "core_projecttype",
    "core_publicproject",
    "core_record",
    "core_record_materials",
    "core_record_sectors",
    "core_record_spaces",
    "core_record_subscribers",
    "core_record_tags",
    "core_recordhistory",
    "core_recordrelationship",
    "core_relationship",
    "core_tag",
    "core_unit",
    "core_video",
    "core_webpage",
    "core_webpagedesign",
    "core_work",
    "core_workactivity",
    "core_workcategory",
    "core_worksprint",
    "core_worksprint_projects",
    "core_zoterocollection",
    "core_zoteroitem",
]

stafdb = [
    "stafdb_activity",
    "stafdb_activitycatalog",
    "stafdb_data",
    "stafdb_flowblocks",
    "stafdb_flowdiagram",
    "stafdb_geocode",
    "stafdb_geocode_scheme",
    "stafdb_material",
    "stafdb_materialcatalog",
    #"stafdb_referencespace",
    "stafdb_referencespace_geocode",
    "stafdb_sector",
    "stafdb_sector_activities",
]

for each in stafdb:
    print(f"DROP TABLE {each} CASCADE;")

for each in old:
    s = each.split("_", 1)[1]
    s = f"main_{s}"
    if not s in new:
        print(f"DROP TABLE {each} CASCADE;")

print("BEGIN;")
for each in old:
    s = each.split("_",1)[1]
    s = f"main_{s}"
    if s in new:
        print(f"ALTER TABLE {each} RENAME TO {s};")
#print("ALTER TABLE main_activatedspace RENAME TO main_island;")
print("COMMIT;")
print('UPDATE "main_record_spaces" SET "referencespace_id" = \'328874\' WHERE "referencespace_id" = \'16513\';')
print('ALTER TABLE "main_record_spaces" DROP CONSTRAINT "core_record_spaces_referencespace_id_07795752_fk_stafdb_re";')
print('ALTER TABLE "main_record_spaces" ADD FOREIGN KEY ("referencespace_id") REFERENCES "stafdb_referencespace" ("record_ptr_id") ON DELETE CASCADE ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;')
