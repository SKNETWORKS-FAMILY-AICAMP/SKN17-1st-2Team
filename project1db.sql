use project1db;

DROP TABLE chargers;

select * from chargers;

select address , count(*) from chargers group by address;

ALTER TABLE chargers DROP COLUMN station_id;
ALTER TABLE chargers DROP COLUMN charger_id;
ALTER TABLE chargers DROP COLUMN lat;
ALTER TABLE chargers DROP COLUMN lng;
ALTER TABLE chargers DROP COLUMN station_name;
ALTER TABLE chargers DROP COLUMN charger_type;
ALTER TABLE chargers DROP COLUMN use_time;
ALTER TABLE chargers DROP COLUMN operator_name;
ALTER TABLE chargers DROP COLUMN status;
ALTER TABLE chargers DROP COLUMN power_output;
ALTER TABLE chargers DROP COLUMN parking_free;
ALTER TABLE chargers DROP COLUMN last_update_dt;

DESCRIBE chargers;

drop table registgrccode;

create table regi(
	r_code int primary key,
    r_name varchar(20)
);

INSERT INTO 
    regi
VALUES 
    (1, '서울'),
    (2, '부산'),
    (3, '대구'),
    (4, '인천'),
    (5, '광주'),
    (6, '대전'),
    (7, '울산'),
    (8, '세종'),
    (9, '경기'),
    (10, '강원'),
    (11, '충북'),
    (12, '충남'),
    (13, '전북'),
    (14, '전남'),
    (15, '경북'),
    (16, '경남'),
    (17, '제주');
    
select r_code, r_name from regi;

ALTER TABLE chargers ADD COLUMN r_code INT;

SET SQL_SAFE_UPDATES = 0;

UPDATE chargers
SET r_code = CASE
    WHEN address LIKE '서울%' THEN 1
    WHEN address LIKE '부산%' THEN 2
    WHEN address LIKE '대구%' THEN 3
    WHEN address LIKE '인천%' THEN 4
    WHEN address LIKE '광주%' THEN 5
    WHEN address LIKE '대전%' THEN 6
    WHEN address LIKE '울산%' THEN 7
    WHEN address LIKE '세종%' THEN 8
    WHEN address LIKE '경기%' THEN 9
    WHEN address LIKE '강원%' THEN 10
    WHEN address LIKE '충청북도%' OR address LIKE '충북%' THEN 11
    WHEN address LIKE '충청남도%' OR address LIKE '충남%' THEN 12
    WHEN address LIKE '전라북도%' OR address LIKE '전북%' THEN 13
    WHEN address LIKE '전라남도%' OR address LIKE '전남%' THEN 14
    WHEN address LIKE '경상북도%' OR address LIKE '경북%' THEN 15
    WHEN address LIKE '경상남도%' OR address LIKE '경남%' THEN 16
    WHEN address LIKE '제주%' THEN 17
    ELSE NULL -- 일치하는 지역이 없을 경우
END;

DELETE FROM chargers WHERE r_code = NULL;

SET SQL_SAFE_UPDATES = 1;

alter TABLE chargers add constraint foreign key (r_code)
references regi (r_code) on DELETE CASCADE;

select * from chargers;

select r_code, count(*) from chargers group by r_code;