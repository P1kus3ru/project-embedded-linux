<html>
  <head>
    <title>Startpagina</title>
    <style>
      table {
        border-collapse: collapse;
        border: 2px solid rgb(140 140 140);
        font-family: sans-serif;
        font-size: 0.8rem;
        letter-spacing: 1px;
        justify-self: center;
      }

      caption {
        caption-side: bottom;
        padding: 10px;
        font-weight: bold;
      }

      thead,
      tfoot {
        background-color: rgb(228 240 245);
      }

      th,
      td {
        border: 1px solid rgb(160 160 160);
        padding: 8px 10px;
      }

      td:last-of-type {
        text-align: center;
      }

      tbody > tr:nth-of-type(even) {
        background-color: rgb(237 238 242);
      }

      tfoot th {
        text-align: right;
      }

      tfoot td {
        font-weight: bold;
      }

    </style>
  </head>
  <body>
    <main>
      <h1>Encounter</h1>
      <table>
        <caption></caption>
        <thead>
          <tr>
            <th>Initiative</th>
            <th>Name</th>
            <th>HP</th>
            <th>AC</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <?php
            $servername = "localhost";
            $username = "lees";
            $password = "lees";
            $dbname = "dnd";
            // creëer connectie
            $conn = mysqli_connect($servername, $username, $password, $dbname);
            // controleer connectie
            if (!$conn) {
              die("Connection failed: " . mysqli_connect_error());
            }
            $sql = "SELECT * FROM adventurers";
            $result = mysqli_query($conn, $sql);
            if (mysqli_num_rows($result) > 0) {
              // data van elke rij tonen
              while($row = mysqli_fetch_assoc($result)) {
              echo "<tr><td>" . $row["id"]. "</td><td>" . $row["name"] . "</br>" . $row["class"] . " " . $row["level"] . "</td><td>" . $row["hp_max"]. "</td><td>" . $row["ac"]. "</td><td> 0 </td></tr>";
              }
            }
            else echo "0 results";
            mysqli_close($conn);
          ?>
        </tbody>
      </table>
    </main>
  </body>
</html>
