function addLoginInit() {
    document.getElementById("login").addEventListener("click", () => {
        fetch("/static/login.html", {
            method: "GET",
            headers: {
                "Content-Type": "text/html"
            }
        })
            .then(response => response.text())
            .then(html => {
                // console.log(html);
                document.getElementsByClassName("login-container")[0].innerHTML = html;
                document.getElementsByClassName("login-container")[0].style.display = "block";

                // const loginRegisterButton = document.querySelector('.login-register-button'); // 假設你的登入/註冊按鈕有這個 class
                const loginContainer = document.getElementsByClassName('login-container')[0];
                const closeButton = loginContainer.querySelector('.close-button');
                if (closeButton) {
                    closeButton.addEventListener('click', closeModal);
                }

                const registerLink = loginContainer.querySelector('.register-link');
                if (registerLink) {
                    registerLink.addEventListener('click', showRegisterForm);
                }

                const loginLink = loginContainer.querySelector('.login-link');
                if (loginLink) {
                    loginLink.addEventListener('click', showLoginForm);
                }
            })
            .catch(error => console.error("Error loading login page:", error));
    });

    function closeModal() {
        // 實作關閉彈出視窗的邏輯 (例如：設定 loginContainer 的 display 為 'none')
        const loginContainer = document.getElementsByClassName('login-container')[0];
        if (loginContainer) {
            loginContainer.style.display = 'none';
            loginContainer.innerHTML = ''; // 清空內容，以便下次重新載入
        }
    }

    function showRegisterForm() {
        // 實作顯示註冊表單的邏輯 (可能需要從後端請求註冊表單的 HTML，或者在後端回傳的 HTML 中包含註冊和登入兩種表單並在此切換)
        console.log('顯示註冊表單');
        // ...
    }

    function showLoginForm() {
        // 實作顯示登入表單的邏輯
        console.log('顯示登入表單');
        // ...
    }
}