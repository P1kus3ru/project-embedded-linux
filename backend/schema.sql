-- ================= CREATE DATABASE =================
-- DROP DATABASE IF EXISTS dnd;
-- CREATE DATABASE IF NOT EXISTS dnd;
-- USE dnd;

-- ================= CREATE TABLES =================
-- ================= USERS =================
CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- ================= ENCOUNTERS =================
CREATE TABLE IF NOT EXISTS encounters (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    date DATE,
    status VARCHAR(50),
    current_turn_index INT DEFAULT 0,
    round INT DEFAULT 1
) ENGINE=InnoDB;

-- ================= CREATURES =================
CREATE TABLE IF NOT EXISTS creatures (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    page VARCHAR(50),
    size VARCHAR(50),
    type VARCHAR(100),
    alignment VARCHAR(100),
    ac VARCHAR(10),
    hp_max VARCHAR(10),
    speed VARCHAR(20),
    strength INT,
    dexterity INT,
    constitution INT,
    intelligence INT,
    wisdom INT,
    charisma INT,
    saving_throws TEXT,
    skills TEXT,
    damage_vulnerabilities TEXT,
    damage_resistances TEXT,
    damage_immunities TEXT,
    condition_immunities TEXT,
    senses TEXT,
    languages TEXT,
    cr VARCHAR(10),
    traits TEXT,
    actions TEXT,
    bonus_actions TEXT,
    reactions TEXT,
    legendary_actions TEXT,
    mythic_actions TEXT,
    lair_actions TEXT,
    regional_effects TEXT,
    environment TEXT,
    treasure TEXT
) ENGINE=InnoDB;

-- ================= ADVENTURERS =================
CREATE TABLE IF NOT EXISTS adventurers (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED,
    page VARCHAR(50),
    name VARCHAR(255),
    species VARCHAR(100),
    class VARCHAR(100),
    subclass VARCHAR(100),
    level INT,
    ac VARCHAR(10),
    hp_max VARCHAR(10),
    speed VARCHAR(20),
    strength INT,
    dexterity INT,
    constitution INT,
    intelligence INT,
    wisdom INT,
    charisma INT,
    saving_throws TEXT,
    skills TEXT,
    damage_vulnerabilities TEXT,
    damage_resistances TEXT,
    damage_immunities TEXT,
    condition_immunities TEXT,
    senses TEXT,
    languages TEXT,
    CONSTRAINT fk_adv_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- ================= CONDITIONS =================
CREATE TABLE IF NOT EXISTS conditions (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    source VARCHAR(100)
) ENGINE=InnoDB;

-- ================= ENCOUNTER_ADVENTURERS =================
CREATE TABLE IF NOT EXISTS encounter_adventurers (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    encounter_id INT UNSIGNED NOT NULL,
    adventurer_id INT UNSIGNED NOT NULL,
    current_hp INT NOT NULL,
    initiative_roll INT,
    downed BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_ea_encounter FOREIGN KEY (encounter_id) REFERENCES encounters(id),
    CONSTRAINT fk_ea_adventurer FOREIGN KEY (adventurer_id) REFERENCES adventurers(id)
) ENGINE=InnoDB;

-- ================= ENCOUNTER_CREATURES =================
CREATE TABLE IF NOT EXISTS encounter_creatures (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    encounter_id INT UNSIGNED NOT NULL,
    creature_id INT UNSIGNED NOT NULL,
    instance_name VARCHAR(100),
    current_hp INT NOT NULL,
    initiative_roll INT,
    is_defeated BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_ec_encounter FOREIGN KEY (encounter_id) REFERENCES encounters(id),
    CONSTRAINT fk_ec_creature FOREIGN KEY (creature_id) REFERENCES creatures(id)
) ENGINE=InnoDB;

-- ================= COMBATANT_CONDITIONS =================
CREATE TABLE IF NOT EXISTS combatant_conditions (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    condition_id INT UNSIGNED NOT NULL,
    encounter_creature_id INT UNSIGNED NULL,
    encounter_adventurer_id INT UNSIGNED NULL,
    duration VARCHAR(50),
    CONSTRAINT fk_cc_condition FOREIGN KEY (condition_id) REFERENCES conditions(id),
    CONSTRAINT fk_cc_creature FOREIGN KEY (encounter_creature_id) REFERENCES encounter_creatures(id),
    CONSTRAINT fk_cc_adventurer FOREIGN KEY (encounter_adventurer_id) REFERENCES encounter_adventurers(id)
) ENGINE=InnoDB;