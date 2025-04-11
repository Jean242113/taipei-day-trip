async function addLoginInit() {
    await checkLoginStatus()

    if (isUserLoggedIn()) {
        document.getElementById("login").innerHTML = "登出系統";
    } else {
        document.getElementById("login").innerHTML = "登入 / 註冊";
    }

    document.getElementById("login").addEventListener("click", () => {
        if (document.getElementById("login").innerHTML === "登出系統") {
            logout();
            return;
        }
        // 載入登入頁面
        fetch("/static/login.html", {
            method: "GET",
            headers: {
                "Content-Type": "text/html"
            }
        })
            .then(response => response.text())
            .then(html => {
                document.getElementsByClassName("login-container")[0].innerHTML = html;
                document.getElementsByClassName("login-container")[0].style.display = "block";
                document.getElementById('username-group').style.display = 'none';

                const loginContainer = document.getElementsByClassName('login-container')[0];
                const closeButton = loginContainer.querySelector('.close-button');
                if (closeButton) {
                    closeButton.addEventListener('click', closeModal);
                }

                const registerLink = document.getElementById('footer-link');
                if (registerLink) {
                    registerLink.addEventListener('click', showRegisterForm);
                }

                const loginButton = document.getElementById('login-button');
                if (loginButton) {
                    loginButton.addEventListener('click', loginButtonClick);
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
        document.getElementById("login-message").style.display = "none"; // Hide the message when switching forms
        if (document.getElementById('username-group').style.display == 'none') {
            // 實作顯示註冊表單的邏輯
            document.getElementById('username-group').style.display = 'block';
            document.getElementsByClassName('login-form-main')[0].firstChild.innerHTML = '註冊會員帳號';
            document.getElementById('login-button').innerHTML = '註冊新會員';
            document.getElementById('footer-info').innerHTML = '已經有帳戶了？';
            document.getElementById('footer-link').innerHTML = '點此登入';
            return;
        }
        //實作顯示登入表單的邏輯
        document.getElementById('username-group').style.display = 'none';
        document.getElementsByClassName('login-form-main')[0].firstChild.innerHTML = '登入會員帳號';
        document.getElementById('login-button').innerHTML = '登入帳戶';
        document.getElementById('footer-info').innerHTML = '還沒有帳戶？';
        document.getElementById('footer-link').innerHTML = '點此註冊';
    }

    function loginButtonClick() {
        const loginButton = document.getElementById('login-button');
        if (loginButton.innerHTML === '登入帳戶') {
            login();
        } else {
            register();
        }
    }

    function login() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const loginButton = document.getElementById('login-button');
        loginButton.disabled = true; // Disable the button to prevent multiple clicks

        fetch("/api/user/auth", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        })
            .then(response => response.json())
            .then(data => {
                if (data.token) {
                    localStorage.setItem("token", data.token); // Store the token in local storage
                    window.location.reload(); // Reload the page on successful login
                } else {
                    const loginMessage = document.getElementById("login-message");
                    loginMessage.innerHTML = data.message;
                    loginMessage.style.color = "red"; // Change the color of the message to red
                    loginMessage.style.display = "block"; // Show the message
                }
            })
            .catch(error => console.error("Error during login:", error))
            .finally(() => {
                loginButton.disabled = false; // Re-enable the button after the request is complete
            });
    }

    function register() {
        const name = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const loginButton = document.getElementById('login-button');
        loginButton.disabled = true; // Disable the button to prevent multiple clicks

        fetch("/api/user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, email, password })
        })
            .then(response => response.json())
            .then(data => {
                const loginMessage = document.getElementById("login-message");
                loginMessage.innerHTML = data.message;
                loginMessage.style.display = "block"; // Show the message
                if (data.ok) {
                    loginMessage.style.color = "green"; // Change the color of the message to green
                } else {
                    loginMessage.style.color = "red"; // Change the color of the message to red
                }
            })
            .catch(error => console.error("Error during registration:", error))
            .finally(() => {
                loginButton.disabled = false; // Re-enable the button after the request is complete
            });
    }
}

function isUserLoggedIn() {
    const token = localStorage.getItem("token");
    return token !== null && token !== undefined && token !== "undefined" && token !== "null";
}

function logout() {
    localStorage.removeItem("token"); // Remove the token from local storage
    window.location.reload(); // Reload the page after logout
}

async function checkLoginStatus() {
    const token = localStorage.getItem("token");
    if (token) {
        fetch("/api/user/auth", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.log("User is not logged in:", data.message);
                    localStorage.removeItem("token");
                }
            })
            .catch(error => console.error("Error checking login status:", error));
    }
}