<?php
require "db.php";

$encounter_id = $_GET['id'] ?? null;
if (!$encounter_id) {
    http_response_code(400);
    exit("Missing encounter id");
}

/*
|--------------------------------------------------------------------------
| Fetch encounter meta
|--------------------------------------------------------------------------
*/
$encounterStmt = $pdo->prepare("
    SELECT current_turn_index, round
    FROM encounters
    WHERE id = ?
");
$encounterStmt->execute([$encounter_id]);
$encounter = $encounterStmt->fetch(PDO::FETCH_ASSOC);

if (!$encounter) {
    http_response_code(404);
    exit("Encounter not found");
}

/*
|--------------------------------------------------------------------------
| Fetch adventurers (PCs)
|--------------------------------------------------------------------------
*/
$pcStmt = $pdo->prepare("
    SELECT
        ea.id AS encounter_combatant_id,
        'pc' AS type,
        a.name,
        a.class,
        a.level,
        a.ac,
        ea.current_hp AS hp,
        a.hp_max AS max_hp,
        ea.initiative_roll AS initiative,
        ea.downed
    FROM encounter_adventurers ea
    JOIN adventurers a ON a.id = ea.adventurer_id
    WHERE ea.encounter_id = ?
");
$pcStmt->execute([$encounter_id]);
$pcs = $pcStmt->fetchAll(PDO::FETCH_ASSOC);

/*
|--------------------------------------------------------------------------
| Fetch creatures (monsters)
|--------------------------------------------------------------------------
*/
$monsterStmt = $pdo->prepare("
    SELECT
        ec.id AS encounter_combatant_id,
        'monster' AS type,
        COALESCE(ec.instance_name, c.name) AS name,
        NULL AS class,
        NULL AS level,
        c.ac,
        ec.current_hp AS hp,
        c.hp_max AS max_hp,
        ec.initiative_roll AS initiative,
        ec.is_defeated
    FROM encounter_creatures ec
    JOIN creatures c ON c.id = ec.creature_id
    WHERE ec.encounter_id = ?
");
$monsterStmt->execute([$encounter_id]);
$monsters = $monsterStmt->fetchAll(PDO::FETCH_ASSOC);

/*
|--------------------------------------------------------------------------
| Fetch conditions (shared logic)
|--------------------------------------------------------------------------
*/
$conditionsStmt = $pdo->prepare("
    SELECT
        cc.encounter_adventurer_id,
        cc.encounter_creature_id,
        cond.name,
        cc.duration
    FROM combatant_conditions cc
    JOIN conditions cond ON cond.id = cc.condition_id
");
$conditionsStmt->execute();
$conditions = $conditionsStmt->fetchAll(PDO::FETCH_ASSOC);

/*
|--------------------------------------------------------------------------
| Attach conditions to combatants
|--------------------------------------------------------------------------
*/
function attachConditions(&$combatants, $conditions, $key) {
    foreach ($combatants as &$c) {
        $c['conditions'] = [];
        foreach ($conditions as $cond) {
            if ($cond[$key] === $c['encounter_combatant_id']) {
                $c['conditions'][] = [
                    'name' => $cond['name'],
                    'duration' => $cond['duration']
                ];
            }
        }
    }
}

attachConditions($pcs, $conditions, 'encounter_adventurer_id');
attachConditions($monsters, $conditions, 'encounter_creature_id');

/*
|--------------------------------------------------------------------------
| Merge + sort by initiative
|--------------------------------------------------------------------------
*/
$combatants = array_merge($pcs, $monsters);

usort($combatants, function ($a, $b) {
    return ($b['initiative'] ?? 0) <=> ($a['initiative'] ?? 0);
});

echo json_encode([
    'round' => $encounter['round'],
    'currentTurnIndex' => (int)$encounter['current_turn_index'],
    'combatants' => $combatants
]);
