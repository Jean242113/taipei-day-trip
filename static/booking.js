document.addEventListener('DOMContentLoaded', () => {
    addLoginInit();
    addBookingInit();

    if (!isUserLoggedIn()) {
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
            } else {
                document.getElementById("empty-container").style.display = "none"; // 隱藏空的預定行程區域
                document.getElementById("booking-container").style.display = "block"; // 顯示預定行程區域

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