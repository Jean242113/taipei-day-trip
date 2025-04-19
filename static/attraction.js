document.addEventListener('DOMContentLoaded', () => {
    // 取得景點 ID (從 URL 取得)
    const attractionId = getAttractionIdFromUrl();

    // 取得 HTML 元素
    const imgContainer = document.querySelector('.img-container');
    const circleContainer = document.querySelector('.circle-container');
    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');
    const infors = document.querySelector('.infors');

    // 目前顯示的圖片索引
    let currentImageIndex = 0;
    let price = 0; // 預設價格

    function handleHalfDateChange() {
        const selectedValue = getSelectedHalfDate(); // 使用前面提供的 getSelectedHalfDate 函式
        if (selectedValue) {
            price = selectedValue === 'morning' ? 2000 : 2500;
            renderPrice(price);
        }
    }

    function getSelectedHalfDate() {
        const radioButtons = document.getElementsByName('half-date');
        for (let i = 0; i < radioButtons.length; i++) {
            if (radioButtons[i].checked) {
                return radioButtons[i].value;
            }
        }
        return null;
    }

    // 1. 渲染景點資訊和預定表單
    function renderAttractionDetails(data) {
        // 渲染預定表單 (範例)

        // 渲染景點名稱和描述 (範例)
        const attractionName = document.getElementsByClassName('attraction-title')[0].children;
        attractionName[0].textContent = data.name;
        attractionName[1].textContent = data.category + ' at ' + data.mrt;

        document.getElementById("date").addEventListener('change', () => {
            const selectedValue = getSelectedHalfDate();
            price = selectedValue === 'morning' ? 2000 : 2500;
            renderPrice(price);
        });

        const radioButtons = document.getElementsByName('half-date');
        radioButtons.forEach(radioButton => {
            radioButton.addEventListener('change', handleHalfDateChange);
        });
    }

    function renderPrice(price) {
        const priceDisplay = document.getElementById('priceDisplay');
        priceDisplay.textContent = `新台幣 ${price} 元`;
    }

    // 2. 渲染圖片輪播
    function renderImageSlideshow(images) {
        // 渲染第一張圖片
        imgContainer.innerHTML = `<img src="${images[currentImageIndex]}" alt="景點圖片">`;

        // 動態產生小圓圈
        circleContainer.innerHTML = images.map((_, index) =>
            `<button class="circle ${index === currentImageIndex ? 'active' : ''}" data-index="${index}"></button>`
        ).join('');

        // 處理小圓圈點擊事件
        circleContainer.querySelectorAll('.circle').forEach(circle => {
            circle.addEventListener('click', () => {
                currentImageIndex = parseInt(circle.dataset.index);
                renderImageSlideshow(images);
            });
        });
    }

    // 3. 處理箭頭點擊事件
    leftArrow.addEventListener('click', () => {
        currentImageIndex = (currentImageIndex - 1 + attractionData.images.length) % attractionData.images.length;
        renderImageSlideshow(attractionData.images);
    });

    rightArrow.addEventListener('click', () => {
        currentImageIndex = (currentImageIndex + 1) % attractionData.images.length;
        renderImageSlideshow(attractionData.images);
    });

    // 4. 渲染景點詳細資訊
    function renderAttractionInfo(data) {

        const attractionDescription = document.createElement('p');
        attractionDescription.textContent = data.description;
        attractionDescription.classList.add('attdescription');
        infors.appendChild(attractionDescription);

        // 渲染景點地址、分類、交通方式 (範例)
        const attractionAddressTitle = document.createElement('p');
        attractionAddressTitle.textContent = `景點地址：`
        attractionAddressTitle.classList.add('address-title');
        infors.appendChild(attractionAddressTitle);

        const attractionAddress = document.createElement('p');
        attractionAddress.textContent = `${data.address}`
        attractionAddress.classList.add('address');
        infors.appendChild(attractionAddress);

        const attractionTransportTitle = document.createElement('p');
        attractionTransportTitle.textContent = `交通方式：`;
        attractionTransportTitle.classList.add('transport-title');
        infors.appendChild(attractionTransportTitle);


        const attractionTransport = document.createElement('p');
        attractionTransport.textContent = `${data.transport}`;
        attractionTransport.classList.add('transport');
        infors.appendChild(attractionTransport);
    }

    // 5. 從 URL 取得景點 ID
    function getAttractionIdFromUrl() {
        const pathSegments = window.location.pathname.split('/');
        return parseInt(pathSegments[pathSegments.length - 1]);
    }

    // 6. 串接 API 取得景點資料
    let attractionData; // 宣告 attractionData 變數
    function fetchAttractionData(attractionId) {
        return fetch(`/api/attraction/${attractionId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.data) {
                    attractionData = data.data; // 將 API 回傳的資料存到 attractionData 變數
                    return data.data;
                } else {
                    throw new Error('API 回傳資料格式錯誤');
                }
            });
    }

    function addBookingInit() {
        const bookingButton = document.getElementById('bookingButton');
        bookingButton.addEventListener('click', () => {
            const date = document.getElementById('date').value;
            const time = getSelectedHalfDate();
            const priceDisplay = document.getElementById('priceDisplay').textContent;
            const price = parseInt(priceDisplay.replace(/\D/g, '')); // 取得價格

            // 在這裡處理預定邏輯，例如發送請求到後端
            console.log(`預定日期: ${date}, 時段: ${time}, 價格: ${price}`);
            fetch('/api/booking', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}` // 使用 token 認證
                },
                body: JSON.stringify({
                    attractionId: attractionId,
                    date: date,
                    time: time,
                    price: price
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.attractionId) {
                        // alert('預定成功！');
                        window.location.href = '/booking'; // 預定成功後導向預定頁面
                    } else {
                        // document.getElementById("login").click(); // 顯示登入頁面
                        localStorage.setItem('login', 'true'); // 設定登入狀態
                        window.location.href = '/';
                    }
                })
                .catch(error => console.error('預定請求失敗:', error));
        });
    }

    // 頁面載入後執行
    fetchAttractionData(attractionId)
        .then(data => {
            renderAttractionDetails(data);
            renderImageSlideshow(data.images);
            renderAttractionInfo(data);
        })
        .catch(error => {
            console.error('API 請求失敗:', error);
            // 處理錯誤情況，例如顯示錯誤訊息
        });

    addLoginInit(); // 初始化登入功能
    addBookingInit(); // 初始化預定功能
});