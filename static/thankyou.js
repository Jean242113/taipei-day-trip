document.addEventListener('DOMContentLoaded', () => {
    addLoginInit();
    addthankyouInit();


    if (localStorage.getItem('token') == null) {
        window.location.href = "/"; // 導向首頁
    }
    const urlParams = new URLSearchParams(window.location.search);
    const number = urlParams.get('number');
    document.getElementById("number").innerText = number;
}
)
async function addthankyouInit() {
    fetch("/api/order/" + number, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}` // 使用 token 認證
        }
    })
        .then(response => response.json())
        .then(data => {
            const attraction_image = document.getElementsByClassName("bookingpicture-container")[0].lastElementChild;
            attraction_image.src = data.data.trip.attraction.image;
            const attraction_name = document.getElementById("frame1").lastElementChild;
            attraction_name.innerHTML = "台北一日遊：" + data.data.trip.attraction.name;
            const date = document.getElementById("frame2").lastElementChild;
            date.innerHTML = data.data.trip.date;
            const time = document.getElementById("frame3").lastElementChild;
            time.innerHTML = (data.data.time == "morning" ? "早上 9 點到下午 12 點" : "下午 1 點到晚上 6 點");
            const price = document.getElementById("frame4").lastElementChild;
            price.innerHTML = "新台幣 " + data.data.price + " 元";
            const address = document.getElementById("frame5").lastElementChild;
            address.innerHTML = data.data.trip.attraction.address;


            const name = document.getElementById("name");
            name.innerHTML = data.data.contact.name; // 使用者名稱
            const email = document.getElementById("email");
            email.innerHTML = data.data.contact.email;  // 使用者電子郵件
            const phone = document.getElementById("phone");
            phone.innerHTML = data.data.contact.phone;  // 使用者電子郵件
        })


        .catch(error => console.error("Error loading booking page:", error))
}


