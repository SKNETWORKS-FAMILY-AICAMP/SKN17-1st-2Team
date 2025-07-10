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

select * from ford_faq;

drop table e_car;

create table e_car(
		e_num int primary key,
        e_year int,
        e_mon int,
        e_regi char(10),
        e_ener varchar(30),
        e_new int
);

select * from e_car;

create table car(
		car_num int primary key,
        Sido char(10),
        Sigungu char(30),
        RegistrationMonth date,
        VehicleType char(30),
        RegisteredCount int
);

select * from e_car;

ALTER TABLE car DROP COLUMN sigungu;

ALTER TABLE car ADD COLUMN r_code INT;

SET SQL_SAFE_UPDATES = 1;

UPDATE car
SET r_code = CASE
    WHEN sido LIKE '서울%' THEN 1
    WHEN sido LIKE '부산%' THEN 2
    WHEN sido LIKE '대구%' THEN 3
    WHEN sido LIKE '인천%' THEN 4
    WHEN sido LIKE '광주%' THEN 5
    WHEN sido LIKE '대전%' THEN 6
    WHEN sido LIKE '울산%' THEN 7
    WHEN sido LIKE '세종%' THEN 8
    WHEN sido LIKE '경기%' THEN 9
    WHEN sido LIKE '강원%' THEN 10
    WHEN sido LIKE '충청북도%' OR sido LIKE '충북%' THEN 11
    WHEN sido LIKE '충청남도%' OR sido LIKE '충남%' THEN 12
    WHEN sido LIKE '전라북도%' OR sido LIKE '전북%' THEN 13
    WHEN sido LIKE '전라남도%' OR sido LIKE '전남%' THEN 14
    WHEN sido LIKE '경상북도%' OR sido LIKE '경북%' THEN 15
    WHEN sido LIKE '경상남도%' OR sido LIKE '경남%' THEN 16
    WHEN sido LIKE '제주%' THEN 17
    ELSE NULL
END;

alter TABLE car add constraint foreign key (r_code)
references regi (r_code) on DELETE CASCADE;

ALTER TABLE car DROP COLUMN sido;
ALTER TABLE car DROP COLUMN vehicletype;

ALTER TABLE e_car ADD COLUMN r_code INT;
ALTER TABLE e_car DROP COLUMN e_mon;

UPDATE e_car
SET r_code = CASE
    WHEN e_regi LIKE '서울%' THEN 1
    WHEN e_regi LIKE '부산%' THEN 2
    WHEN e_regi LIKE '대구%' THEN 3
    WHEN e_regi LIKE '인천%' THEN 4
    WHEN e_regi LIKE '광주%' THEN 5
    WHEN e_regi LIKE '대전%' THEN 6
    WHEN e_regi LIKE '울산%' THEN 7
    WHEN e_regi LIKE '세종%' THEN 8
    WHEN e_regi LIKE '경기%' THEN 9
    WHEN e_regi LIKE '강원%' THEN 10
    WHEN e_regi LIKE '충청북도%' OR e_regi LIKE '충북%' THEN 11
    WHEN e_regi LIKE '충청남도%' OR e_regi LIKE '충남%' THEN 12
    WHEN e_regi LIKE '전라북도%' OR e_regi LIKE '전북%' THEN 13
    WHEN e_regi LIKE '전라남도%' OR e_regi LIKE '전남%' THEN 14
    WHEN e_regi LIKE '경상북도%' OR e_regi LIKE '경북%' THEN 15
    WHEN e_regi LIKE '경상남도%' OR e_regi LIKE '경남%' THEN 16
    WHEN e_regi LIKE '제주%' THEN 17
    ELSE NULL
END;

alter TABLE e_car add constraint foreign key (r_code)
references regi (r_code) on DELETE CASCADE;

ALTER TABLE e_car DROP COLUMN e_regi;

select r_code, count(*) from chargers group by r_code;

ALTER TABLE chargers DROP COLUMN address;

select * from kia_faq;

select * from car;

SET SQL_SAFE_UPDATES = 0;

ALTER TABLE car ADD COLUMN year INT;

UPDATE car SET Year = YEAR(RegistrationMonth);

ALTER TABLE car DROP COLUMN RegistrationMonth;

-- car 테이블 정규화
-- 신규 테이블 생성
-- GROUP BY r_code, year: r_code와 year가 같은 행들을 하나의 그룹으로 묶음.
-- 각 그룹의 RegisteredCount 값을 모두 더함
-- ROW_NUMBER() OVER (ORDER BY year, r_code): year와 r_code 순서로 정렬
-- 행에 1부터 시작하는 번호를 부여하여 새로운 car_num을 생성

CREATE TABLE car_aggregated AS SELECT
ROW_NUMBER() OVER (ORDER BY year, r_code) AS car_num, r_code, year,
SUM(RegisteredCount) AS RegisteredCount
FROM car GROUP BY r_code, year;

select * from car;
select * from e_car;


DROP TABLE car;

RENAME TABLE car_aggregated TO car;
-- 교체한 car 테이블 PK 재지정
ALTER TABLE car ADD PRIMARY KEY (car_num);

select * from ford_faq;
select * from kia_faq;

drop table ford_faq;
drop table kia_faq;

ALTER TABLE kia_faq DROP COLUMN crawled_at;
ALTER TABLE ford_faq DROP COLUMN crawled_at;

create table keyword (
	key_num int primary key,
    key_name char(30)
);

INSERT INTO keyword VALUES 
(1, '전기'), (2, '하이브리드');

select * from keyword;

ALTER TABLE kia_faq ADD COLUMN key_num INT;
ALTER TABLE ford_faq ADD COLUMN key_num INT;

UPDATE ford_faq
SET
    key_num = 1;
    
UPDATE kia_faq SET
key_num = 1
where faq_id < 11;

UPDATE kia_faq SET
key_num = 2
where faq_id > 10;

ALTER TABLE kia_faq DROP COLUMN keyword;

alter TABLE kia_faq add constraint foreign key (key_num)
references keyword (key_num) on DELETE CASCADE;

alter TABLE ford_faq add constraint foreign key (key_num)
references keyword (key_num) on DELETE CASCADE;