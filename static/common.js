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
        console.log('showRegisterForm called');
        if (document.getElementById('username-group').style.display == 'none') {
            // 實作顯示註冊表單的邏輯
            document.getElementsByClassName('modal-content')[0].style.height = '332px';
            document.getElementById('username-group').style.display = 'block';
            document.getElementsByClassName('login-form-main')[0].firstChild.innerHTML = '註冊會員帳號';
            document.getElementById('login-button').innerHTML = '註冊新會員';
            document.getElementById('footer-info').innerHTML = '已經有帳戶了？';
            document.getElementById('footer-link').innerHTML = '點此登入';
            return;
        }
        //實作顯示登入表單的邏輯
        document.getElementsByClassName('modal-content')[0].style.height = '275px';
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

        fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload(); // Reload the page on successful login
                } else {
                    alert("Login failed: " + data.message);
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
                if (data.ok) {
                    alert("註冊成功"); // Reload the page on successful registration
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error("Error during registration:", error))
            .finally(() => {
                loginButton.disabled = false; // Re-enable the button after the request is complete
            });
    }
}