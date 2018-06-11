CREATE TABLE `user` (
  `id` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `open_id` varchar(32) NOT NULL COMMENT '用户 open_id',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_oid` (`open_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;