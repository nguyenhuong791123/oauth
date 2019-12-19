-- create the database for OAuth 2.0 provider and admin user
CREATE DATABASE IF NOT EXISTS sc_oauth;
-- CREATE USER 'oauth'@'localhost' IDENTIFIED BY 'Oauth080!';
-- GRANT ALL PRIVILEGES ON sc_oauth.* TO 'oauth'@'localhost';

-- access the recently created database oauth2provider
USE sc_oauth;

-- added innodb 767 byte error solution 
-- SET GLOBAL innodb_large_prefix=on;
-- SET GLOBAL innodb_file_format=Barracuda;
-- SET GLOBAL innodb_file_format_max=Barracuda;
-- SET GLOBAL innodb_file_per_table=true;

-- create needed structure for oauth provider
CREATE TABLE IF NOT EXISTS oa_users (
  user_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT
  ,user_mail VARCHAR(150) NOT NULL DEFAULT ''
  ,user_pass VARCHAR(80) NOT NULL DEFAULT ''
  ,UNIQUE KEY uk_users_user_mail (`user_mail`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

CREATE TABLE oa_client (
  client_id VARCHAR(40) PRIMARY KEY
  ,client_secret VARCHAR(55) NOT NULL DEFAULT ''
  ,user_id INT NOT NULL DEFAULT 0
  ,user_mail VARCHAR(40) NOT NULL DEFAULT ''
  ,is_confidential BOOLEAN DEFAULT FALSE
  ,redirect_uris TEXT
  ,default_scopes TEXT
  ,description VARCHAR(400)
  ,UNIQUE KEY uk_client_secret (`client_secret`)
  ,FOREIGN KEY (`user_id`) REFERENCES `oa_users` (`user_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS oa_grant (
  grant_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT
  ,client_id VARCHAR(40) NOT NULL DEFAULT ''
  ,user_id INT NOT NULL DEFAULT 0
  ,code VARCHAR(255)
  ,redirect_uri VARCHAR(255)
  ,expires TIMESTAMP
  ,scopes TEXT
  ,INDEX idx_grant_code(`code`)
  ,FOREIGN KEY (`user_id`) REFERENCES `oa_users` (`user_id`) ON UPDATE CASCADE
  ,FOREIGN KEY (`client_id`) REFERENCES `oa_client` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS oa_token (
  token_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT
  ,token_type VARCHAR(40) NOT NULL DEFAULT ''
  ,user_id INT NOT NULL DEFAULT 0
  ,client_id VARCHAR(40) NOT NULL DEFAULT ''
  ,access_token VARCHAR(255)
  ,refresh_token VARCHAR(255)
  ,expires TIMESTAMP
  ,scopes TEXT
  ,UNIQUE KEY uk_token_access_token (`access_token`)
  ,UNIQUE KEY uk_token_refresh_token (`refresh_token`)
  ,FOREIGN KEY (`user_id`) REFERENCES `oa_users` (`user_id`) ON UPDATE CASCADE
  ,FOREIGN KEY (`client_id`) REFERENCES `oa_client` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
