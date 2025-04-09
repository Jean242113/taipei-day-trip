document.addEventListener('DOMContentLoaded', () => {
    const loginRegisterButton = document.querySelector('.login-register-button'); // 假設你的登入/註冊按鈕有這個 class
    const modalContainer = document.getElementById('modal-container'); // 用於放置彈出視窗的容器 (需要你在 HTML 中建立)

    loginRegisterButton.addEventListener('click', () => {
        fetch('/api/login-page') // 請求後端提供的登入頁面 HTML
            .then(response => response.text())
            .then(html => {
                modalContainer.innerHTML = html; // 將後端回傳的 HTML 插入到容器中

                // 在 HTML 載入後，你需要重新綁定事件監聽器，例如關閉按鈕、切換註冊/登入表單的按鈕等
                const closeButton = modalContainer.querySelector('.close-button');
                if (closeButton) {
                    closeButton.addEventListener('click', closeModal);
                }

                const registerLink = modalContainer.querySelector('.register-link');
                if (registerLink) {
                    registerLink.addEventListener('click', showRegisterForm);
                }

                const loginLink = modalContainer.querySelector('.login-link');
                if (loginLink) {
                    loginLink.addEventListener('click', showLoginForm);
                }

                // 顯示彈出視窗 (你需要自己實作這個函數，例如透過修改 CSS 的 display 屬性)
                showModal();
            })
            .catch(error => {
                console.error('Error fetching login page:', error);
                // 處理錯誤，例如顯示一個錯誤訊息
            });
    });

    function showModal() {
        // 實作顯示彈出視窗的邏輯 (例如：設定 modalContainer 的 display 為 'flex')
        if (modalContainer) {
            modalContainer.style.display = 'flex';
        }
    }

    function closeModal() {
        // 實作關閉彈出視窗的邏輯 (例如：設定 modalContainer 的 display 為 'none')
        if (modalContainer) {
            modalContainer.style.display = 'none';
            modalContainer.innerHTML = ''; // 清空內容，以便下次重新載入
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

    // ... 其他前端邏輯 (例如處理表單提交)
});