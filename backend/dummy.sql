-- ===== INSERT DUMMY DATA =====
-- Users
INSERT INTO users (username, role) VALUES
('DM_Jona', 'dm'),
('Player_Ash', 'player'),
('Player_Brook', 'player');

-- Adventurers
INSERT INTO adventurers (
    user_id, page, name, species, class, subclass, level,
    ac, hp_max, speed, strength, dexterity, constitution,
    intelligence, wisdom, charisma,
    saving_throws, skills, senses, languages
) VALUES
(2, '10', 'Thorin Oakenshield', 'Dwarf', 'Fighter', 'Champion', 5, '18', '45', '25 ft',
 18, 12, 16, 10, 11, 10, 'STR, CON', 'Athletics, Survival', 'Darkvision 60 ft', 'Common, Dwarvish'),
(3, '12', 'Elaria Moonwhisper', 'Elf', 'Wizard', 'Evocation', 5, '13', '28', '30 ft',
 8, 16, 12, 18, 14, 11, 'INT, WIS', 'Arcana, History', 'Darkvision 60 ft', 'Common, Elvish');

-- Encounters
INSERT INTO encounters (name, location, date, status) VALUES
('Goblin Ambush', 'Neverwinter Forest', '2025-12-01', 'active');

-- Creatures
INSERT INTO creatures (
    name, source, size, type, alignment, ac, hp_max, speed,
    strength, dexterity, constitution, intelligence, wisdom, charisma,
    cr, actions
) VALUES
('Goblin', 'MM', 'Small', 'Humanoid', 'Neutral Evil', '15', '7', '30 ft',
 8, 14, 10, 10, 8, 8, '1/4', 'Scimitar, Shortbow');

-- Encounter creatures
INSERT INTO encounter_creatures (
    encounter_id, creature_id, instance_name, current_hp, initiative_roll
) VALUES
(1, 1, 'Goblin_1', 7, 15),
(1, 1, 'Goblin_2', 7, 12);

-- Encounter adventurers
INSERT INTO encounter_adventurers (
    encounter_id, adventurer_id, current_hp, initiative_roll
) VALUES
(1, 1, 45, 18),
(1, 2, 28, 14);

-- Conditions
INSERT INTO conditions (name, description, source) VALUES
('Poisoned', 'Disadvantage on attack rolls and ability checks.', 'PHB'),
('Stunned', 'Cannot move or take actions.', 'PHB');

-- Apply condition to Goblin_1
INSERT INTO combatant_conditions (
    condition_id, encounter_creature_id, duration
) VALUES
(1, 1, '2 rounds');