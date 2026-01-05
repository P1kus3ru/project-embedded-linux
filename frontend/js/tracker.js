let combatants = [];
let currentTurn = 0;
let round = 1;
let encounterId = null;

function loadEncounter() {
    encounterId = document.getElementById("encounterId").value;

    fetch(`api/fetch_encounter.php?id=${encounterId}`)
        .then(res => res.json())
        .then(data => {
            combatants = data.combatants;
            currentTurn = data.currentTurnIndex;
            round = data.round;
            renderTable();
        });
}

function renderTable() {
    const tbody = document.querySelector("#combatTable tbody");
    tbody.innerHTML = "";
    document.getElementById("roundDisplay").textContent = `Round ${round}`;

    combatants.forEach((c, index) => {
        const tr = document.createElement("tr");
        if (index === currentTurn) tr.classList.add("active-turn");

        const hpDisplay =
            c.type === "pc"
                ? `${c.hp} / ${c.max_hp}`
                : monsterHealthDescription(c);

        const conditions =
            c.conditions.length
                ? c.conditions.map(cond => `${cond.name} (${cond.duration})`).join(", ")
                : "";

        tr.innerHTML = `
            <td>${index === currentTurn ? "▶" : ""}</td>
            <td>${c.name}<br/>${c.class ?? "-"} ${c.level ?? "-"}</td>
            <td>${c.ac}</td>
            <td>${hpDisplay}</td>
            <td>${conditions}</td>
        `;

        tbody.appendChild(tr);
    });
}

function monsterHealthDescription(c) {
    if (!c.hp || !c.max_hp) return "Unknown";

    const pct = (c.hp / c.max_hp) * 100;
    if (pct > 80) return "Healthy";
    if (pct > 50) return "Injured";
    if (pct > 20) return "Bloodied";
    return "Near Death";
}

function nextTurn() {
    fetch("api/advance_turn.php", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            encounter_id: encounterId,
            combatant_count: combatants.length
        })
    })
    .then(res => res.json())
    .then(data => {
        currentTurn = data.currentTurnIndex;
        round = data.round;
        renderTable();
    });
}