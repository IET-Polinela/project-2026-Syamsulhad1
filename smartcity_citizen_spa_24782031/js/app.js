let currentDashboardTab = "my_reports";
let currentDashboardPage = 1;
let editingReportId = null;
let reportModalInstance = null;
let reportFormListenersReady = false;

const categoryLabels = {
    INFRASTRUCTURE: "Infrastruktur & Jalan",
    SECURITY: "Keamanan",
    HEALTH: "Kesehatan",
    ENVIRONMENT: "Lingkungan & Kebersihan",
    PUBLIC_FACILITY: "Fasilitas Publik"
};

const statusLabels = {
    DRAFT: "Draft",
    REPORTED: "Dilaporkan",
    VERIFIED: "Terverifikasi",
    IN_PROGRESS: "Diproses",
    RESOLVED: "Selesai"
};

const statusProgress = {
    DRAFT: 10,
    REPORTED: 35,
    VERIFIED: 60,
    IN_PROGRESS: 80,
    RESOLVED: 100
};

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.hash = "#login";
}

function escapeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getResultsFromResponse(data) {
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.results)) return data.results;
    return [];
}

function getPageCount(data) {
    if (!data || Array.isArray(data)) return 1;

    const count = Number(data.count || 0);
    const pageSize = 10;

    return Math.max(1, Math.ceil(count / pageSize));
}

function getReportPayload() {
    return {
        title: document.getElementById("reportTitle").value.trim(),
        category: document.getElementById("reportCategory").value,
        description: document.getElementById("reportDescription").value.trim(),
        location: document.getElementById("reportLocation").value.trim(),
        is_anonymous: document.getElementById("reportAnonymous").checked
    };
}

function fillReportForm(report) {
    document.getElementById("reportTitle").value = report.title || "";
    document.getElementById("reportCategory").value = report.category || "ENVIRONMENT";
    document.getElementById("reportLocation").value = report.location || "";
    document.getElementById("reportDescription").value = report.description || "";
    document.getElementById("reportAnonymous").checked = Boolean(report.is_anonymous);
}

function resetReportPhotoPreview() {
    const input = document.getElementById("reportPhotoInput");
    const preview = document.getElementById("reportPhotoPreview");
    const image = document.getElementById("reportPhotoPreviewImage");

    if (input) {
        input.value = "";
    }

    if (image) {
        image.removeAttribute("src");
    }

    if (preview) {
        preview.classList.remove("has-image");
    }
}

function handleReportPhotoPreview(event) {
    const file = event.target.files && event.target.files[0];
    const preview = document.getElementById("reportPhotoPreview");
    const image = document.getElementById("reportPhotoPreviewImage");

    if (!file || !preview || !image) {
        resetReportPhotoPreview();
        return;
    }

    if (!file.type.startsWith("image/")) {
        alert("File harus berupa gambar.");
        resetReportPhotoPreview();
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        image.src = reader.result;
        preview.classList.add("has-image");
    };
    reader.readAsDataURL(file);
}

function resetReportForm() {
    const form = document.getElementById("reportForm");

    if (form) {
        form.reset();
    }

    resetReportPhotoPreview();
    editingReportId = null;
    document.getElementById("reportModalLabel").textContent = "Laporan Baru";
}

function openReportModal(report = null) {
    if (!reportModalInstance) {
        reportModalInstance = new bootstrap.Modal(
            document.getElementById("reportModal")
        );
    }

    resetReportForm();

    if (report) {
        editingReportId = report.id;
        fillReportForm(report);
        document.getElementById("reportModalLabel").textContent = "Edit Draft Laporan";
    }

    reportModalInstance.show();
}

async function saveReportDraft() {
    const endpoint = editingReportId
        ? `/api/reports/${editingReportId}/`
        : "/api/reports/";

    const method = editingReportId ? "PUT" : "POST";
    const response = await requestAPI(endpoint, method, getReportPayload());
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Laporan gagal disimpan.");
    }

    return data;
}

async function submitReport(reportId) {
    const response = await requestAPI(`/api/reports/${reportId}/submit/`, "POST");
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Laporan gagal diajukan.");
    }

    return data;
}

async function handleSaveDraft() {
    const form = document.getElementById("reportForm");

    if (!form.reportValidity()) return;

    const button = document.getElementById("saveDraftBtn");
    button.disabled = true;

    try {
        await saveReportDraft();
        reportModalInstance.hide();
        resetReportForm();
        await loadDashboardData(currentDashboardTab, currentDashboardPage);
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
    }
}

async function handleSubmitReport() {
    const form = document.getElementById("reportForm");

    if (!form.reportValidity()) return;

    const button = document.getElementById("submitReportBtn");
    button.disabled = true;

    try {
        const savedReport = await saveReportDraft();
        await submitReport(savedReport.id);
        reportModalInstance.hide();
        resetReportForm();
        await loadDashboardData(currentDashboardTab, 1);
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
    }
}

function setupReportModalEvents() {
    if (reportFormListenersReady) return;

    document.getElementById("saveDraftBtn").addEventListener("click", handleSaveDraft);
    document.getElementById("submitReportBtn").addEventListener("click", handleSubmitReport);
    document.getElementById("reportModal").addEventListener("hidden.bs.modal", resetReportForm);

    const photoInput = document.getElementById("reportPhotoInput");

    if (photoInput) {
        photoInput.addEventListener("change", handleReportPhotoPreview);
    }

    reportFormListenersReady = true;
}

function renderList(reports, tab) {
    const list = document.getElementById("reportList");

    if (!reports.length) {
        list.innerHTML = `
            <div class="portal-card empty-list">
                <div>
                    <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                    <p class="mb-0">Belum ada laporan pada tab ini.</p>
                </div>
            </div>
        `;
        return;
    }

    list.innerHTML = reports.map((report) => renderReportCard(report, tab)).join("");
}

function renderReportCard(report, tab) {
    if (tab === "feed") {
        return renderFeedCard(report);
    }

    const progress = statusProgress[report.status] || 0;
    const statusLabel = statusLabels[report.status] || report.status;
    const categoryLabel = categoryLabels[report.category] || report.category;
    const canEdit = tab === "my_reports" && report.is_owner && report.status === "DRAFT";
    const statusClass = getStatusClass(report.status);

    return `
        <article class="portal-card report-card ${statusClass}">
            <div class="d-flex align-items-start justify-content-between gap-3">
                <div>
                    <h2 class="report-card-title">${escapeHTML(report.title)}</h2>
                    <div class="report-meta">
                        <i class="bi bi-tags me-1"></i>${escapeHTML(categoryLabel)}
                        <span class="mx-1">|</span>
                        <i class="bi bi-person me-1"></i>${escapeHTML(report.reporter)}
                    </div>
                </div>
                <span class="status-badge">${escapeHTML(statusLabel)}</span>
            </div>

            <p class="my-3">${escapeHTML(report.description)}</p>

            <div class="report-meta mb-3">
                <i class="bi bi-geo-alt me-1"></i>${escapeHTML(report.location)}
            </div>

            <div class="progress" aria-label="Progress status laporan">
                <div
                    class="progress-bar"
                    role="progressbar"
                    style="width: ${progress}%"
                    aria-valuenow="${progress}"
                    aria-valuemin="0"
                    aria-valuemax="100"></div>
            </div>

            <div class="d-flex align-items-center justify-content-between mt-3">
                <span class="report-meta">Progress: ${progress}%</span>
                ${canEdit ? `
                    <button type="button" class="btn btn-outline-primary btn-sm fw-semibold" onclick="editDraft(${report.id})">
                        <i class="bi bi-pencil-square me-1"></i>Edit
                    </button>
                ` : ""}
            </div>
        </article>
    `;
}

function renderFeedCard(report) {
    const progress = statusProgress[report.status] || 0;
    const statusLabel = statusLabels[report.status] || report.status;
    const categoryLabel = categoryLabels[report.category] || report.category;
    const pillClass = getFeedStatusClass(report.status);
    const statusClass = getStatusClass(report.status);

    return `
        <article class="feed-card ${statusClass}">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-2">
                <h2 class="feed-title">${escapeHTML(report.title)}</h2>
                <span class="feed-pill ${pillClass}">${escapeHTML(statusLabel)}</span>
            </div>

            <div class="feed-meta-row">
                <div class="feed-meta">
                    <i class="bi bi-tags"></i>
                    <span>${escapeHTML(categoryLabel)}</span>
                </div>
                <div class="feed-meta">
                    <i class="bi bi-person"></i>
                    <span>${escapeHTML(report.reporter)}</span>
                </div>
            </div>

            <p class="feed-description">${escapeHTML(report.description)}</p>

            <div class="feed-location">
                <i class="bi bi-geo-alt"></i>
                <span>${escapeHTML(report.location)}</span>
            </div>

            <div class="feed-progress-label">
                <span>Progress: ${progress}%</span>
                <span>${escapeHTML(statusLabel)}</span>
            </div>
            <div class="feed-progress-track" aria-label="Progress status laporan">
                <div
                    class="feed-progress-fill"
                    style="width: ${progress}%"
                    role="progressbar"
                    aria-valuenow="${progress}"
                    aria-valuemin="0"
                    aria-valuemax="100"></div>
            </div>
        </article>
    `;
}

function getFeedStatusClass(status) {
    const statusClasses = {
        REPORTED: "feed-pill-reported",
        VERIFIED: "feed-pill-verified",
        IN_PROGRESS: "feed-pill-progress",
        RESOLVED: "feed-pill-resolved"
    };

    return statusClasses[status] || "feed-pill-reported";
}

function getStatusClass(status) {
    const statusClasses = {
        DRAFT: "status-draft",
        REPORTED: "status-reported",
        VERIFIED: "status-verified",
        IN_PROGRESS: "status-in-progress",
        RESOLVED: "status-resolved"
    };

    return statusClasses[status] || "status-reported";
}

function formatReportDate(value) {
    if (!value) return "Baru saja";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Baru saja";
    }

    return date.toLocaleDateString("id-ID", {
        day: "2-digit",
        month: "short"
    });
}

function getAnnouncementConfig(status) {
    const configs = {
        REPORTED: {
            icon: "bi-clipboard-check",
            tone: "reported",
            message: "Laporan baru diterima dan menunggu proses verifikasi petugas."
        },
        VERIFIED: {
            icon: "bi-shield-check",
            tone: "verified",
            message: "Laporan sudah diverifikasi dan siap diteruskan ke unit terkait."
        },
        IN_PROGRESS: {
            icon: "bi-tools",
            tone: "progressing",
            message: "Penanganan laporan sedang berjalan oleh petugas terkait."
        },
        RESOLVED: {
            icon: "bi-check-circle",
            tone: "resolved",
            message: "Laporan telah diselesaikan dan masuk arsip pengumuman kota."
        },
        DRAFT: {
            icon: "bi-file-earmark-text",
            tone: "reported",
            message: "Draft laporan belum diajukan ke sistem pelaporan kota."
        }
    };

    return configs[status] || configs.REPORTED;
}

function renderAnnouncements(reports) {
    const list = document.getElementById("announcementList");
    const count = document.getElementById("announcementCount");

    if (!list) return;

    const visibleReports = reports.slice(0, 5);

    if (count) {
        count.textContent = visibleReports.length;
    }

    if (!visibleReports.length) {
        list.innerHTML = `
            <div class="announcement-empty">
                <div>
                    <i class="bi bi-inbox d-block fs-4 mb-2"></i>
                    Belum ada pengumuman laporan.
                </div>
            </div>
        `;
        return;
    }

    list.innerHTML = visibleReports.map((report) => {
        const statusLabel = statusLabels[report.status] || report.status;
        const categoryLabel = categoryLabels[report.category] || report.category;
        const config = getAnnouncementConfig(report.status);
        const date = formatReportDate(report.updated_at || report.created_at);

        return `
            <article class="announcement-row ${config.tone}">
                <div class="announcement-icon">
                    <i class="bi ${config.icon}"></i>
                </div>
                <div>
                    <h3 class="announcement-row-title">${escapeHTML(report.title)}</h3>
                    <p class="announcement-desc">${escapeHTML(config.message)}</p>
                    <div class="announcement-meta">
                        <span class="announcement-badge">${escapeHTML(statusLabel)}</span>
                        <span>${escapeHTML(categoryLabel)}</span>
                        <span>${escapeHTML(date)}</span>
                    </div>
                </div>
            </article>
        `;
    }).join("");
}

async function loadAnnouncements() {
    const list = document.getElementById("announcementList");
    const count = document.getElementById("announcementCount");

    if (!list) return;

    list.innerHTML = `
        <div class="announcement-empty">
            <div>
                <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
                <div>Memuat pengumuman laporan...</div>
            </div>
        </div>
    `;

    if (count) {
        count.textContent = "0";
    }

    try {
        const response = await requestAPI("/api/reports/?tab=feed&page_size=5");
        const data = await response.json();

        if (!response.ok) {
            throw new Error("Gagal memuat pengumuman.");
        }

        const feedReports = getResultsFromResponse(data);

        if (feedReports.length) {
            renderAnnouncements(feedReports);
            return;
        }

        const fallbackResponse = await requestAPI("/api/reports/?tab=my_reports&page_size=5");
        const fallbackData = await fallbackResponse.json();

        if (!fallbackResponse.ok) {
            throw new Error("Gagal memuat pengumuman.");
        }

        renderAnnouncements(getResultsFromResponse(fallbackData));
    } catch (error) {
        list.innerHTML = `
            <div class="announcement-empty">
                <div>
                    <i class="bi bi-exclamation-triangle d-block fs-4 mb-2"></i>
                    ${escapeHTML(error.message)}
                </div>
            </div>
        `;
    }
}

function renderPagination(data, page) {
    const pagination = document.getElementById("paginationBar");
    const totalPages = getPageCount(data);

    if (totalPages <= 1) {
        pagination.innerHTML = "";
        return;
    }

    const pages = getVisiblePages(page, totalPages);
    const buttons = [
        paginationButton(
            "Sebelumnya",
            page - 1,
            false,
            page === 1,
            "nav"
        )
    ];

    pages.forEach((item) => {
        if (item === "...") {
            buttons.push('<span class="pagination-ellipsis">...</span>');
            return;
        }

        buttons.push(
            paginationButton(
                item,
                item,
                item === page,
                false
            )
        );
    });

    buttons.push(
        paginationButton(
            "Berikutnya",
            page + 1,
            false,
            page === totalPages,
            "nav"
        )
    );

    pagination.innerHTML = buttons.join("");
}

function paginationButton(label, targetPage, isActive = false, disabled = false, extraClass = "") {
    const disabledAttribute = disabled ? "disabled" : "";
    const activeClass = isActive ? "active" : "";
    const clickHandler = disabled
        ? ""
        : `onclick="loadDashboardData('${currentDashboardTab}', ${targetPage})"`;

    return `
        <button
            type="button"
            class="pagination-button ${activeClass} ${extraClass}"
            ${disabledAttribute}
            ${clickHandler}>
            ${label}
        </button>
    `;
}

function getVisiblePages(currentPage, totalPages) {
    if (totalPages <= 7) {
        return Array.from({ length: totalPages }, (_, index) => index + 1);
    }

    const pages = new Set([
        1,
        2,
        currentPage - 1,
        currentPage,
        currentPage + 1,
        totalPages - 1,
        totalPages
    ]);

    const sortedPages = Array.from(pages)
        .filter((item) => item >= 1 && item <= totalPages)
        .sort((a, b) => a - b);

    return sortedPages.reduce((items, item, index) => {
        if (index > 0 && item - sortedPages[index - 1] > 1) {
            items.push("...");
        }

        items.push(item);
        return items;
    }, []);
}

async function loadSummaryStats() {
    const response = await requestAPI("/api/reports/?tab=my_reports&page_size=1000");
    const data = await response.json();

    if (!response.ok) {
        throw new Error("Gagal memuat rekap status.");
    }

    const reports = getResultsFromResponse(data);
    const statusCounts = {
        DRAFT: 0,
        REPORTED: 0,
        VERIFIED: 0,
        IN_PROGRESS: 0,
        RESOLVED: 0
    };

    reports.forEach((report) => {
        if (Object.prototype.hasOwnProperty.call(statusCounts, report.status)) {
            statusCounts[report.status] += 1;
        }
    });

    document.getElementById("draftCount").textContent = statusCounts.DRAFT;
    document.getElementById("reportedCount").textContent = statusCounts.REPORTED;
    document.getElementById("verifiedCount").textContent = statusCounts.VERIFIED;
    document.getElementById("inProgressCount").textContent = statusCounts.IN_PROGRESS;
    document.getElementById("resolvedCount").textContent = statusCounts.RESOLVED;
}

async function loadDashboardData(tab = currentDashboardTab, page = 1) {
    currentDashboardTab = tab;
    currentDashboardPage = page;

    document.querySelectorAll(".dashboard-tab").forEach((button) => {
        button.classList.toggle("active", button.dataset.tab === tab);
    });

    document.querySelectorAll("[data-nav-tab]").forEach((link) => {
        link.classList.toggle("active", link.dataset.navTab === tab);
    });

    const list = document.getElementById("reportList");
    list.innerHTML = `
        <div class="portal-card empty-list">
            <div>
                <div class="spinner-border text-primary mb-3" role="status"></div>
                <p class="mb-0">Memuat data laporan...</p>
            </div>
        </div>
    `;

    try {
        const response = await requestAPI(`/api/reports/?tab=${tab}&page=${page}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error("Gagal memuat data laporan.");
        }

        renderList(getResultsFromResponse(data), tab);
        renderPagination(data, page);
        await loadSummaryStats();
        await loadAnnouncements();
    } catch (error) {
        list.innerHTML = `
            <div class="portal-card empty-list">
                <div>
                    <i class="bi bi-exclamation-triangle fs-1 d-block mb-2"></i>
                    <p class="mb-0">${escapeHTML(error.message)}</p>
                </div>
            </div>
        `;
    }
}

async function editDraft(id) {
    try {
        const response = await requestAPI(`/api/reports/${id}/`);
        const report = await response.json();

        if (!response.ok) {
            throw new Error(report.detail || "Draft tidak dapat dimuat.");
        }

        openReportModal(report);
    } catch (error) {
        alert(error.message);
    }
}

function initializeDashboard() {
    setupReportModalEvents();

    const newReportButton = document.getElementById("newReportButton");

    if (newReportButton) {
        newReportButton.addEventListener("click", function () {
            openReportModal();
        });
    }

    document.querySelectorAll(".dashboard-tab").forEach((button) => {
        button.addEventListener("click", function () {
            loadDashboardData(button.dataset.tab, 1);
        });
    });

    document.querySelectorAll("[data-nav-tab]").forEach((link) => {
        if (link.dataset.bound === "true") return;

        link.dataset.bound = "true";

        link.addEventListener("click", function () {
            loadDashboardData(link.dataset.navTab, 1);
        });
    });

    loadDashboardData(currentDashboardTab, currentDashboardPage);
}
