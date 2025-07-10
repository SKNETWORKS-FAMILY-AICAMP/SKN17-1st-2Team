-- [1] 데이터베이스 생성 및 선택
CREATE DATABASE IF NOT EXISTS ev_info
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_general_ci;

USE ev_info;

-- [2] 지역정보 테이블 생성
DROP TABLE IF EXISTS Region_Info;
CREATE TABLE Region_Info (
    RegionID VARCHAR(10) PRIMARY KEY,
    Sido VARCHAR(50) NOT NULL,
    Sigungu VARCHAR(50) NOT NULL
);

-- [3] 차종정보 테이블 생성
DROP TABLE IF EXISTS Car_Type_Info;
CREATE TABLE Car_Type_Info (
    CarTypeID INT AUTO_INCREMENT PRIMARY KEY,
    Manufacturer VARCHAR(50) NOT NULL,
    Model VARCHAR(100) NOT NULL,
    FuelType ENUM('전기', '수소') DEFAULT '전기',
    MaxRange INT,
    BatteryCapacity FLOAT,
    ChargingType ENUM('DC콤보', '차데모', 'AC') DEFAULT 'DC콤보'
);

-- [4] 차량등록정보 테이블 생성
DROP TABLE IF EXISTS Car_Registration;
CREATE TABLE Car_Registration (
    CarID VARCHAR(20) NOT NULL,
    RegistrationDate DATE NOT NULL,
    CarType VARCHAR(20),
    Manufacturer VARCHAR(50),
    Model VARCHAR(100),
    RegionID VARCHAR(10),
    VehicleType ENUM('승용', '화물') DEFAULT '승용',
    
    PRIMARY KEY (CarID, RegistrationDate),
    FOREIGN KEY (RegionID) REFERENCES Region_Info(RegionID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
