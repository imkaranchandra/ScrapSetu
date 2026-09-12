const rates={
 Plastic:20, Paper:15, Iron:35,
 Copper:600, Aluminium:120,
 Steel:45, "E-Waste":80
};

function login(){
    if(mobile.value && pass.value){
        loginDiv.classList.add("hide");
        app.classList.remove("hide");
    }else alert("Enter login details");
}

const loginDiv=document.getElementById("login");

function logout(){location.reload()}

function show(id){
    document.querySelectorAll(".section")
    .forEach(x=>x.classList.add("hide"));

    document.getElementById(id).classList.remove("hide");

    if(id=="history") load();
}

function calc(){
    let total=(rates[material.value]||0)*weight.value;
    price.innerText="₹"+total;
}

function add(){

    if(!material.value || !weight.value)
        return alert("Enter material and weight");

    let data=JSON.parse(localStorage.scrap||"[]");

    data.push({
        material:material.value,
        weight:weight.value,
        price:rates[material.value]*weight.value
    });

    localStorage.scrap=JSON.stringify(data);

    alert("Scrap added successfully!");
    show("history");
}

function load(){

    let data=JSON.parse(localStorage.scrap||"[]");

    list.innerHTML=data.length ?
        data.map((x,i)=>
        `<p>${i+1}. ${x.material} — ${x.weight}kg — ₹${x.price}</p>`
        ).join("") :
        "No collections yet.";
}