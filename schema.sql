USE `githubreporting`;
DROP TABLE repositories;
DROP TABLE branches;
DROP TABLE branch_diff;
DROP TABLE commits;
DROP TABLE files;
DROP TABLE commit_files;

CREATE TABLE repositories (
  id   MEDIUMINT    NOT NULL AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE branches (
  id            MEDIUMINT    NOT NULL AUTO_INCREMENT,
  name          VARCHAR(200) NOT NULL,
  repository_id INT          NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (repository_id) REFERENCES repositories (id)
);

CREATE TABLE branch_diff (
  id            MEDIUMINT NOT NULL AUTO_INCREMENT,
  branch_a_id   INT       NOT NULL,
  branch_b_id   INT       NOT NULL,
  repository_id INT       NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (branch_a_id, branch_b_id) REFERENCES branches (id, id),
  FOREIGN KEY (repository_id) REFERENCES repositories (id)
);

CREATE TABLE commits (
  id             INT           NOT NULL AUTO_INCREMENT,
  repository_id  INT           NOT NULL,
  branch_diff_id INT           NOT NULL,
  sha            VARCHAR(40)   NOT NULL,
  author         VARCHAR(128)  NOT NULL,
  message        VARCHAR(1024) NOT NULL,
  commit_date    DATETIME      NOT NULL,
  jira           VARCHAR(16),
  PRIMARY KEY (id),
  FOREIGN KEY (repository_id) REFERENCES repositories (id),
  FOREIGN KEY (branch_diff_id) REFERENCES branch_diff (id)
);

CREATE TABLE files (
  id            INT          NOT NULL AUTO_INCREMENT,
  repository_id INT          NOT NULL,
  path          VARCHAR(256) NOT NULL,
  module        VARCHAR(64),
  PRIMARY KEY (id),
  FOREIGN KEY (repository_id) REFERENCES repositories (id)
);

CREATE TABLE commit_files (
  commit_id     INT     NOT NULL,
  file_id       INT     NOT NULL,
  action        CHAR(1) NOT NULL,
  lines_added   INT     NOT NULL,
  lines_removed INT     NOT NULL
);

COMMIT;