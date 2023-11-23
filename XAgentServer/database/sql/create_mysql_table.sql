/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80028
 Source Host           : localhost
 Source Schema         : xagent-dev

 Target Server Type    : MySQL
 Target Server Version : 80028
 File Encoding         : 65001

 Date: 17/11/2023 10:54:36
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP DATABASE IF EXISTS `xagent`;
CREATE DATABASE IF NOT EXISTS `xagent`;

USE `xagent`;

-- ----------------------------
-- Table structure for interaction_parameters
-- ----------------------------
DROP TABLE IF EXISTS `interaction_parameters`;
CREATE TABLE `interaction_parameters`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `interaction_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '对话ID',
  `parameter_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '参数ID',
  `args` json NULL COMMENT '参数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 480 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for interactions
-- ----------------------------
DROP TABLE IF EXISTS `interactions`;
CREATE TABLE `interactions`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `interaction_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '对话ID',
  `user_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户ID',
  `create_time` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '更新时间',
  `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '描述',
  `agent` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '代理',
  `mode` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '模式',
  `recorder_root_dir` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '录音根目录',
  `file_list` json NULL COMMENT '文件列表',
  `status` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '状态',
  `message` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '消息',
  `current_step` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '当前步骤',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '是否删除',
  `call_method` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT 'web' COMMENT '调用方式：web: 页面， command: 命令行， recorder: recorder',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 468 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for raw
-- ----------------------------
DROP TABLE IF EXISTS `raw`;
CREATE TABLE `raw`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `node_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '节点id',
  `interaction_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '交互id',
  `current` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '当前节点',
  `step` int NULL DEFAULT 0 COMMENT '步骤',
  `data` json NULL COMMENT '数据',
  `file_list` json NULL COMMENT 'workspace文件列表',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'running' COMMENT '状态',
  `do_interrupt` tinyint(1) NULL DEFAULT 0 COMMENT '是否中断',
  `wait_seconds` int NULL DEFAULT 0 COMMENT '已等待时间',
  `ask_for_human_help` tinyint(1) NULL DEFAULT 0 COMMENT '是否需要人工干预',
  `create_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '更新时间',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '是否删除',
  `is_human` tinyint(1) NULL DEFAULT 0 COMMENT '是否人工已经输入',
  `human_data` json NULL COMMENT '人工输入数据',
  `human_file_list` json NULL COMMENT '人工文件列表',
  `is_send` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否推送前端消息, 0:未推送, 1:已推送',
  `is_receive` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否接收前端消息, 0:未接收, 1:已接收',
  `include_pictures` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否包含png',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `node_id`(`node_id` ASC) USING BTREE,
  INDEX `interaction_id`(`interaction_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1784 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '交互过程' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for running_record
-- ----------------------------
DROP TABLE IF EXISTS `running_record`;
CREATE TABLE `running_record`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `record_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `current` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `node_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `node_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `data` json NULL,
  `create_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `update_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2560 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for shared_interactions
-- ----------------------------
DROP TABLE IF EXISTS `shared_interactions`;
CREATE TABLE `shared_interactions`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `interaction_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '交互ID',
  `user_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名',
  `create_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '创建时间',
  `update_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '更新时间',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '描述',
  `agent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'agent',
  `mode` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模式',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除',
  `star` int NOT NULL DEFAULT 0 COMMENT '星级',
  `record_dir` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '记录路径',
  `is_audit` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否通过审核',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 55 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户ID',
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '邮箱',
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '姓名',
  `token` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '令牌',
  `available` tinyint(1) NULL DEFAULT 1 COMMENT '是否可用',
  `corporation` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '公司',
  `industry` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '行业',
  `position` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '职位',
  `create_time` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '更新时间',
  `deleted` tinyint(1) NULL DEFAULT NULL COMMENT '删除标识',
  `is_beta` tinyint(1) NULL DEFAULT 0 COMMENT '是否内测用户',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 284 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

INSERT INTO xagent.users (user_id, email, name, token, available, corporation, industry, position, create_time, update_time, deleted, is_beta) VALUES ('guest', 'Guest', 'guest', 'xagent', 1, 'xagent', 'AI', 'NLP', '', '', 0, 1);

SET FOREIGN_KEY_CHECKS = 1;
