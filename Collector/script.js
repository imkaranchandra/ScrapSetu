// ==========================================
// SCRAPSETU - COLLECTOR PORTAL (CONNECTED TO BACKEND)
// ==========================================

const API_BASE_URL = "http://192.168.29.209:8000/api";

// Fallback rates if backend is unreachable
let rates = {
    Plastic: 20,
    Paper: 15,
    Iron: 35,
    Copper: 600,
    Aluminium: 120,
    Steel: 45,
    "E-Waste": 80
};

// ==========================================
// INITIALIZATION & DYNAMIC RATES
// ==========================================

async function fetchRates() {
    try {
        const res = await fetch(`${API_BASE_URL}/rates/dict`);
        if (res.ok) {
            rates = await res.json();
            updatePriceBoardUI();
        }
    } catch (err) {
        console.warn("Backend offline, using fallback rates:", err.message);
    }
}

function updatePriceBoardUI() {
    const priceBoard = document.querySelector("#priceModal .prices");
    if (!priceBoard) return;

    let html = "";
    for (const [mat, rate] of Object.entries(rates)) {
        html += `
            <div class="price-row">
                <span>${mat}</span>
                <b>₹${rate}/kg</b>
            </div>
        `;
    }
    priceBoard.innerHTML = html;
}

// ==========================================
// AUTHENTICATION: LOGIN & SIGNUP
// ==========================================

function showSignup() {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    const portal = document.querySelector(".login-card .portal");
    if (loginForm && signupForm) {
        loginForm.classList.add("hide");
        signupForm.classList.remove("hide");
        if (portal) portal.innerText = "Create Collector ID";
    }
}

function showLogin() {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    const portal = document.querySelector(".login-card .portal");
    if (loginForm && signupForm) {
        signupForm.classList.add("hide");
        loginForm.classList.remove("hide");
        if (portal) portal.innerText = "Collector Portal";
    }
}

async function register() {
    const name = document.getElementById("signupName");
    const mobile = document.getElementById("signupMobile");
    const pass = document.getElementById("signupPass");
    const city = document.getElementById("signupCity");

    if (!name || !mobile || !pass) return;

    const nameVal = name.value.trim();
    const mobileVal = mobile.value.trim();
    const passVal = pass.value.trim();
    const cityVal = city ? city.value.trim() : "";

    if (nameVal === "" || mobileVal === "" || passVal === "") {
        alert("Please enter full name, mobile number, and choose a password.");
        return;
    }

    if (passVal.length < 4) {
        alert("Password must be at least 4 characters long.");
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name: nameVal,
                mobile: mobileVal,
                password: passVal,
                role: "collector",
                city: cityVal
            })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || "Registration failed.");
            return;
        }

        // Save login information
        localStorage.setItem("scrapsetu_token", data.access_token);
        localStorage.setItem("scrapsetu_user", JSON.stringify(data.user));

        alert(`🎉 Collector ID created successfully for ${nameVal}!`);

        // Automatically go to Collector dashboard
        window.location.href = "index.html";

    } catch (err) {
        console.error("Registration error:", err);
        alert("Registration failed. Please check that the backend is running.");
    }
}

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

    // Attempt backend authentication
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
        if (mobileVal === "9336864092" && passVal === "karancollector") {
            loginBox.classList.add("hide");
            app.classList.remove("hide");
        } else {
            alert("Login failed. Ensure backend is running or use credentials (Mobile: 9336864092, Password: karancollector).");
        }
    }
}

function updateProfileUI(user) {
    if (!user) return;
    const profileCard = document.querySelector("#profileModal .profile-info");
    if (profileCard) {
        profileCard.innerHTML = `
            <h3>${user.full_name || "Scrap Collector"}</h3>
            <p><b>Mobile:</b> ${user.mobile}</p>
            <p><b>Role:</b> Collector</p>
            <p><b>Status:</b> <span class="active">● Active</span></p>
            ${user.city ? `<p><b>City:</b> ${user.city}</p>` : ""}
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
// MODALS
// ==========================================

function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.add("show");
    document.body.classList.add("modal-open");

    if (id === "historyModal") {
        load();
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.remove("show");
    document.body.classList.remove("modal-open");
}

document.addEventListener("DOMContentLoaded", function () {
    fetchRates();

    const modals = document.querySelectorAll(".modal");
    modals.forEach(function (modal) {
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                modal.classList.remove("show");
                document.body.classList.remove("modal-open");
            }
        });
    });

    // Check if previously logged in
    const savedUser = localStorage.getItem("scrapsetu_user");
    if (savedUser) {
        try {
            updateProfileUI(JSON.parse(savedUser));
        } catch (e) {}
    }
});

// ==========================================
// CALCULATE PRICE
// ==========================================

function calc() {
    const material = document.getElementById("material");
    const weight = document.getElementById("weight");
    const price = document.getElementById("price");

    if (!material || !weight || !price) {
        return;
    }

    const selectedMaterial = material.value;
    const selectedWeight = Number(weight.value);
    const rate = rates[selectedMaterial] || 0;
    const total = rate * selectedWeight;

    price.innerText = "₹" + total;
}

// ==========================================
// ADD SCRAP
// ==========================================

async function add() {
    const material = document.getElementById("material");
    const weight = document.getElementById("weight");
    const price = document.getElementById("price");

    if (!material || !weight || !price) {
        return;
    }

    const matVal = material.value;
    const weightVal = Number(weight.value);

    if (matVal === "" || weight.value === "" || weightVal <= 0) {
        alert("Please select material and enter a valid weight.");
        return;
    }

    const calculatedPrice = (rates[matVal] || 0) * weightVal;
    const token = localStorage.getItem("scrapsetu_token");

    let submittedToBackend = false;

    // 1. Submit to Backend API
    try {
        const res = await fetch(`${API_BASE_URL}/scrap`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(token ? { "Authorization": `Bearer ${token}` } : {})
            },
            body: JSON.stringify({
                material: matVal,
                weight: weightVal,
                pickup_address: "Current Location"
            })
        });

        if (res.ok) {
            submittedToBackend = true;
        }
    } catch (err) {
        console.warn("Backend not available, saving locally:", err.message);
    }

    // 2. Also keep in localStorage for offline availability
    let localData = [];
    try {
        localData = JSON.parse(localStorage.getItem("scrap") || "[]");
    } catch (e) {
        localData = [];
    }

    localData.push({
        material: matVal,
        weight: weightVal,
        price: calculatedPrice,
        status: "Pending"
    });

    localStorage.setItem("scrap", JSON.stringify(localData));

    // Success feedback
    if (submittedToBackend) {
        alert("♻️ Scrap added successfully to ScrapSetu cloud & saved!");
    } else {
        alert("♻️ Scrap added successfully (saved locally)!");
    }

    // Clear form
    material.value = "";
    weight.value = "";
    price.innerText = "₹0";

    closeModal("addModal");
    openModal("historyModal");
}

// ==========================================
// LOAD HISTORY
// ==========================================

async function load() {
    const list = document.getElementById("list");
    if (!list) return;

    const token = localStorage.getItem("scrapsetu_token");
    let items = null;

    // 1. Try fetching from Backend API
    try {
        const res = await fetch(`${API_BASE_URL}/scrap/my-collections`, {
            headers: token ? { "Authorization": `Bearer ${token}` } : {}
        });
        if (res.ok) {
            items = await res.json();
        }
    } catch (err) {
        console.warn("Failed to load from backend, using local storage:", err.message);
    }

    // 2. Fallback to localStorage if backend failed
    if (!items) {
        try {
            items = JSON.parse(localStorage.getItem("scrap") || "[]");
        } catch (e) {
            items = [];
        }
    }

    // 3. Render Empty State
    if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = `
            <div class="empty">
                <div style="font-size:40px;">📦</div>
                <h3>No collections yet</h3>
                <p>Your submitted scrap will appear here.</p>
            </div>
        `;
        return;
    }

    // 4. Render Items
    let html = "";
    items.forEach(function (item, index) {
        const material = item.material || "Unknown";
        const weight = item.weight || 0;
        const itemPrice = item.price || 0;
        const status = item.status || "Pending";
        const lotNumber = item.lot_number || `#${index + 1}`;

        html += `
            <div class="collection">
                <div class="collection-top">
                    <div>
                        <span class="collection-number">
                            ${lotNumber}
                        </span>
                        <h3>
                            ${material}
                        </h3>
                    </div>
                    <span class="status">
                        ${status}
                    </span>
                </div>

                <div class="collection-details">
                    <div>
                        <small>Weight</small>
                        <b>⚖️ ${weight} kg</b>
                    </div>
                    <div>
                        <small>Estimated Value</small>
                        <b class="collection-price">₹${itemPrice}</b>
                    </div>
                </div>
            </div>
        `;
    });

    list.innerHTML = html;
}