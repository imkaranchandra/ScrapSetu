// ==========================================
// SCRAPSETU - COLLECTOR PORTAL
// ==========================================


// ==========================================
// SCRAP RATES
// ==========================================

const rates = {
    Plastic: 20,
    Paper: 15,
    Iron: 35,
    Copper: 600,
    Aluminium: 120,
    Steel: 45,
    "E-Waste": 80
};


// ==========================================
// LOGIN
// ==========================================

function login() {

    const mobile = document.getElementById("mobile");
    const pass = document.getElementById("pass");
    const loginBox = document.getElementById("login");
    const app = document.getElementById("app");

    if (!mobile || !pass || !loginBox || !app) {
        return;
    }

    if (
        mobile.value.trim() !== "" &&
        pass.value.trim() !== ""
    ) {

        loginBox.classList.add("hide");
        app.classList.remove("hide");

    } else {

        alert("Please enter mobile number and password.");

    }
}


// ==========================================
// LOGOUT
// ==========================================

function logout() {

    location.reload();

}


// ==========================================
// OPEN MODAL
// ==========================================

function openModal(id) {

    const modal = document.getElementById(id);

    if (!modal) {
        return;
    }

    modal.classList.add("show");

    document.body.classList.add("modal-open");


    // Load history when history popup opens

    if (id === "historyModal") {

        load();

    }
}


// ==========================================
// CLOSE MODAL
// ==========================================

function closeModal(id) {

    const modal = document.getElementById(id);

    if (!modal) {
        return;
    }

    modal.classList.remove("show");

    document.body.classList.remove("modal-open");

}


// ==========================================
// CLOSE MODAL WHEN CLICKING OUTSIDE
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const modals = document.querySelectorAll(".modal");

    modals.forEach(function (modal) {

        modal.addEventListener("click", function (event) {

            if (event.target === modal) {

                modal.classList.remove("show");

                document.body.classList.remove(
                    "modal-open"
                );

            }

        });

    });

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

function add() {

    const material = document.getElementById("material");
    const weight = document.getElementById("weight");
    const price = document.getElementById("price");

    if (!material || !weight || !price) {
        return;
    }


    // Check input

    if (
        material.value === "" ||
        weight.value === "" ||
        Number(weight.value) <= 0
    ) {

        alert(
            "Please select material and enter a valid weight."
        );

        return;
    }


    // Get old scrap data

    let data = [];

    try {

        data = JSON.parse(
            localStorage.getItem("scrap") || "[]"
        );

    } catch (error) {

        data = [];

    }


    // Calculate price

    const calculatedPrice =
        (rates[material.value] || 0) *
        Number(weight.value);


    // Create scrap object

    const scrap = {

        material: material.value,

        weight: Number(weight.value),

        price: calculatedPrice,

        status: "Pending"

    };


    // Add scrap

    data.push(scrap);


    // Save scrap

    localStorage.setItem(
        "scrap",
        JSON.stringify(data)
    );


    // Success message

    alert("♻️ Scrap added successfully!");


    // Clear form

    material.value = "";

    weight.value = "";

    price.innerText = "₹0";


    // Close Add Scrap popup

    closeModal("addModal");


    // Open History popup

    openModal("historyModal");

}


// ==========================================
// LOAD HISTORY
// ==========================================

function load() {

    const list = document.getElementById("list");

    if (!list) {
        return;
    }


    // Get data

    let data = [];

    try {

        data = JSON.parse(
            localStorage.getItem("scrap") || "[]"
        );

    } catch (error) {

        data = [];

    }


    // No data

    if (
        !Array.isArray(data) ||
        data.length === 0
    ) {

        list.innerHTML = `
            <div class="empty">

                <div style="font-size:40px;">
                    📦
                </div>

                <h3>
                    No collections yet
                </h3>

                <p>
                    Your submitted scrap will
                    appear here.
                </p>

            </div>
        `;

        return;
    }


    // Show data

    let html = "";


    data.forEach(function (item, index) {

        const material =
            item.material || "Unknown";

        const weight =
            item.weight || 0;

        const itemPrice =
            item.price || 0;

        const status =
            item.status || "Pending";


        html += `

            <div class="collection">

                <div class="collection-top">

                    <div>

                        <span class="collection-number">
                            #${index + 1}
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

                        <small>
                            Weight
                        </small>

                        <b>
                            ⚖️ ${weight} kg
                        </b>

                    </div>


                    <div>

                        <small>
                            Estimated Value
                        </small>

                        <b class="collection-price">
                            ₹${itemPrice}
                        </b>

                    </div>

                </div>

            </div>

        `;

    });


    list.innerHTML = html;

}