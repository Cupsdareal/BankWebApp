const API_URL = "http://127.0.0.1:5000";

async function register() {
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    
    const response = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    alert(data.message);
}

async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    
    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (data.token) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("username", username);
        window.location.href = "dashboard.html";
    } else {
        alert("Échec de connexion !");
    }
}

async function loadDashboard() {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");

    if (!token) {
        alert("Vous devez être connecté !");
        window.location.href = "index.html";
        return;
    }

    document.getElementById("username").innerText = username;

    const response = await fetch(`${API_URL}/balance`, {
        method: "GET",
        headers: { "x-access-token": token }
    });

    const data = await response.json();
    document.getElementById("balance").innerText = data.balance;

    loadTransactions();
}

async function deposit() {
    const token = localStorage.getItem("token");
    const amount = parseFloat(document.getElementById("deposit-amount").value);

    if (!token) {
        alert("Vous devez être connecté !");
        return;
    }

    const response = await fetch(`${API_URL}/deposit`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "x-access-token": token
        },
        body: JSON.stringify({ amount })
    });

    const data = await response.json();
    alert(data.message);
    loadDashboard();
}

async function withdraw() {
    const token = localStorage.getItem("token");
    const amount = parseFloat(document.getElementById("withdraw-amount").value);

    if (!token) {
        alert("Vous devez être connecté !");
        return;
    }

    const response = await fetch(`${API_URL}/withdraw`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "x-access-token": token
        },
        body: JSON.stringify({ amount })
    });

    const data = await response.json();
    alert(data.message);
    loadDashboard();
}

async function transfer() {
    const token = localStorage.getItem("token");
    const receiver = document.getElementById("transfer-to").value;
    const amount = parseFloat(document.getElementById("transfer-amount").value);

    if (!token) {
        alert("Vous devez être connecté !");
        return;
    }

    const response = await fetch(`${API_URL}/transfer`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "x-access-token": token
        },
        body: JSON.stringify({ receiver, amount })
    });

    const data = await response.json();
    alert(data.message);
    loadDashboard();
}

async function loadTransactions() {
    const token = localStorage.getItem("token");

    if (!token) {
        return;
    }

    const response = await fetch(`${API_URL}/transactions`, {
        method: "GET",
        headers: { "x-access-token": token }
    });

    const data = await response.json();
    const transactionsList = document.getElementById("transactions-list");
    transactionsList.innerHTML = "";

    data.transactions.forEach(transaction => {
        const li = document.createElement("li");
        li.textContent = `${transaction.type === "sent" ? "Envoyé" : "Reçu"} ${transaction.amount}€ ${transaction.type === "sent" ? "à" : "de"} ${transaction.type === "sent" ? transaction.receiver : transaction.sender}`;
        transactionsList.appendChild(li);
    });
}

async function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    window.location.href = "index.html";
}

if (window.location.pathname.includes("dashboard.html")) {
    loadDashboard();
}
