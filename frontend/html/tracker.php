<html>
  <head>
    <title>Startpagina</title>
    <link rel="stylesheet" href="../../css/tracker.css">
    <script>
      function hpState($current, $max) {
        if ($current <= 0) return ['Unconscious', 'hp-0'];

        $pct = ($current / $max) * 100;

        if ($pct > 80) return ['Healthy', 'hp-healthy'];
        if ($pct > 50) return ['Injured', 'hp-injured'];
        if ($pct > 20) return ['Bloodied', 'hp-bloodied'];
        return ['Critical', 'hp-critical'];
      }
    </script>
  </head>
  <body>
    <main>
      <div>
        <h1>Encounter</h1>
        <table class="initiative-table">
          <thead>
            <tr>
              <th>Init</th>
              <th>Combatant</th>
              <th>AC</th>
              <th>HP</th>
              <th>Conditions</th>
            </tr>
          </thead>
          <tbody>
            <?php foreach ($combatants as $index => $c): ?>
              <tr class="<?= $index === $currentTurn ? 'current-turn' : '' ?>">
                <td><?= $c['initiative'] ?></td>
                <td>
                  <strong><?= htmlspecialchars($c['name']) ?></strong><br>
                  <?= $c['size'] ?> <?= $c['type'] ?><br>
                  <?php if ($c['combatant_type'] === 'PC'): ?>
                    <?= $c['class'] ?> (<?= $c['subclass'] ?>) — Lv <?= $c['level'] ?>
                  <?php endif; ?>
                </td>
                <td><?= $c['ac'] ?></td>
                <td>
                  <?php [$label, $css] = hpState($c['current_hp'], $c['hp_max']); ?>
                  <span class="hp-badge <?= $css ?>"><?= $label ?></span>
                </td>
                <td><?= renderConditions($c) ?></td>
              </tr>
            <?php endforeach; ?>
          </tbody>
        </table>
      </div>
      <div>
      
      </div>
    </main>
  </body>
</html>
