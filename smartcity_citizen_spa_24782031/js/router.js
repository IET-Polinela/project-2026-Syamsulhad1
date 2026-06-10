function isAuthenticated() {
    return Boolean(localStorage.getItem("access_token"));
}

function updateNavigation(currentHash) {
    const navMenu = document.getElementById("nav-menus");
    const navUserLabel = document.getElementById("navUserLabel");

    if (!navMenu) return;

    if (isAuthenticated()) {
        if (navUserLabel) {
            navUserLabel.innerHTML = 'Citizen <span class="nav-logo-role">(Aktif)</span>';
        }

        navMenu.innerHTML = `
            <button type="button" class="nav-auth-btn nav-auth-logout" onclick="logout()">
                <i class="bi bi-box-arrow-right me-1"></i>Logout
            </button>
        `;
        return;
    }

    if (navUserLabel) {
        navUserLabel.textContent = "Citizen Portal";
    }

    navMenu.innerHTML = `
        <a href="#login" class="nav-auth-btn ${currentHash === "#login" ? "nav-auth-primary" : "nav-auth-outline"}">
            <i class="bi bi-box-arrow-in-right me-1"></i>Login
        </a>
        <a href="#register" class="nav-auth-btn ${currentHash === "#register" ? "nav-auth-primary" : "nav-auth-outline"}">
            <i class="bi bi-person-plus me-1"></i>Register
        </a>
    `;
}

function loginView() {
    return `
        <div class="login-shell">
            <div class="portal-card login-card">
                <div class="mb-4">
                    <div class="login-kicker">Citizen Portal</div>
                    <h1 class="h4 fw-bold mb-2">Login SmartReport</h1>
                    <p class="text-secondary mb-0">Masuk untuk membuat, mengelola, dan memantau laporan kota.</p>
                </div>

                <form id="loginForm">
                    <label class="form-label fw-semibold" for="loginUsername">Username</label>
                    <input
                        type="text"
                        id="loginUsername"
                        class="form-control mb-3"
                        placeholder="Masukkan username"
                        autocomplete="username"
                        required>

                    <label class="form-label fw-semibold" for="loginPassword">Password</label>
                    <input
                        type="password"
                        id="loginPassword"
                        class="form-control mb-4"
                        placeholder="Masukkan password"
                        autocomplete="current-password"
                        required>

                    <button type="submit" class="btn btn-primary w-100 fw-bold py-2">
                        <i class="bi bi-box-arrow-in-right me-2"></i>Login
                    </button>

                    <a href="#register" class="btn btn-outline-primary w-100 fw-bold py-2 mt-3">
                        <i class="bi bi-person-plus me-2"></i>Register
                    </a>
                </form>
            </div>
        </div>
    `;
}

function registerView() {
    return `
        <div class="login-shell">
            <div class="portal-card login-card">
                <div class="mb-4">
                    <div class="login-kicker">Citizen Portal</div>
                    <h1 class="h4 fw-bold mb-2">Register SmartReport</h1>
                    <p class="text-secondary mb-0">Buat akun warga untuk mulai mengirim dan memantau laporan kota.</p>
                </div>

                <form id="registerForm">
                    <label class="form-label fw-semibold" for="registerUsername">Username</label>
                    <input
                        type="text"
                        id="registerUsername"
                        class="form-control mb-3"
                        placeholder="Pilih username"
                        autocomplete="username"
                        required>

                    <label class="form-label fw-semibold" for="registerPassword">Password</label>
                    <input
                        type="password"
                        id="registerPassword"
                        class="form-control mb-3"
                        placeholder="Buat password"
                        autocomplete="new-password"
                        required>

                    <label class="form-label fw-semibold" for="registerPasswordConfirm">Konfirmasi Password</label>
                    <input
                        type="password"
                        id="registerPasswordConfirm"
                        class="form-control mb-4"
                        placeholder="Ulangi password"
                        autocomplete="new-password"
                        required>

                    <button type="submit" class="btn btn-primary w-100 fw-bold py-2">
                        <i class="bi bi-person-plus me-2"></i>Register
                    </button>

                    <p class="text-secondary text-center small mt-3 mb-0">
                        Sudah punya akun? <a href="#login" class="fw-semibold">Login</a>
                    </p>
                </form>
            </div>
        </div>
    `;
}

function dashboardView() {
    return `
        <div class="dashboard-app">
            <aside class="app-sidebar">
                <div class="app-brand">
                    <div class="app-brand-mark">SR</div>
                    <div>
                        <div class="app-brand-title">SmartReport</div>
                        <div class="app-brand-subtitle">Citizen Portal</div>
                    </div>
                </div>

                <nav class="app-sidebar-nav" aria-label="Menu dashboard">
                    <button type="button" class="app-nav-link active" data-nav-tab="my_reports">
                        <i class="bi bi-person-lines-fill"></i>
                        <span>Laporan Saya</span>
                    </button>
                    <button type="button" class="app-nav-link" data-nav-tab="feed">
                        <i class="bi bi-broadcast"></i>
                        <span>Feed Kota</span>
                    </button>
                    <button type="button" class="app-nav-link app-nav-danger" onclick="logout()">
                        <i class="bi bi-box-arrow-left"></i>
                        <span>Logout</span>
                    </button>
                </nav>

                <div class="app-sidebar-section">
                    <button type="button" class="new-report-button" id="newReportButton">
                        <i class="bi bi-plus-circle-fill me-2"></i>Laporan Baru
                    </button>
                </div>

                <div class="app-sidebar-section app-status-panel">
                    <h2 class="app-sidebar-title">Rekap Status</h2>
                    <div class="summary-item">
                        <span>Draft</span>
                        <span class="summary-number" id="draftCount">0</span>
                    </div>
                    <div class="summary-item">
                        <span>Reported</span>
                        <span class="summary-number" id="reportedCount">0</span>
                    </div>
                    <div class="summary-item">
                        <span>Verified</span>
                        <span class="summary-number" id="verifiedCount">0</span>
                    </div>
                    <div class="summary-item">
                        <span>In Progress</span>
                        <span class="summary-number" id="inProgressCount">0</span>
                    </div>
                    <div class="summary-item">
                        <span>Resolved</span>
                        <span class="summary-number" id="resolvedCount">0</span>
                    </div>
                </div>
            </aside>

            <section class="app-main">
                <header class="app-topbar">
                    <div>
                        <div class="dashboard-kicker">Citizen Dashboard</div>
                        <h1 class="app-page-title">Portal Laporan Warga</h1>
                        <p class="text-secondary mb-0">Kelola draft, pantau progress laporan, dan lihat feed publik SmartReport.</p>
                    </div>
                    <button type="button" class="app-topbar-logout" onclick="logout()">
                        <i class="bi bi-box-arrow-right"></i>
                        <span>Logout</span>
                    </button>
                </header>

                <div class="app-workspace">
                    <main class="app-report-area">
                        <div class="dashboard-tabs">
                            <button type="button" class="dashboard-tab active" data-tab="my_reports">
                                <i class="bi bi-person-lines-fill me-1"></i>Laporan Saya
                            </button>
                            <button type="button" class="dashboard-tab" data-tab="feed">
                                <i class="bi bi-broadcast me-1"></i>Feed Kota
                            </button>
                        </div>

                        <div id="reportList" class="mt-3">
                            <div class="portal-card empty-list">
                                <div>
                                    <div class="spinner-border text-primary mb-3" role="status"></div>
                                    <p class="mb-0">Memuat data laporan...</p>
                                </div>
                            </div>
                        </div>

                        <div id="paginationBar" class="pagination-bar"></div>
                    </main>

                    <aside class="app-announcement-area">
                        <div class="portal-card announcement-card">
                            <div class="announcement-header">
                                <h2 class="announcement-title">
                                    <i class="bi bi-megaphone-fill"></i>Pengumuman
                                </h2>
                                <span class="announcement-count" id="announcementCount">0</span>
                            </div>

                            <div class="announcement-list" id="announcementList">
                                <div class="announcement-empty">
                                    <div>
                                        <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
                                        <div>Memuat pengumuman laporan...</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </aside>
                </div>
            </section>
        </div>
    `;
}

const routes = {
    "#login": loginView,
    "#register": registerView,
    "#dashboard": dashboardView
};

function setupDashboardActions() {

    if (typeof initializeDashboard === "function") {
        initializeDashboard();
    }

    if (typeof loadDashboardData === "function") {
        loadDashboardData("my_reports", 1);
    }

    const newReportButton =
        document.getElementById("newReportButton");

    if (
        newReportButton &&
        typeof openCreateModal === "function"
    ) {
        newReportButton.addEventListener(
            "click",
            openCreateModal
        );
    }
}
function handleRouting() {
    const hash = window.location.hash || "#login";
    const targetHash = routes[hash] ? hash : "#login";

    if (targetHash === "#dashboard" && !isAuthenticated()) {
        window.location.hash = "#login";
        return;
    }

    document.body.dataset.view = targetHash.replace("#", "");
    document.getElementById("app-content").innerHTML = routes[targetHash]();
    updateNavigation(targetHash);

    if (targetHash === "#login" && typeof setupLoginForm === "function") {
        setupLoginForm();
    }

    if (targetHash === "#register" && typeof setupRegisterForm === "function") {
        setupRegisterForm();
    }

    if (targetHash === "#dashboard") {
        setupDashboardActions();
    }
}

window.addEventListener("hashchange", handleRouting);
window.addEventListener("DOMContentLoaded", handleRouting);
