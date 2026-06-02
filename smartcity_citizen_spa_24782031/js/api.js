const API_BASE_URL = "http://127.0.0.1:8000";

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

    return await fetch(
        `${API_BASE_URL}${endpoint}`,
        options
    );
}