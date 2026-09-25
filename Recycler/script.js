// ==========================================
// SCRAPSETU - RECYCLER PORTAL (CONNECTED TO BACKEND)
// ==========================================

const API_BASE_URL = "http://192.168.29.209:8000/api";

// Cached memory for active lots
let cachedIncomingLots = [];
let currentActivePickup = null;

// ==========================================
// LOGIN
// ==========================================

async function login() {
    const mobile = document.getElementById("mobile");
    const pass = document.getElementById("pass");
    const loginBox = document.getElementById("login");
    const app = document.getElementById("app");

    if (!mobile || !pass || !loginBox || !app) {
        return;
    }

    const mobileVal = mobile.value.trim();
    const passVal = pass.value.trim();

    if (mobileVal === "" || passVal === "") {
        alert("Please enter mobile number and password.");
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mobile: mobileVal,
                password: passVal
            })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("scrapsetu_token", data.access_token);
            localStorage.setItem("scrapsetu_user", JSON.stringify(data.user));
            updateProfileUI(data.user);

            // Access granted: switch to main app
            loginBox.classList.add("hide");
            app.classList.remove("hide");
        } else {
            alert(data.detail || "Invalid mobile number or password.");
        }
    } catch (err) {
        // Fallback check if backend is offline
        if (mobileVal === "9936541942" && passVal === "ramrecyclers") {
            loginBox.classList.add("hide");
            app.classList.remove("hide");
        } else {
            alert("Login failed. Ensure backend is running or use credentials (Mobile: 9936541942, Password: ramrecyclers).");
        }
    }
}

function updateProfileUI(user) {
    if (!user) return;
    const profileCard = document.querySelector("#profileModal .profile-info");
    if (profileCard) {
        profileCard.innerHTML = `
            <h3>${user.business_name || user.full_name || "Green Recycling Centre"}</h3>
            <p><b>Role:</b> Recycler</p>
            <p><b>Contact:</b> ${user.mobile}</p>
            <p><b>Status:</b> <span class="active">● Active</span></p>
            ${user.city ? `<p><b>Location:</b> ${user.city}</p>` : ""}
        `;
    }
}

// ==========================================
// LOGOUT
// ==========================================

function logout() {
    localStorage.removeItem("scrapsetu_token");
    localStorage.removeItem("scrapsetu_user");
    location.reload();
}

// ==========================================
// MODAL CONTROLS
// ==========================================

function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.add("show");
    document.body.classList.add("modal-open");

    if (id === "lotsModal") {
        loadIncomingLots();
    }
    if (id === "historyModal") {
        loadHistory();
    }
    if (id === "pickupModal") {
        loadPickup();
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.remove("show");
    document.body.classList.remove("modal-open");
}

document.addEventListener("DOMContentLoaded", function () {
    const modals = document.querySelectorAll(".modal");
    modals.forEach(function (modal) {
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                modal.classList.remove("show");
                document.body.classList.remove("modal-open");
            }
        });
    });

    const savedUser = localStorage.getItem("scrapsetu_user");
    if (savedUser) {
        try {
            updateProfileUI(JSON.parse(savedUser));
        } catch (e) {}
    }
});

// ==========================================
// LOCAL STORAGE HELPERS (FALLBACK)
// ==========================================

function getScrapData() {
    try {
        const data = JSON.parse(localStorage.getItem("scrap") || "[]");
        return Array.isArray(data) ? data : [];
    } catch (e) {
        return [];
    }
}

function saveScrapData(data) {
    localStorage.setItem("scrap", JSON.stringify(data));
}

// ==========================================
// LOAD INCOMING LOTS
// ==========================================

async function loadIncomingLots() {
    const container = document.getElementById("incomingLots");
    if (!container) return;

    let pendingLots = null;

    // 1. Fetch from Backend
    try {
        const res = await fetch(`${API_BASE_URL}/scrap/incoming`);
        if (res.ok) {
            pendingLots = await res.json();
            cachedIncomingLots = pendingLots;
        }
    } catch (err) {
        console.warn("Backend not accessible, reading local storage:", err.message);
    }

    // 2. Fallback to LocalStorage
    if (!pendingLots) {
        const localData = getScrapData();
        pendingLots = localData
            .map((item, idx) => ({ ...item, _localIndex: idx }))
            .filter(item => item.status === "Pending");
        cachedIncomingLots = pendingLots;
    }

    // 3. Render Empty State
    if (!pendingLots || pendingLots.length === 0) {
        container.innerHTML = `
            <div class="empty">
                <div class="empty-icon">📦</div>
                <h3>No incoming lots</h3>
                <p>New collector submissions will appear here.</p>
            </div>
        `;
        return;
    }

    // 4. Render Lots
    let html = "";
    pendingLots.forEach(function (item, index) {
        const material = item.material || "Unknown";
        const weight = item.weight || 0;
        const price = item.price || 0;
        const identifier = item.id !== undefined ? item.id : item._localIndex;
        const isBackendId = item.id !== undefined;

        html += `
            <div class="lot">
                <div class="lot-top">
                    <div>
                        <span class="lot-icon">♻️</span>
                        <div>
                            <h3>${material}</h3>
                            <p>${weight} kg ${item.lot_number ? `• ${item.lot_number}` : ""}</p>
                        </div>
                    </div>
                    <strong>₹${price}</strong>
                </div>

                <div class="lot-actions">
                    <button class="accept-btn" onclick="acceptLot(${identifier}, ${isBackendId})">
                        ✓ Accept
                    </button>
                    <button class="reject-btn" onclick="rejectLot(${identifier}, ${isBackendId})">
                        ✕ Reject
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// ==========================================
// ACCEPT LOT
// ==========================================

async function acceptLot(identifier, isBackendId) {
    const token = localStorage.getItem("scrapsetu_token");
    let acceptedItem = null;

    if (isBackendId) {
        try {
            const res = await fetch(`${API_BASE_URL}/scrap/${identifier}/accept`, {
                method: "POST",
                headers: token ? { "Authorization": `Bearer ${token}` } : {}
            });
            if (res.ok) {
                acceptedItem = await res.json();
            }
        } catch (err) {
            console.warn("Backend accept failed:", err.message);
        }
    }

    // Also update local storage mirror
    const localData = getScrapData();
    const idx = isBackendId ? localData.findIndex(d => d.id === identifier) : identifier;
    if (idx !== -1 && localData[idx]) {
        localData[idx].status = "Accepted";
        saveScrapData(localData);
        if (!acceptedItem) acceptedItem = localData[idx];
    }

    currentActivePickup = acceptedItem;
    alert("✅ Lot accepted! Pickup scheduled with logistics.");

    closeModal("lotsModal");
    openModal("pickupModal");
}

// ==========================================
// REJECT LOT
// ==========================================

async function rejectLot(identifier, isBackendId) {
    const token = localStorage.getItem("scrapsetu_token");

    if (isBackendId) {
        try {
            await fetch(`${API_BASE_URL}/scrap/${identifier}/reject`, {
                method: "POST",
                headers: token ? { "Authorization": `Bearer ${token}` } : {}
            });
        } catch (err) {
            console.warn("Backend reject failed:", err.message);
        }
    }

    // LocalStorage fallback
    const localData = getScrapData();
    const idx = isBackendId ? localData.findIndex(d => d.id === identifier) : identifier;
    if (idx !== -1 && localData[idx]) {
        localData[idx].status = "Rejected";
        saveScrapData(localData);
    }

    alert("❌ Scrap lot rejected.");
    loadIncomingLots();
}

// ==========================================
// UPDATE PICKUP UI
// ==========================================

function updatePickup(item) {
    const pickupStatus = document.getElementById("pickupStatus");
    if (!pickupStatus) return;

    currentActivePickup = item;
    const material = item.material || "Material";
    const weight = item.weight || 0;
    const price = item.price || 0;
    const lotNumber = item.lot_number || "Active Lot";

    pickupStatus.innerHTML = `
        <div class="pickup-active">
            <div class="pickup-symbol">🚚</div>
            <div>
                <span>Pickup Scheduled</span>
                <h3>${material} (${lotNumber})</h3>
                <p>${weight} kg &nbsp; • &nbsp; ₹${price}</p>
            </div>
        </div>

        <div class="pickup-line">
            <span class="done">✓</span>
            <span>Lot Accepted</span>
        </div>

        <div class="pickup-line">
            <span class="current">2</span>
            <span>Pickup Scheduled (Vehicle: MH-12-SS-2026)</span>
        </div>

        <div class="pickup-line">
            <span class="waiting">3</span>
            <span>Handover Pending</span>
        </div>
    `;

    const handoverButton = document.getElementById("handoverButton");
    if (handoverButton) {
        handoverButton.classList.remove("hide");
    }
}

// ==========================================
// LOAD PICKUP
// ==========================================

async function loadPickup() {
    const pickupStatus = document.getElementById("pickupStatus");
    const handoverButton = document.getElementById("handoverButton");
    const token = localStorage.getItem("scrapsetu_token");

    let activeLot = null;

    // 1. Try fetching from Backend API
    try {
        const res = await fetch(`${API_BASE_URL}/pickups/active`, {
            headers: token ? { "Authorization": `Bearer ${token}` } : {}
        });
        if (res.ok) {
            activeLot = await res.json();
        }
    } catch (err) {
        console.warn("Failed to fetch active pickup from backend:", err.message);
    }

    // 2. Fallback to localStorage
    if (!activeLot) {
        const localData = getScrapData();
        const acceptedLots = localData.filter(item => item.status === "Accepted");
        if (acceptedLots.length > 0) {
            activeLot = acceptedLots[acceptedLots.length - 1];
        }
    }

    if (!activeLot) {
        if (pickupStatus) {
            pickupStatus.innerHTML = `
                <div class="pickup-empty">
                    🚚
                    <h3>No active pickup</h3>
                    <p>Accept a lot to schedule a pickup.</p>
                </div>
            `;
        }
        if (handoverButton) {
            handoverButton.classList.add("hide");
        }
        return;
    }

    updatePickup(activeLot);
}

// ==========================================
// HANDOVER CONFIRMATION
// ==========================================

async function handover() {
    const token = localStorage.getItem("scrapsetu_token");
    let completedOnBackend = false;

    if (currentActivePickup && currentActivePickup.id) {
        try {
            const res = await fetch(`${API_BASE_URL}/scrap/${currentActivePickup.id}/handover`, {
                method: "POST",
                headers: token ? { "Authorization": `Bearer ${token}` } : {}
            });
            if (res.ok) {
                completedOnBackend = true;
            }
        } catch (err) {
            console.warn("Backend handover failed:", err.message);
        }
    }

    // Update Local Storage
    const localData = getScrapData();
    let found = false;
    for (let i = localData.length - 1; i >= 0; i--) {
        if (localData[i].status === "Accepted") {
            localData[i].status = "Completed";
            found = true;
            break;
        }
    }
    saveScrapData(localData);

    alert("🤝 Handover confirmed successfully! Scrap received and completed.");

    closeModal("handoverModal");
    closeModal("pickupModal");
    openModal("historyModal");
}

// ==========================================
// LOAD HISTORY
// ==========================================

async function loadHistory() {
    const historyList = document.getElementById("historyList");
    if (!historyList) return;

    const token = localStorage.getItem("scrapsetu_token");
    let transactions = null;

    // 1. Fetch from Backend API
    try {
        const res = await fetch(`${API_BASE_URL}/scrap/history`, {
            headers: token ? { "Authorization": `Bearer ${token}` } : {}
        });
        if (res.ok) {
            transactions = await res.json();
        }
    } catch (err) {
        console.warn("Failed to fetch history from backend:", err.message);
    }

    // 2. Fallback to localStorage
    if (!transactions) {
        const localData = getScrapData();
        transactions = localData.filter(
            item => item.status === "Accepted" || item.status === "Completed"
        );
    }

    if (!transactions || transactions.length === 0) {
        historyList.innerHTML = `
            <div class="empty">
                <div class="empty-icon">📜</div>
                <h3>No transactions yet</h3>
                <p>Accepted lots will appear here.</p>
            </div>
        `;
        return;
    }

    let html = "";
    transactions.forEach(function (item, index) {
        const material = item.material || "Unknown";
        const weight = item.weight || 0;
        const price = item.price || 0;
        const status = item.status || "Accepted";
        const statusClass = status === "Completed" ? "completed" : "accepted";
        const lotNumber = item.lot_number || `#${index + 1}`;

        html += `
            <div class="transaction">
                <div class="transaction-top">
                    <div>
                        <span class="transaction-number">
                            ${lotNumber}
                        </span>
                        <h3>
                            ${material}
                        </h3>
                    </div>

                    <span class="transaction-status ${statusClass}">
                        ${status}
                    </span>
                </div>

                <div class="transaction-details">
                    <div>
                        <small>Weight</small>
                        <b>⚖️ ${weight} kg</b>
                    </div>

                    <div>
                        <small>Amount</small>
                        <b class="transaction-price">₹${price}</b>
                    </div>
                </div>
            </div>
        `;
    });

    historyList.innerHTML = html;
}