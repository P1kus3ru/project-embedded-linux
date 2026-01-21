let encounterId = null;
let combatants = [];
let currentTurn = 0;
let round = 1;

/* -----------------------------
   URL helpers
----------------------------- */
function getEncounterIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("encounterId");
}

function setEncounterIdInUrl(id) {
    const params = new URLSearchParams(window.location.search);

    if (id) {
        params.set("encounterId", id);
    } else {
        params.delete("encounterId");
    }

    const newUrl =
        params.toString().length > 0
            ? `${window.location.pathname}?${params.toString()}`
            : window.location.pathname;

    history.replaceState({}, "", newUrl);
}

/* -----------------------------
   Load encounter
----------------------------- */
function loadEncounter(idFromCall = null) {
    const input = document.getElementById("encounterId");

    encounterId = idFromCall !== null
        ? idFromCall
        : input.value.trim();

    if (!encounterId) {
        console.warn("No encounter ID");
        return;
    }

    // Always update URL
    setEncounterIdInUrl(encounterId);

    // fetch(`api/fetch_encounter?id=${encounterId}`)
    //     .then(res => {
    //         if (!res.ok) throw new Error("Encounter not found");
    //         return res.json();
    //     })
    //     .then(data => {
    //         combatants = data.combatants;
    //         currentTurn = data.currentTurnIndex;
    //         round = data.round;
    //         renderTable();
    //     })
    //     .catch(err => {
    //         console.error(err);
    //         alert("Failed to load encounter");
    //     });

    setInterval(() => {
        fetch(`api/fetch_encounter?id=${encounterId}`)
            .then(res => {
                if (!res.ok) throw new Error("Encounter not found");
                return res.json();
            })
            .then(data => {
                combatants = data.combatants;
                currentTurn = data.currentTurnIndex;
                round = data.round;
                renderTable();
            })
            .catch(err => {
                console.error(err);
                alert("Failed to load encounter");
            });
    }, 1000);
}

function nextTurn() {
    fetch("api/advance_turn", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            encounter_id: encounterId,
            combatant_count: combatants.length
        })
    })
    .then(async res => {
        const text = await res.text();

        if (!res.ok) {
            console.error("Server error:", text);
            throw new Error(`HTTP ${res.status}`);
        }

        try {
            return JSON.parse(text);
        } catch (e) {
            console.error("Invalid JSON returned:", text);
            throw e;
        }
    })
    .then(data => {
        currentTurn = data.currentTurnIndex;
        round = data.round;
        renderTable();
    })
    .catch(err => {
        console.error("nextTurn failed:", err);
        alert("Failed to advance turn. Check console.");
    });
}

/* -----------------------------
   Init
----------------------------- */
document.addEventListener("DOMContentLoaded", () => {
    document
        .getElementById("loadBtn")
        .addEventListener("click", () => loadEncounter());

    const idFromUrl = getEncounterIdFromUrl();
    if (idFromUrl) {
        document.getElementById("encounterId").value = idFromUrl;
        loadEncounter(idFromUrl);
    }
});

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

        const conditionsText = (c.conditions ?? [])
            .map(cond => `${cond.name} (${cond.duration})`)
            .join(", ");

        tr.innerHTML = `
            <td>${index === currentTurn ? "▶" : ""}</td>
            <td>${c.name}<br/>${c.class ?? "-"} ${c.level ?? "-"}</td>
            <td>${c.ac}</td>
            <td>${hpDisplay}</td>
            <td>${conditionsText || "-"}</td>
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
