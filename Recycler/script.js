// ==========================================
// SCRAPSETU - RECYCLER PORTAL
// ==========================================


// ==========================================
// LOGIN
// ==========================================

function login() {

    const mobile =
        document.getElementById("mobile");

    const pass =
        document.getElementById("pass");

    const loginBox =
        document.getElementById("login");

    const app =
        document.getElementById("app");


    if (
        !mobile ||
        !pass ||
        !loginBox ||
        !app
    ) {
        return;
    }


    if (
        mobile.value.trim() !== "" &&
        pass.value.trim() !== ""
    ) {

        loginBox.classList.add("hide");

        app.classList.remove("hide");

    } else {

        alert(
            "Please enter mobile number and password."
        );

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

    const modal =
        document.getElementById(id);


    if (!modal) {
        return;
    }


    modal.classList.add("show");

    document.body.classList.add(
        "modal-open"
    );


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


// ==========================================
// CLOSE MODAL
// ==========================================

function closeModal(id) {

    const modal =
        document.getElementById(id);


    if (!modal) {
        return;
    }


    modal.classList.remove("show");

    document.body.classList.remove(
        "modal-open"
    );

}


// ==========================================
// CLICK OUTSIDE MODAL TO CLOSE
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const modals =
            document.querySelectorAll(".modal");


        modals.forEach(
            function (modal) {

                modal.addEventListener(
                    "click",
                    function (event) {

                        if (
                            event.target === modal
                        ) {

                            modal.classList.remove(
                                "show"
                            );

                            document.body.classList.remove(
                                "modal-open"
                            );

                        }

                    }
                );

            }
        );

    }
);


// ==========================================
// READ COLLECTOR DATA
// ==========================================

function getScrapData() {

    let data = [];


    try {

        data = JSON.parse(
            localStorage.getItem(
                "scrap"
            ) || "[]"
        );

    } catch (error) {

        data = [];

    }


    if (!Array.isArray(data)) {

        data = [];

    }


    return data;

}


// ==========================================
// SAVE COLLECTOR DATA
// ==========================================

function saveScrapData(data) {

    localStorage.setItem(
        "scrap",
        JSON.stringify(data)
    );

}


// ==========================================
// LOAD INCOMING LOTS
// ==========================================

function loadIncomingLots() {

    const container =
        document.getElementById(
            "incomingLots"
        );


    if (!container) {
        return;
    }


    const data =
        getScrapData();


    const pendingLots =
        data.filter(
            function (item) {

                return item.status === "Pending";

            }
        );


    if (pendingLots.length === 0) {

        container.innerHTML = `

            <div class="empty">

                <div class="empty-icon">
                    📦
                </div>

                <h3>
                    No incoming lots
                </h3>

                <p>
                    New collector submissions
                    will appear here.
                </p>

            </div>

        `;

        return;

    }


    let html = "";


    pendingLots.forEach(
        function (item) {

            const originalIndex =
                data.indexOf(item);


            const material =
                item.material || "Unknown";


            const weight =
                item.weight || 0;


            const price =
                item.price || 0;


            html += `

                <div class="lot">

                    <div class="lot-top">

                        <div>

                            <span class="lot-icon">
                                ♻️
                            </span>

                            <div>

                                <h3>
                                    ${material}
                                </h3>

                                <p>
                                    ${weight} kg
                                </p>

                            </div>

                        </div>


                        <strong>
                            ₹${price}
                        </strong>

                    </div>


                    <div class="lot-actions">

                        <button
                            class="accept-btn"
                            onclick="acceptLot(${originalIndex})">

                            ✓ Accept

                        </button>


                        <button
                            class="reject-btn"
                            onclick="rejectLot(${originalIndex})">

                            ✕ Reject

                        </button>

                    </div>

                </div>

            `;

        }
    );


    container.innerHTML = html;

}


// ==========================================
// ACCEPT LOT
// ==========================================

function acceptLot(index) {

    const data =
        getScrapData();


    if (
        !data[index] ||
        data[index].status !== "Pending"
    ) {

        alert(
            "This lot is no longer available."
        );

        loadIncomingLots();

        return;

    }


    data[index].status =
        "Accepted";


    saveScrapData(data);


    updatePickup(
        data[index]
    );


    alert(
        "✅ Lot accepted! Pickup scheduled."
    );


    closeModal("lotsModal");

    openModal("pickupModal");

}


// ==========================================
// REJECT LOT
// ==========================================

function rejectLot(index) {

    const data =
        getScrapData();


    if (
        !data[index] ||
        data[index].status !== "Pending"
    ) {

        alert(
            "This lot is no longer available."
        );

        loadIncomingLots();

        return;

    }


    const material =
        data[index].material;


    data[index].status =
        "Rejected";


    saveScrapData(data);


    alert(
        "❌ " +
        material +
        " lot rejected."
    );


    loadIncomingLots();

}


// ==========================================
// UPDATE PICKUP
// ==========================================

function updatePickup(item) {

    const pickupStatus =
        document.getElementById(
            "pickupStatus"
        );


    if (!pickupStatus) {
        return;
    }


    pickupStatus.innerHTML = `

        <div class="pickup-active">

            <div class="pickup-symbol">
                🚚
            </div>

            <div>

                <span>
                    Pickup Scheduled
                </span>

                <h3>
                    ${item.material}
                </h3>

                <p>
                    ${item.weight} kg
                    &nbsp; • &nbsp;
                    ₹${item.price}
                </p>

            </div>

        </div>


        <div class="pickup-line">

            <span class="done">
                ✓
            </span>

            <span>
                Lot Accepted
            </span>

        </div>


        <div class="pickup-line">

            <span class="current">
                2
            </span>

            <span>
                Pickup Scheduled
            </span>

        </div>


        <div class="pickup-line">

            <span class="waiting">
                3
            </span>

            <span>
                Handover Pending
            </span>

        </div>

    `;


    const handoverButton =
        document.getElementById(
            "handoverButton"
        );


    if (handoverButton) {

        handoverButton.classList.remove(
            "hide"
        );

    }

}


// ==========================================
// LOAD PICKUP
// ==========================================

function loadPickup() {

    const data =
        getScrapData();


    const acceptedLots =
        data.filter(
            function (item) {

                return item.status === "Accepted";

            }
        );


    const handoverButton =
        document.getElementById(
            "handoverButton"
        );


    if (acceptedLots.length === 0) {

        const pickupStatus =
            document.getElementById(
                "pickupStatus"
            );


        if (pickupStatus) {

            pickupStatus.innerHTML = `

                <div class="pickup-empty">

                    🚚

                    <h3>
                        No active pickup
                    </h3>

                    <p>
                        Accept a lot to schedule
                        a pickup.
                    </p>

                </div>

            `;

        }


        if (handoverButton) {

            handoverButton.classList.add(
                "hide"
            );

        }


        return;

    }


    const latest =
        acceptedLots[
            acceptedLots.length - 1
        ];


    updatePickup(latest);

}


// ==========================================
// HANDOVER
// ==========================================

function handover() {

    const data =
        getScrapData();


    let found = false;


    for (
        let i = data.length - 1;
        i >= 0;
        i--
    ) {

        if (
            data[i].status ===
            "Accepted"
        ) {

            data[i].status =
                "Completed";

            found = true;

            break;

        }

    }


    if (!found) {

        alert(
            "No accepted lot available."
        );

        return;

    }


    saveScrapData(data);


    alert(
        "🤝 Handover confirmed successfully!"
    );


    closeModal("handoverModal");

    closeModal("pickupModal");

    openModal("historyModal");

}


// ==========================================
// LOAD HISTORY
// ==========================================

function loadHistory() {

    const historyList =
        document.getElementById(
            "historyList"
        );


    if (!historyList) {
        return;
    }


    const data =
        getScrapData();


    const transactions =
        data.filter(
            function (item) {

                return (
                    item.status === "Accepted" ||
                    item.status === "Completed"
                );

            }
        );


    if (transactions.length === 0) {

        historyList.innerHTML = `

            <div class="empty">

                <div class="empty-icon">
                    📜
                </div>

                <h3>
                    No transactions yet
                </h3>

                <p>
                    Accepted lots will appear here.
                </p>

            </div>

        `;

        return;

    }


    let html = "";


    transactions.forEach(
        function (item, index) {

            const material =
                item.material || "Unknown";


            const weight =
                item.weight || 0;


            const price =
                item.price || 0;


            const status =
                item.status || "Accepted";


            const statusClass =
                status === "Completed"
                    ? "completed"
                    : "accepted";


            html += `

                <div class="transaction">

                    <div class="transaction-top">

                        <div>

                            <span
                                class="transaction-number">

                                #${index + 1}

                            </span>

                            <h3>
                                ${material}
                            </h3>

                        </div>


                        <span
                            class="
                            transaction-status
                            ${statusClass}
                            ">

                            ${status}

                        </span>

                    </div>


                    <div class="transaction-details">

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
                                Amount
                            </small>

                            <b
                                class="transaction-price">

                                ₹${price}

                            </b>

                        </div>

                    </div>

                </div>

            `;

        }
    );


    historyList.innerHTML =
        html;

}