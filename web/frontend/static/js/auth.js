document.querySelectorAll(".auth-tab").forEach((tab) => {
    tab.onclick = () => {
        document.querySelectorAll(".auth-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById("login-form").style.display = tab.dataset.tab === "login" ? "block" : "none";
        document.getElementById("register-form").style.display = tab.dataset.tab === "register" ? "block" : "none";
        document.getElementById("auth-error").textContent = "";
    };
});

document.getElementById("login-form").onsubmit = async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = { email: form.email.value, password: form.password.value };
    const err = document.getElementById("auth-error");
    try {
        const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || "Помилка");
        localStorage.setItem("token", json.token);
        localStorage.setItem("user", JSON.stringify(json.user));
        window.location.href = "/";
    } catch (ex) {
        err.textContent = ex.message;
    }
};

document.getElementById("register-form").onsubmit = async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = { email: form.email.value, username: form.username.value, password: form.password.value };
    const err = document.getElementById("auth-error");
    try {
        const res = await fetch("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || "Помилка");
        localStorage.setItem("token", json.token);
        localStorage.setItem("user", JSON.stringify(json.user));
        window.location.href = "/";
    } catch (ex) {
        err.textContent = ex.message;
    }
};
