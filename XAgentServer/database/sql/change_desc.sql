-- changed the description field in the database from Varchar(255) to Text
alter table shared_interactions modify `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'description / 描述';
alter table interactions modify `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'description / 描述';
