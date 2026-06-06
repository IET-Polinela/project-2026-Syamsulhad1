function setupLoginForm() {

    const form = document.getElementById("loginForm");

    if (!form) return;

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        const submitButton = form.querySelector("button[type='submit']");

        const username =
            document.getElementById("loginUsername").value.trim();

        const password =
            document.getElementById("loginPassword").value;

        submitButton.disabled = true;

        try {
            const response = await requestAPI(
                "/api/token/",
                "POST",
                {
                    username,
                    password
                }
            );

            const data = await response.json();

            if (response.status === 200) {
                localStorage.setItem(
                    "access_token",
                    data.access
                );

                localStorage.setItem(
                    "refresh_token",
                    data.refresh
                );

                alert("Login berhasil!");

                window.location.hash = "#dashboard";
            } else {
                alert("Login gagal. Periksa username dan password.");
            }
        } catch (error) {
            alert("Tidak dapat menghubungi server API.");
        } finally {
            submitButton.disabled = false;
        }

    });
}
