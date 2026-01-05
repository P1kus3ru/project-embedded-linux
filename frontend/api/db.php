<?php
$host = $_ENV['MYSQL_HOST'] ?? 'localhost';
$db   = $_ENV['MYSQL_DB'] ?? 'dnd';
$user = $_ENV['MYSQL_USER'] ?? 'lees';
$pass = $_ENV['MYSQL_PASS'] ?? 'lees';

try {
    $pdo = new PDO(
        "mysql:host=$host;dbname=$db;charset=utf8mb4",
        $user,
        $pass,
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
} catch (PDOException $e) {
    http_response_code(500);
    echo "Database connection failed";
    exit;
}
?>