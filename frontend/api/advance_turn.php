<?php
require "db.php";

ini_set('log_errors', 1);
ini_set('error_log', '/var/log/php_errors.log');
error_reporting(E_ALL);

header('Content-Type: application/json');
ini_set('display_errors', 0);

$encounter_id = $_POST['encounter_id'] ?? null;
$combatant_count = $_POST['combatant_count'] ?? null;

if ($encounter_id === null || $combatant_count === null) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Missing parameters',
        'received' => $_POST
    ]);
    exit;
}

/*
|--------------------------------------------------------------------------
| Fetch current state
|--------------------------------------------------------------------------
*/
$stmt = $pdo->prepare("
    SELECT current_turn_index, round
    FROM encounters
    WHERE id = ?
");
$stmt->execute([$encounter_id]);
$encounter = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$encounter) {
    http_response_code(404);
    echo json_encode([
        'error' => 'Encounter not found',
        'received' => $_POST
    ]);
    exit;
}

$currentTurn = (int)$encounter['current_turn_index'];
$round = (int)$encounter['round'];

/*
|--------------------------------------------------------------------------
| Advance turn
|--------------------------------------------------------------------------
*/
$currentTurn++;

if ($currentTurn >= $combatant_count) {
    $currentTurn = 0;
    $round++;
}

/*
|--------------------------------------------------------------------------
| Persist
|--------------------------------------------------------------------------
*/
$update = $pdo->prepare("
    UPDATE encounters
    SET current_turn_index = ?, round = ?
    WHERE id = ?
");

try {
    $update->execute([$currentTurn, $round, $encounter_id]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Database update failed'
    ]);
    exit;
}

echo json_encode([
    'currentTurnIndex' => $currentTurn,
    'round' => $round
]);
