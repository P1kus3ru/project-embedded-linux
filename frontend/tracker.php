<!DOCTYPE html>
<html lang="en">
  <head>
      <meta charset="UTF-8">
      <title>D&D Encounter Tracker</title>
      <link rel="stylesheet" href="css/tracker.css">
  </head>
  <body>

    <h1>Encounter Tracker</h1>
    <h2 id="roundDisplay"></h2>

    <div class="controls">
        <input type="number" id="encounterId" placeholder="Encounter ID">
        <button id="loadBtn">Load Encounter</button>
    </div>

    <table id="combatTable" class="Initiative-table">
        <thead>
            <tr>
                <th>Initiative</th>
                <th>Name</th>
                <th>AC</th>
                <th>HP</th>
                <th>Conditions</th>
            </tr>
        </thead>
        <tbody>

        </tbody>
    </table>

    <div class="turn-controls">
        <button onclick="nextTurn()">Next Turn</button>
    </div>

    <script src="js/tracker.js"></script>
  </body>
</html>