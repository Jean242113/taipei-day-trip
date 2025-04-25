document.addEventListener('DOMContentLoaded', () => {
    addLoginInit();
    addBookingInit();
    creditCard();

    if (localStorage.getItem('token') == null) {
        window.location.href = "/"; // 導向首頁
    }

    document.getElementById("empty-container").style.display = "none"; // 隱藏空的預定行程區域
    document.getElementById("booking-container").style.display = "none"; // 隱藏預定行程區域

    document.getElementsByClassName("delete-button")[0].addEventListener("click", () => {
        const confirmDelete = confirm("確定要取消預定嗎？");
        if (confirmDelete) {
            deleteBooking();
        }
    });
});

async function addBookingInit() {
    fetch("/api/booking", {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}` // 使用 token 認證
        }
    })
        .then(response => response.json())
        .then(data => {
            const hello = document.getElementsByClassName("headline")[0].lastElementChild;
            hello.innerHTML = `您好，${localStorage.getItem('name')}，待預訂的行程如下：`;
            if (data.data == null) {
                document.getElementById("empty-container").style.display = "block"; // 隱藏空的預定行程區域
                document.getElementById("booking-container").style.display = "none"; // 隱藏預定行程區域
                localStorage.removeItem('order_id'); // 移除訂單 ID
            } else {
                document.getElementById("empty-container").style.display = "none"; // 隱藏空的預定行程區域
                document.getElementById("booking-container").style.display = "block"; // 顯示預定行程區域

                localStorage.setItem('attraction_id', data.data.attraction.id);
                const attraction_image = document.getElementsByClassName("bookingpicture-container")[0].lastElementChild;
                attraction_image.src = data.data.attraction.image;
                const attraction_name = document.getElementById("frame1").lastElementChild;
                attraction_name.innerHTML = "台北一日遊：" + data.data.attraction.name;
                const date = document.getElementById("frame2").lastElementChild;
                date.innerHTML = data.data.date;
                const time = document.getElementById("frame3").lastElementChild;
                time.innerHTML = (data.data.time == "morning" ? "早上 9 點到下午 12 點" : "下午 1 點到晚上 6 點");
                const price = document.getElementById("frame4").lastElementChild;
                price.innerHTML = "新台幣 " + data.data.price + " 元";
                const address = document.getElementById("frame5").lastElementChild;
                address.innerHTML = data.data.attraction.address;
                const total_price = document.getElementsByClassName("confirm-title")[0].lastElementChild;
                total_price.innerHTML = "新台幣 " + data.data.price + " 元";

                const name = document.getElementById("name");
                name.value = localStorage.getItem('name'); // 使用者名稱
                const email = document.getElementById("email");
                email.value = localStorage.getItem('email'); // 使用者電子郵件
            }

        })
        .catch(error => console.error("Error loading booking page:", error))

}

function deleteBooking() {
    fetch("/api/booking", {
        method: "DELETE",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}` // 使用 token 認證
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.ok) {
                window.location.href = "/booking"; // 預定成功後導向預定頁面
            } else {
                alert('取消預定失敗: ' + data.message);
            }
        })
        .catch(error => console.error('取消預定請求失敗:', error));
}

function creditCard() {
    TPDirect.setupSDK(160139, 'app_uZ8YPqUn2Ot3O5flyagXYGaouQiowIHVbeeEfQhC0RgIb4WjvMZO5edN266r', 'sandbox');
    let fields = {
        number: {
            // css selector
            element: '#card-number',
            placeholder: '**** **** **** ****'
        },
        expirationDate: {
            // DOM object
            element: document.getElementById('card-expiration-date'),
            placeholder: 'MM / YY'
        },
        ccv: {
            element: '#card-ccv',
            placeholder: 'ccv'
        }
    };
    TPDirect.card.setup({
        fields: fields,
        styles: {
            // Style all elements
            'input': {
                'color': 'gray'
            },
            // Styling ccv field
            'input.ccv': {
                // 'font-size': '16px'
            },
            // Styling expiration-date field
            'input.expiration-date': {
                // 'font-size': '16px'
            },
            // Styling card-number field
            'input.card-number': {
                // 'font-size': '16px'
            },
            // style focus state
            ':focus': {
                // 'color': 'black'
            },
            // style valid state
            '.valid': {
                'color': 'green'
            },
            // style invalid state
            '.invalid': {
                'color': 'red'
            },
            // Media queries
            // Note that these apply to the iframe, not the root window.
            '@media screen and (max-width: 400px)': {
                'input': {
                    'color': 'orange'
                }
            }
        }
    });

    creditCardOnUpdate();

    const confirmButton = document.getElementById('confirm-button');
    confirmButton.addEventListener('click', function () {
        // creditCardOnUpdate();
        confirmButton.disabled = true; // 禁用按鈕，避免重複點擊
        TPDirect.card.getPrime(function (result) {
            if (result.status !== 0) {
                console.log('getPrime error' + result.msg);
                confirmButton.disabled = false; // 問題發生時重新啟用按鈕
                return;
            }
            var prime = result.card.prime
            fetch("/api/orders", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}` // 使用 token 認證
                },
                body: JSON.stringify({
                    prime: prime,
                    order: {
                        price: parseInt(document.getElementsByClassName("confirm-title")[0].lastElementChild.innerHTML.replace(/[^0-9]/g, '')),
                        trip: {
                            attraction: {
                                id: localStorage.getItem('attraction_id'),
                                name: document.getElementById("frame1").lastElementChild.innerHTML.replace("台北一日遊：", ""),
                                address: document.getElementById("frame5").lastElementChild.innerHTML,
                                image: document.getElementsByClassName("bookingpicture-container")[0].lastElementChild.src
                            },
                            date: document.getElementById("frame2").lastElementChild.innerHTML,
                            time: (document.getElementById("frame3").lastElementChild.innerHTML == "早上 9 點到下午 12 點" ? "morning" : "afternoon")
                        }
                    },
                    contact: {
                        name: document.getElementById("name").value,
                        email: document.getElementById("email").value,
                        phone: document.getElementById("phone").value
                    }
                })
            })
                .then(response => response.json())
                .then(data => {
                    confirmButton.disabled = false;
                    if (data.data != null) {
                        window.location.href = "/thankyou?number=" + data.data.number; // 預定成功後導向預定頁面
                    } else {
                        alert('預定失敗: ' + data.message);
                    }
                })
        });
    });
}

function creditCardOnUpdate() {
    const confirmButton = document.getElementById('confirm-button');
    TPDirect.card.onUpdate(function (update) {
        // update.canGetPrime === true
        // --> you can call TPDirect.card.getPrime()
        if (update.canGetPrime) {
            // Enable submit Button to get prime.
            confirmButton.disabled = false;
        } else {
            // Disable submit Button to get prime.
            confirmButton.disabled = true;
        }

        // cardTypes = ['mastercard', 'visa', 'jcb', 'amex', 'unknown']
        if (update.cardType === 'visa') {
            // Handle card type visa.
        }

        // number fields is error
        if (update.status.number === 2) {
            // setNumberFormGroupToError()
        } else if (update.status.number === 0) {
            // setNumberFormGroupToSuccess()
        } else {
            // setNumberFormGroupToNormal()
        }

        if (update.status.expiry === 2) {
            // setNumberFormGroupToError()
        } else if (update.status.expiry === 0) {
            // setNumberFormGroupToSuccess()
        } else {
            // setNumberFormGroupToNormal()
        }

        if (update.status.ccv === 2) {
            // setNumberFormGroupToError()
        } else if (update.status.ccv === 0) {
            // setNumberFormGroupToSuccess()
        } else {
            // setNumberFormGroupToNormal()
        }
    });
}
