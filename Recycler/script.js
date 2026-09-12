function login(){

    if(mobile.value && pass.value){
        loginBox.classList.add("hide");
        app.classList.remove("hide");
    }else{
        alert("Enter login details");
    }
}

const loginBox=document.getElementById("login");


function show(id){

    document.querySelectorAll(".section")
    .forEach(x=>x.classList.add("hide"));

    document.getElementById(id)
    .classList.remove("hide");
}


function accept(material,weight,price){

    let data=JSON.parse(localStorage.transactions||"[]");

    data.push({
        material,
        weight,
        price,
        status:"Accepted"
    });

    localStorage.transactions=JSON.stringify(data);

    document.getElementById("pickupStatus").innerHTML=
        "🚚 <b>"+material+"</b> pickup scheduled.<br>Status: Accepted";

    alert("Lot accepted!");

    show("pickup");
}


function reject(material){

    alert(material+" lot rejected.");
}


function handover(){

    alert("✅ Handover confirmed!");

    let data=JSON.parse(localStorage.transactions||"[]");

    if(data.length){
        data[data.length-1].status="Completed";
        localStorage.transactions=JSON.stringify(data);
    }

    show("history");
    loadHistory();
}


function loadHistory(){

    let data=JSON.parse(localStorage.transactions||"[]");

    historyList.innerHTML=data.length ?
        data.map((x,i)=>
        `<p>${i+1}. ${x.material} — ${x.weight}kg — ₹${x.price}
        <br>✅ ${x.status}</p>`
        ).join("") :
        "No transactions yet.";
}