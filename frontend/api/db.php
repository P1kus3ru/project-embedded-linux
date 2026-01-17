<?php
$envPath = __DIR__ . '/../../.env';

if (file_exists($envPath)) {
    $lines = file($envPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (str_starts_with(trim($line), '#')) continue;
        [$key, $value] = explode('=', $line, 2);
        $_ENV[$key] = trim($value);
    }
}

$host = $_ENV['MYSQL_HOST'] ?? 'localhost';
$db   = $_ENV['MYSQL_DB'] ?? 'dnd';
$user = $_ENV['MYSQL_USER'] ?? 'lees';
$pass = $_ENV['MYSQL_PASS'] ?? 'lees';

error_log(print_r($_ENV, true));
try {
    $pdo = new PDO(
        "mysql:host=$host;dbname=$db;charset=utf8mb4",
        $user,
        $pass,
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
} catch (PDOException $e) {
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode([
        'error' => 'Database connection failed'
    ]);
    exit;
}
?>