-- phpMyAdmin SQL Dump
-- version 3.4.3.2
-- http://www.phpmyadmin.net
--
-- Host: sql
-- Generation Time: Oct 14, 2013 at 04:35 PM
-- Server version: 5.1.66
-- PHP Version: 5.3.3-7+squeeze17

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `stkaddons_gsoc_dev`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`stkaddons_gsoc_dev`@`%` PROCEDURE `v2_create_file_record`(IN id TEXT, IN atype TEXT, IN ftype TEXT, IN fname TEXT, OUT insertid INT)
BEGIN
    INSERT INTO `v2_files`
    (`addon_id`,`addon_type`,`file_type`,`file_path`)
    VALUES
    (id,atype,ftype,fname);
    SELECT LAST_INSERT_ID() INTO insertid;
END$$

CREATE DEFINER=`stkaddons_gsoc_dev`@`%` PROCEDURE `v2_increment_download`(IN filepath TEXT)
UPDATE `v2_files`
    SET `downloads` = `downloads` + 1
    WHERE `file_path` = filepath$$

CREATE DEFINER=`stkaddons_gsoc_dev`@`%` PROCEDURE `v2_log_event`(IN in_user INT(10) unsigned, IN in_message TEXT)
INSERT INTO `v2_logs`
    (`user`,`message`)
    VALUES
    (in_user,in_message)$$

CREATE DEFINER=`stkaddons_gsoc_dev`@`%` PROCEDURE `v2_register_user`(IN in_user TEXT, IN in_pass CHAR(96), IN in_name TEXT, IN in_email TEXT, IN in_vercode TEXT, IN in_regdate DATE)
INSERT INTO `v2_users`
    (`user`,`pass`,`name`,`role`,`email`,`active`,`verify`,`reg_date`)
    VALUES
    (in_user, in_pass, in_name, 'basicUser', in_email, 0, in_vercode, in_regdate)$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_achieved`
--

CREATE TABLE IF NOT EXISTS `v2_achieved` (
  `userid` int(10) unsigned NOT NULL,
  `achievementid` int(10) unsigned NOT NULL,
  UNIQUE KEY `userid_2` (`userid`,`achievementid`),
  KEY `userid` (`userid`),
  KEY `achievementid` (`achievementid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `v2_achievements`
--

CREATE TABLE IF NOT EXISTS `v2_achievements` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_addons`
--

CREATE TABLE IF NOT EXISTS `v2_addons` (
  `id` varchar(30) NOT NULL,
  `type` enum('karts','tracks','arenas') NOT NULL,
  `name` tinytext NOT NULL,
  `uploader` int(11) NOT NULL,
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `designer` tinytext NOT NULL,
  `props` int(10) unsigned NOT NULL DEFAULT '0',
  `description` varchar(140) NOT NULL,
  `license` mediumtext,
  `min_include_ver` varchar(16) DEFAULT NULL,
  `max_include_ver` varchar(16) DEFAULT NULL,
  UNIQUE KEY `id` (`id`),
  KEY `type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_arenas_revs`
--

CREATE TABLE IF NOT EXISTS `v2_arenas_revs` (
  `id` char(23) NOT NULL,
  `addon_id` varchar(30) NOT NULL,
  `fileid` int(10) unsigned NOT NULL DEFAULT '0',
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `revision` tinyint(4) NOT NULL DEFAULT '1',
  `format` tinyint(4) NOT NULL,
  `image` int(10) unsigned NOT NULL DEFAULT '0',
  `status` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `moderator_note` varchar(4096) DEFAULT NULL,
  UNIQUE KEY `id` (`id`),
  KEY `track_id` (`addon_id`),
  KEY `status` (`status`),
  KEY `revision` (`revision`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_cache`
--

CREATE TABLE IF NOT EXISTS `v2_cache` (
  `file` varchar(30) NOT NULL,
  `addon` varchar(30) DEFAULT NULL,
  `props` text,
  UNIQUE KEY `file` (`file`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_clients`
--

CREATE TABLE IF NOT EXISTS `v2_clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `agent_string` varchar(255) NOT NULL,
  `stk_version` varchar(64) NOT NULL DEFAULT 'latest',
  `disabled` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=17 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_client_sessions`
--

CREATE TABLE IF NOT EXISTS `v2_client_sessions` (
  `uid` int(10) unsigned NOT NULL,
  `cid` char(24) NOT NULL,
  `online` tinyint(1) NOT NULL DEFAULT '1',
  `save` tinyint(1) NOT NULL DEFAULT '0',
  `ip` int(10) unsigned NOT NULL DEFAULT '0',
  `private_port` smallint(5) unsigned NOT NULL DEFAULT '0',
  `port` smallint(5) unsigned NOT NULL DEFAULT '0',
  `last-online` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `session` (`uid`,`cid`)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_config`
--

CREATE TABLE IF NOT EXISTS `v2_config` (
  `name` varchar(256) NOT NULL,
  `value` varchar(512) NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_files`
--

CREATE TABLE IF NOT EXISTS `v2_files` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `addon_id` varchar(30) NOT NULL,
  `addon_type` enum('karts','tracks','arenas') DEFAULT NULL,
  `file_type` enum('source','image','addon') DEFAULT NULL,
  `file_path` text NOT NULL,
  `date_added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Field added Jul 7 2011',
  `approved` int(1) NOT NULL DEFAULT '0',
  `downloads` int(10) unsigned NOT NULL DEFAULT '0',
  `delete_date` date NOT NULL DEFAULT '0000-00-00',
  PRIMARY KEY (`id`),
  KEY `delete_date` (`delete_date`),
  FULLTEXT KEY `file_path` (`file_path`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=101 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_friends`
--

CREATE TABLE IF NOT EXISTS `v2_friends` (
  `asker_id` int(10) unsigned NOT NULL,
  `receiver_id` int(10) unsigned NOT NULL,
  `request` tinyint(1) NOT NULL DEFAULT '1',
  `date` date NOT NULL,
  PRIMARY KEY (`asker_id`,`receiver_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `v2_help`
--

CREATE TABLE IF NOT EXISTS `v2_help` (
  `user` int(11) NOT NULL,
  `name` tinytext NOT NULL,
  `description` mediumtext NOT NULL,
  `file` text NOT NULL,
  `image` tinytext NOT NULL,
  `icon` tinytext NOT NULL,
  `date` date NOT NULL,
  `available` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `versionStk` tinytext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_history`
--

CREATE TABLE IF NOT EXISTS `v2_history` (
  `date` date NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` tinytext NOT NULL,
  `action` tinytext NOT NULL,
  `option` tinytext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_host_votes`
--

CREATE TABLE IF NOT EXISTS `v2_host_votes` (
  `userid` int(10) unsigned NOT NULL,
  `hostid` int(10) unsigned NOT NULL,
  `vote` int(11) NOT NULL,
  PRIMARY KEY (`userid`,`hostid`),
  KEY `hostid` (`hostid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `v2_karts_revs`
--

CREATE TABLE IF NOT EXISTS `v2_karts_revs` (
  `id` char(23) NOT NULL,
  `addon_id` varchar(30) NOT NULL,
  `fileid` int(10) unsigned NOT NULL DEFAULT '0',
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `revision` tinyint(4) NOT NULL DEFAULT '1',
  `format` tinyint(4) NOT NULL,
  `image` int(10) unsigned NOT NULL DEFAULT '0',
  `icon` int(10) unsigned NOT NULL DEFAULT '0',
  `status` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `moderator_note` varchar(4096) DEFAULT NULL,
  UNIQUE KEY `id` (`id`),
  KEY `track_id` (`addon_id`),
  KEY `status` (`status`),
  KEY `revision` (`revision`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_logs`
--

CREATE TABLE IF NOT EXISTS `v2_logs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user` int(10) unsigned NOT NULL,
  `message` text NOT NULL,
  `emailed` int(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=29 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_music`
--

CREATE TABLE IF NOT EXISTS `v2_music` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `artist` varchar(200) NOT NULL,
  `license` varchar(1000) NOT NULL,
  `gain` float NOT NULL DEFAULT '1',
  `length` int(11) NOT NULL DEFAULT '0',
  `file` varchar(200) NOT NULL,
  `file_md5` char(32) NOT NULL,
  `xml_filename` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `file` (`file`),
  UNIQUE KEY `xml_filename` (`xml_filename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_news`
--

CREATE TABLE IF NOT EXISTS `v2_news` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `author_id` int(11) unsigned NOT NULL DEFAULT '0',
  `content` char(140) DEFAULT NULL,
  `condition` varchar(255) DEFAULT NULL,
  `important` tinyint(1) NOT NULL DEFAULT '0',
  `web_display` tinyint(1) NOT NULL DEFAULT '1',
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `dynamic` int(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `date` (`date`,`active`),
  KEY `dynamic` (`dynamic`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=159 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_notifications`
--

CREATE TABLE IF NOT EXISTS `v2_notifications` (
  `to` int(10) unsigned NOT NULL,
  `from` int(10) unsigned NOT NULL,
  `type` varchar(10) NOT NULL,
  UNIQUE KEY `to_2` (`to`,`type`),
  KEY `to` (`to`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `v2_properties`
--

CREATE TABLE IF NOT EXISTS `v2_properties` (
  `type` text NOT NULL,
  `lock` int(11) NOT NULL,
  `typefield` text NOT NULL,
  `default` text NOT NULL,
  `name` text NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `v2_servers`
--

CREATE TABLE IF NOT EXISTS `v2_servers` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `hostid` int(10) unsigned NOT NULL,
  `name` tinytext NOT NULL,
  `ip` int(10) unsigned NOT NULL DEFAULT '0',
  `port` smallint(5) unsigned NOT NULL DEFAULT '0',
  `private_port` smallint(5) unsigned NOT NULL DEFAULT '0',
  `max_players` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `current_players` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT 'Isn''t exact. Just to show in the server-list, where it doens''t need to be exact.',
  PRIMARY KEY (`id`),
  KEY `hostid` (`hostid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=488 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_server_conn`
--

CREATE TABLE IF NOT EXISTS `v2_server_conn` (
  `serverid` int(10) unsigned NOT NULL,
  `userid` int(10) unsigned NOT NULL,
  `request` tinyint(1) NOT NULL DEFAULT '1',
  UNIQUE KEY `userid` (`userid`),
  KEY `serverid` (`serverid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_stats`
--

CREATE TABLE IF NOT EXISTS `v2_stats` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type` text NOT NULL,
  `date` date NOT NULL,
  `value` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_tracks_revs`
--

CREATE TABLE IF NOT EXISTS `v2_tracks_revs` (
  `id` char(23) NOT NULL,
  `addon_id` varchar(30) NOT NULL,
  `fileid` int(10) unsigned NOT NULL DEFAULT '0',
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `revision` tinyint(4) NOT NULL DEFAULT '1',
  `format` tinyint(4) NOT NULL,
  `image` int(10) unsigned NOT NULL DEFAULT '0',
  `status` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `moderator_note` varchar(4096) DEFAULT NULL,
  UNIQUE KEY `id` (`id`),
  KEY `track_id` (`addon_id`),
  KEY `status` (`status`),
  KEY `revision` (`revision`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `v2_users`
--

CREATE TABLE IF NOT EXISTS `v2_users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user` tinytext NOT NULL,
  `pass` char(96) NOT NULL,
  `name` tinytext NOT NULL,
  `role` tinytext NOT NULL,
  `email` tinytext NOT NULL,
  `active` tinyint(1) NOT NULL,
  `last_login` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `reg_date` date NOT NULL,
  `homepage` text,
  `avatar` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=45 ;

-- --------------------------------------------------------

--
-- Table structure for table `v2_verification`
--

CREATE TABLE IF NOT EXISTS `v2_verification` (
  `userid` int(10) unsigned NOT NULL DEFAULT '0',
  `code` text NOT NULL COMMENT 'The verification code',
  PRIMARY KEY (`userid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Used for account activation and recovery';

-- --------------------------------------------------------

--
-- Table structure for table `v2_votes`
--

CREATE TABLE IF NOT EXISTS `v2_votes` (
  `user_id` int(10) unsigned NOT NULL,
  `addon_id` varchar(30) NOT NULL,
  `vote` float unsigned NOT NULL,
  PRIMARY KEY (`user_id`,`addon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `v2_achieved`
--
ALTER TABLE `v2_achieved`
  ADD CONSTRAINT `v2_achieved_ibfk_2` FOREIGN KEY (`achievementid`) REFERENCES `v2_achievements` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `v2_achieved_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `v2_users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `v2_servers`
--
ALTER TABLE `v2_servers`
  ADD CONSTRAINT `v2_servers_ibfk_1` FOREIGN KEY (`hostid`) REFERENCES `v2_users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `v2_server_conn`
--
ALTER TABLE `v2_server_conn`
  ADD CONSTRAINT `v2_server_conn_ibfk_3` FOREIGN KEY (`serverid`) REFERENCES `v2_servers` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `v2_server_conn_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `v2_users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `v2_verification`
--
ALTER TABLE `v2_verification`
  ADD CONSTRAINT `v2_verification_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `v2_users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `v2_votes`
--
ALTER TABLE `v2_votes`
  ADD CONSTRAINT `v2_votes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `v2_users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

