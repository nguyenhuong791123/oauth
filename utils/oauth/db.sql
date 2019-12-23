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
CREATE TABLE IF NOT EXISTS oa_basic (
  id INT NOT NULL PRIMARY KEY AUTO_INCREMENT
  ,username VARCHAR(20) NOT NULL DEFAULT ''
  ,password VARCHAR(80) NOT NULL DEFAULT ''
  ,UNIQUE KEY uk_oa_basic_username (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS oa_client (
  client_id VARCHAR(40) PRIMARY KEY
  ,client_secret VARCHAR(55) NOT NULL DEFAULT ''
  ,basic_id INT NOT NULL DEFAULT 0
  ,is_confidential BOOLEAN DEFAULT FALSE
  ,_redirect_uris TEXT
  ,_default_scopes TEXT
  ,description VARCHAR(400)
  ,UNIQUE KEY uk_client_secret (`client_secret`)
  ,CONSTRAINT fk_oa_client_username FOREIGN KEY (`basic_id`) REFERENCES `oa_basic` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS oa_grant (
  id INT NOT NULL PRIMARY KEY AUTO_INCREMENT
  ,client_id VARCHAR(40) NOT NULL DEFAULT ''
  ,basic_id INT NOT NULL DEFAULT 0
  ,code VARCHAR(255)
  ,redirect_uri VARCHAR(255)
  ,expires TIMESTAMP
  ,_scopes TEXT
  ,INDEX idx_grant_code(`code`)
  ,CONSTRAINT fk_oa_grant_username FOREIGN KEY (`basic_id`) REFERENCES `oa_basic` (`id`) ON UPDATE CASCADE
  ,CONSTRAINT fk_oa_grant_client_id FOREIGN KEY (`client_id`) REFERENCES `oa_client` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

CREATE TABLE IF NOT EXISTS oa_token (
  id INT NOT NULL PRIMARY KEY AUTO_INCREMENT
  ,token_type VARCHAR(40) NOT NULL DEFAULT ''
  ,basic_id INT NOT NULL DEFAULT 0
  ,client_id VARCHAR(40) NOT NULL DEFAULT ''
  ,access_token VARCHAR(255)
  ,refresh_token VARCHAR(255)
  ,expires TIMESTAMP
  ,_scopes TEXT
  ,UNIQUE KEY uk_token_access_token (`access_token`)
  ,UNIQUE KEY uk_token_refresh_token (`refresh_token`)
  ,CONSTRAINT fk_oa_token_username FOREIGN KEY (`basic_id`) REFERENCES `oa_basic` (`id`) ON UPDATE CASCADE
  ,CONSTRAINT fk_oa_token_client_id FOREIGN KEY (`client_id`) REFERENCES `oa_client` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
