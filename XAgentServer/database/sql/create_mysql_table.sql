CREATE TABLE
IF
	NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键',
		user_id VARCHAR ( 32 ) UNIQUE NOT NULL COMMENT '用户ID',
		email VARCHAR ( 255 ) UNIQUE NOT NULL COMMENT '邮箱',
		NAME VARCHAR ( 255 ) COMMENT '姓名',
		token VARCHAR ( 255 ) COMMENT '令牌',
		available BOOLEAN DEFAULT TRUE COMMENT '是否可用',
		corporation TEXT COMMENT '公司',
		industry TEXT COMMENT '行业',
		position VARCHAR ( 255 ) COMMENT '职位',
		create_time VARCHAR ( 255 ) COMMENT '创建时间',
		update_time VARCHAR ( 255 ) COMMENT '更新时间' 
	);
CREATE TABLE
IF
	NOT EXISTS interactions (
		id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键',
		interaction_id VARCHAR ( 32 ) NOT NULL COMMENT '对话ID',
		user_id VARCHAR ( 32 ) NOT NULL COMMENT '用户ID',
		create_time VARCHAR ( 255 ) COMMENT '创建时间',
		update_time VARCHAR ( 255 ) COMMENT '更新时间',
		description VARCHAR ( 255 ) COMMENT '描述',
		agent VARCHAR ( 255 ) COMMENT '代理',
		MODE VARCHAR ( 255 ) COMMENT '模式',
		recorder_root_dir TEXT COMMENT '录音根目录',
		file_list JSON COMMENT '文件列表',
		STATUS VARCHAR ( 255 ) COMMENT '状态',
		message TEXT COMMENT '消息',
		current_step VARCHAR ( 255 ) COMMENT '当前步骤',
		is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除' 
	);
CREATE TABLE
IF
	NOT EXISTS interaction_parameters (
		id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL COMMENT '主键',
		interaction_id VARCHAR ( 255 ) NOT NULL COMMENT '对话ID',
		parameter_id VARCHAR ( 255 ) NOT NULL COMMENT '参数ID',
		args JSON COMMENT '参数' 
	);
CREATE TABLE
IF
	NOT EXISTS shared_interactions (
		id INT ( 11 ) NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
		interaction_id VARCHAR ( 255 ) NOT NULL COMMENT '交互ID',
		user_name VARCHAR ( 255 ) NOT NULL COMMENT '用户名',
		create_time VARCHAR ( 255 ) NOT NULL COMMENT '创建时间',
		update_time VARCHAR ( 255 ) NOT NULL COMMENT '更新时间',
		description VARCHAR ( 255 ) NOT NULL COMMENT '描述',
		agent VARCHAR ( 255 ) NOT NULL COMMENT 'agent',
		MODE VARCHAR ( 255 ) NOT NULL COMMENT '模式',
		is_deleted TINYINT ( 1 ) NOT NULL DEFAULT '0' COMMENT '是否删除',
	star INT ( 11 ) NOT NULL DEFAULT '0' COMMENT '星级' 
	) ENGINE = INNODB DEFAULT CHARSET = utf8mb4;