const API = "/api";

let roomsCache = [];
let usersCache = [];
let doorResetTimer = null;

//Funkcja api napisana została z pomocą AI
async function api(path, options = {}) {
    const res = await fetch(`${API}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Błąd żądania");
    }
    return res.status === 204 ? null : res.json();
}


function setupNavigation() {
    document.querySelector(".app-nav").addEventListener("click", (e) => {
        const btn = e.target.closest(".nav-btn");
        if (!btn) return;

        document.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));

        btn.classList.add("active");
        document.querySelector(`#view-${btn.dataset.view}`).classList.add("active");
    });
}

async function loadHealth() {
    const el = document.querySelector("#health-status");
    try {
        const data = await api("/health");
        const ok = data.database === "connected";
        el.textContent = ok ? "Online (DB połączona)" : "Błąd bazy danych";
        el.className = `badge ${ok ? "badge-ok" : "badge-deny"}`;
    } catch {
        el.textContent = "Backend niedostępny";
        el.className = "badge badge-deny";
    }
}

function updateRoomPlaqueMeta() {
    const code = document.querySelector("#sim-room-select").value;
    const room = roomsCache.find((r) => r.code === code);
    const meta = document.querySelector("#sim-room-meta");
    if (!room) {
        meta.textContent = "Brak pomieszczeń";
        return;
    }
    meta.textContent = `Wymagany poziom: ${room.min_access_level} | ${room.is_active ? "AKTYWNE" : "ZABLOKOWANE"}`;
}

function updateCardVisual() {
    const selectVal = document.querySelector("#sim-user-select").value;
    const ownerEl = document.querySelector("#card-display-owner");
    const idEl = document.querySelector("#card-display-id");
    const levelEl = document.querySelector("#card-display-level");
    const statusEl = document.querySelector("#card-display-status");

    const user = usersCache.find((u) => u.card_id === selectVal);
    if (!user) return;

    ownerEl.textContent = `${user.first_name} ${user.last_name}`;
    idEl.textContent = user.card_id;
    levelEl.textContent = `Poziom: ${user.access_level}`;
    statusEl.textContent = user.is_active ? "Aktywna" : "Nieaktywna";
}


async function loadRooms() {
    roomsCache = await api("/rooms");

    const simSelect = document.querySelector("#sim-room-select");
    const prevSim = simSelect.value;
    simSelect.innerHTML = roomsCache.map((r) => `<option value="${r.code}">${r.code} - ${r.name}</option>`).join("");
    if (roomsCache.some((r) => r.code === prevSim)) simSelect.value = prevSim;
    updateRoomPlaqueMeta();

    const filterSelect = document.querySelector("#log-filter-room");
    const prevFilter = filterSelect.value;
    filterSelect.innerHTML =
        `<option value="">Wszystkie pomieszczenia</option>` +
        roomsCache.map((r) => `<option value="${r.code}">${r.code} - ${r.name}</option>`).join("");
    filterSelect.value = prevFilter;

    document.querySelector("#rooms-table tbody").innerHTML = roomsCache
        .map(
        (r) => `
        <tr>
            <td>${r.code}</td>
            <td>${r.name}</td>
            <td>${r.min_access_level}</td>
            <td><span class="badge ${r.is_active ? "badge-ok" : "badge-deny"}">${r.is_active ? "AKTYWNE" : "ZABLOKOWANE"}</span></td>
            <td>
            <button type="button" class="action-btn" data-action="edit-room" data-id="${r.id}">Edytuj</button>
            <button type="button" class="action-btn" data-action="delete-room" data-id="${r.id}">Usuń</button>
            </td>
        </tr>`
        )
        .join("");
}

async function loadUsers() {
    usersCache = await api("/users");

    const userSelect = document.querySelector("#sim-user-select");
    const prevUser = userSelect.value;
    userSelect.innerHTML = usersCache
        .map((u) => `<option value="${u.card_id}">${u.card_id} - ${u.first_name} ${u.last_name} (poz. ${u.access_level})</option>`)
        .join("");
    if (usersCache.some((u) => u.card_id === prevUser)) {
        userSelect.value = prevUser;
    }
    updateCardVisual();

    document.querySelector("#users-table tbody").innerHTML = usersCache
        .map(
        (u) => `
        <tr>
            <td>${u.first_name}</td>
            <td>${u.last_name}</td>
            <td>${u.card_id}</td>
            <td>${u.access_level}</td>
            <td><span class="badge ${u.is_active ? "badge-ok" : "badge-deny"}">${u.is_active ? "AKTYWNA" : "NIEAKTYWNA"}</span></td>
            <td>
            <button type="button" class="action-btn" data-action="edit-user" data-id="${u.id}">Edytuj</button>
            <button type="button" class="action-btn" data-action="toggle-user" data-id="${u.id}">Przełącz</button>
            </td>
        </tr>`
        )
        .join("");
}

async function loadSimLogs() {
    const roomCode = document.querySelector("#sim-room-select").value;
    if (!roomCode) return;
    const logs = await api(`/access/logs?limit=8&room_code=${encodeURIComponent(roomCode)}`);
    document.querySelector("#sim-logs-table tbody").innerHTML = logs
        .map(
        (l) => `
        <tr>
            <td>${new Date(l.created_at).toLocaleString()}</td>
            <td>${l.card_id}</td>
            <td>${l.first_name ? `${l.first_name} ${l.last_name}` : "-"}</td>
            <td><span class="badge ${l.granted ? "badge-ok" : "badge-deny"}">${l.granted ? "PRZYZNANO" : "ODMOWA"}</span></td>
            <td>${l.reason}</td>
        </tr>`
        )
        .join("");
}

async function loadAdminLogs() {
    const roomCode = document.querySelector("#log-filter-room").value;
    const query = roomCode ? `?limit=50&room_code=${encodeURIComponent(roomCode)}` : "?limit=50";
    const logs = await api(`/access/logs${query}`);
    document.querySelector("#admin-logs-table tbody").innerHTML = logs
        .map(
        (l) => `
        <tr>
            <td>${new Date(l.created_at).toLocaleString()}</td>
            <td>${l.card_id}</td>
            <td>${l.first_name ? `${l.first_name} ${l.last_name}` : "-"}</td>
            <td>${l.room_code}</td>
            <td><span class="badge ${l.granted ? "badge-ok" : "badge-deny"}">${l.granted ? "PRZYZNANO" : "ODMOWA"}</span></td>
            <td>${l.reason}</td>
        </tr>`
        )
        .join("");
}

function setupSimulator() {
    const roomSelect = document.querySelector("#sim-room-select");
    const cardBtn = document.querySelector("#rfid-card");
    const cardConfig = document.querySelector("#card-config");
    const userSelect = document.querySelector("#sim-user-select");

    roomSelect.addEventListener("change", () => {
        updateRoomPlaqueMeta();
        loadSimLogs();
    });

    cardBtn.addEventListener("click", () => {
        cardConfig.classList.toggle("hidden");
    });

    userSelect.addEventListener("change", updateCardVisual);

    document.querySelector("#scan-btn").addEventListener("click", async () => {
        const roomCode = roomSelect.value;
        const cardId = userSelect.value;
        const screen = document.querySelector("#reader-status");
        const door = document.querySelector("#door-frame");

        if (!cardId || !roomCode) {
        screen.className = "reader-screen deny";
        screen.textContent = "BŁĄD";
        return;
        }

        clearTimeout(doorResetTimer);
        screen.className = "reader-screen";
        screen.textContent = "SPRAWDZANIE...";
        door.classList.remove("open");

        try {
        const res = await api("/access", {
            method: "POST",
            body: JSON.stringify({ card_id: cardId, room_code: roomCode }),
        });

        if (res.granted) {
            screen.className = "reader-screen ok";
            screen.textContent = "PRZYZNANO";
            door.classList.add("open");
        } else {
            screen.className = "reader-screen deny";
            screen.textContent = "ODMOWA";
        }

        await Promise.all([loadSimLogs(), loadAdminLogs()]);

        doorResetTimer = setTimeout(() => {
            screen.className = "reader-screen";
            screen.textContent = "GOTOWY";
            door.classList.remove("open");
        }, 3000);
        } catch {
        screen.className = "reader-screen deny";
        screen.textContent = "BŁĄD";
        }
    });
}

function setupAdmin() {
    const roomDialog = document.querySelector("#edit-room-dialog");
    const userDialog = document.querySelector("#edit-user-dialog");

    document.querySelector("#log-filter-room").addEventListener("change", loadAdminLogs);

    document.querySelector("#room-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const errEl = document.querySelector("#room-error");
        errEl.textContent = "";
        try {
        await api("/rooms", {
            method: "POST",
            body: JSON.stringify({
            code: document.querySelector("#room-code").value,
            name: document.querySelector("#room-name").value,
            min_access_level: Number(document.querySelector("#room-level").value),
            }),
        });
        e.target.reset();
        await loadRooms();
        } catch (err) {
        errEl.textContent = err.message;
        }
    });

    document.querySelector("#user-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const errEl = document.querySelector("#user-error");
        errEl.textContent = "";
        try {
        await api("/users", {
            method: "POST",
            body: JSON.stringify({
            first_name: document.querySelector("#user-first-name").value,
            last_name: document.querySelector("#user-last-name").value,
            card_id: document.querySelector("#user-card").value,
            access_level: Number(document.querySelector("#user-level").value),
            }),
        });
        e.target.reset();
        await loadUsers();
        } catch (err) {
        errEl.textContent = err.message;
        }
    });

    document.querySelector("#rooms-table tbody").addEventListener("click", async (e) => {
        const btn = e.target.closest("[data-action]");
        if (!btn) return;
        const id = Number(btn.dataset.id);

        if (btn.dataset.action === "delete-room") {
        await api(`/rooms/${id}`, { method: "DELETE" });
        await Promise.all([loadRooms(), loadSimLogs(), loadAdminLogs()]);
        } else if (btn.dataset.action === "edit-room") {
        const room = roomsCache.find((r) => r.id === id);
        if (!room) return;
        document.querySelector("#edit-room-id").value = room.id;
        document.querySelector("#edit-room-code").textContent = room.code;
        document.querySelector("#edit-room-name").value = room.name;
        document.querySelector("#edit-room-level").value = room.min_access_level;
        document.querySelector("#edit-room-active").checked = room.is_active;
        roomDialog.showModal();
        }
    });

    document.querySelector("#users-table tbody").addEventListener("click", async (e) => {
        const btn = e.target.closest("[data-action]");
        if (!btn) return;
        const id = Number(btn.dataset.id);

        if (btn.dataset.action === "toggle-user") {
        await api(`/users/${id}/toggle`, { method: "PATCH" });
        await loadUsers();
        } else if (btn.dataset.action === "edit-user") {
        const user = usersCache.find((u) => u.id === id);
        if (!user) return;
        document.querySelector("#edit-user-id").value = user.id;
        document.querySelector("#edit-user-card").textContent = user.card_id;
        document.querySelector("#edit-user-first").value = user.first_name;
        document.querySelector("#edit-user-last").value = user.last_name;
        document.querySelector("#edit-user-level").value = user.access_level;
        document.querySelector("#edit-user-active").checked = user.is_active;
        userDialog.showModal();
        }
    });

    document.querySelector("#cancel-room-edit").addEventListener("click", () => roomDialog.close());
    document.querySelector("#cancel-user-edit").addEventListener("click", () => userDialog.close());

    document.querySelector("#edit-room-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.querySelector("#edit-room-id").value;
        await api(`/rooms/${id}`, {
        method: "PUT",
        body: JSON.stringify({
            name: document.querySelector("#edit-room-name").value,
            min_access_level: Number(document.querySelector("#edit-room-level").value),
            is_active: document.querySelector("#edit-room-active").checked,
        }),
        });
        roomDialog.close();
        await loadRooms();
    });

    document.querySelector("#edit-user-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.querySelector("#edit-user-id").value;
        await api(`/users/${id}`, {
        method: "PUT",
        body: JSON.stringify({
            first_name: document.querySelector("#edit-user-first").value,
            last_name: document.querySelector("#edit-user-last").value,
            access_level: Number(document.querySelector("#edit-user-level").value),
            is_active: document.querySelector("#edit-user-active").checked,
        }),
        });
        userDialog.close();
        await loadUsers();
    });
}

async function init() {
    setupNavigation();
    setupSimulator();
    setupAdmin();
    await Promise.all([loadHealth(), loadRooms(), loadUsers()]);
    await Promise.all([loadSimLogs(), loadAdminLogs()]);
}

init();