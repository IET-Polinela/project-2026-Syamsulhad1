const API_BASE_URL = "http://103.151.63.84:8011";

async function requestAPI(endpoint, method = "GET", bodyData = null) {

    const accessToken = localStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json"
    };

    if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`;
    }

    const options = {
        method: method,
        headers: headers
    };

    if (bodyData) {
        options.body = JSON.stringify(bodyData);
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        options
    );

    if (response.status === 401) {
        alert("Sesi Anda telah habis atau Anda belum login.");
        localStorage.clear();
        window.location.hash = "#login";
    }

    return response;
}
