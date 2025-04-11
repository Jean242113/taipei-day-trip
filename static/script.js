let currentIndex = 0;
let currentPage = 0;
let nextPage = 1;
let currentObserveElenment = null;

async function fetchStations() {
    try {
        const response = await fetch("/api/mrts");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.data;
    } catch (error) {
        console.error("Error fetching stations:", error);
        return [];
    }
}

async function fetchAttractions(page = 0, keyword = null, mrt = null) {
    try {
        const url = new URL("/api/attractions", window.location.origin);
        url.searchParams.append("page", page);
        if (keyword) url.searchParams.append("keyword", keyword);
        if (mrt) url.searchParams.append("mrt", mrt);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        nextPage = data.nextPage;
        return data.data;
    } catch (error) {
        console.error("Error fetching attractions:", error);
        throw error;
    }
}


// 自動載入更多資料
const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && nextPage !== null) {
        if (currentObserveElenment !== null) {
            observer.unobserve(currentObserveElenment); // 移除舊的觀察目標
        }
        currentPage = nextPage;
        displayAttractions(currentPage, document.getElementById("search-input").value);
    }
}, {
    rootMargin: "50% 80% 0% 0%", // 觀察範圍
    threshold: 1.0
});

async function displayAttractions(page = 0, keyword = null, mrt = null) {
    try {
        const attractions = await fetchAttractions(page, keyword, mrt);
        const attractionsGroup = document.querySelector(".attractions-group");
        if (page === 0) {
            attractionsGroup.innerHTML = "";
        }

        attractions.forEach(attraction => {
            const attractionLink = document.createElement("a");
            attractionLink.href = `/attraction/${attraction.id}`; // 設定超連結目標
            attractionLink.classList.add("attraction-link");

            const attractionDiv = document.createElement("div");
            attractionDiv.classList.add("attraction");

            // 新增 attraction-container div
            const containerDiv = document.createElement("div");
            containerDiv.classList.add("attraction-container");
            attractionDiv.appendChild(containerDiv);

            const detailsDiv = document.createElement("div");
            detailsDiv.classList.add("attraction-details");
            if (attraction.mrt == null) {
                attraction.mrt = "";
            }
            detailsDiv.innerHTML = `<p>${attraction.mrt}</p><p>${attraction.category}</p>`;
            attractionDiv.appendChild(detailsDiv);


            const img = document.createElement("img");
            img.src = attraction.images[0];
            containerDiv.appendChild(img);

            const name = document.createElement("div");
            name.classList.add("attraction-name");
            const info = document.createElement("label");
            info.textContent = attraction.name;
            name.appendChild(info);
            containerDiv.appendChild(name);

            attractionLink.appendChild(attractionDiv);
            attractionsGroup.appendChild(attractionLink);
        });

        if (attractionsGroup.lastElementChild) {
            currentObserveElenment = attractionsGroup.lastElementChild;
            observer.observe(currentObserveElenment); // 觀察新的最後一個子元素
        }
    } catch (error) {
        console.error("Error displaying attractions:", error);
    }
}

async function init() {
    const stationsContainer = document.querySelector(".stations");
    const searchInput = document.getElementById("search-input");
    const searchButton = document.getElementById("search-button");

    await displayAttractions(currentPage);
    const stations = await fetchStations();

    stations.forEach(station => {
        const stationElement = document.createElement("div");
        stationElement.classList.add("station");
        stationElement.textContent = station;
        stationElement.addEventListener("click", () => {
            searchInput.value = station;
            currentPage = 0;
            displayAttractions(currentPage, station);
        });
        stationsContainer.appendChild(stationElement);
    });

    // 箭頭滾動
    document.querySelector(".left-arrow").addEventListener("click", () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateStationsPosition();
        }
    });

    document.querySelector(".right-arrow").addEventListener("click", () => {
        // 檢查是否已到達最右邊
        if (!isAtRightEnd()) {
            currentIndex++;
            updateStationsPosition();
        }
    });

    function updateStationsPosition() {
        const stationWidth = document.querySelector(".station").offsetWidth;
        stationsContainer.style.transform = `translateX(-${currentIndex * stationWidth}px)`;
    }

    // 檢查是否已到達最右邊
    function isAtRightEnd() {
        const stationWidth = document.querySelector(".station").offsetWidth;
        const containerWidth = stationsContainer.offsetWidth;
        const totalWidth = stations.length * stationWidth;
        const visibleWidth = containerWidth;
        const scrolledWidth = currentIndex * stationWidth;

        return scrolledWidth + visibleWidth >= totalWidth;
    }

    // 搜尋事件
    searchButton.addEventListener("click", () => {
        const keyword = searchInput.value;
        currentPage = 0;
        displayAttractions(currentPage, keyword);
    });

    addLoginInit();
}

init();