const routes = {

    "#login": `
        <div class="container mt-5">
            <h2>Login Citizen</h2>

            <form id="loginForm">

                <input
                    type="text"
                    id="loginUsername"
                    class="form-control mb-2"
                    placeholder="Username"
                    required>

                <input
                    type="password"
                    id="loginPassword"
                    class="form-control mb-2"
                    placeholder="Password"
                    required>

                <button
                    type="submit"
                    class="btn btn-primary">
                    Login
                </button>

            </form>
        </div>
    `,

    "#dashboard": `
        <div class="row">

            <aside class="col-12 col-lg-3">
                <div class="card p-3">
                    Menu
                </div>
            </aside>

            <section class="col-12 col-lg-6">
                <div class="card p-3">
                    Dashboard Citizen
                </div>
            </section>

            <aside class="col-12 col-lg-3">
                <div class="card p-3">
                    Pengumuman
                </div>
            </aside>

        </div>
    `
};

function handleRouting() {

    const hash =
        window.location.hash || "#login";

    document.getElementById(
        "app-content"
    ).innerHTML =
        routes[hash];

    if (
        hash === "#login" &&
        typeof setupLoginForm === "function"
    ) {
        setupLoginForm();
    }
}

window.addEventListener(
    "hashchange",
    handleRouting
);

window.addEventListener(
    "DOMContentLoaded",
    handleRouting
);