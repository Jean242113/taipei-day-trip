from fastapi import *
from fastapi.responses import JSONResponse, FileResponse
import json
from collections import defaultdict

app = FastAPI()


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/index.html", media_type="text/html")


@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")


@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")


@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")


def load_data():
    with open("data/taipei-attractions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["result"]["results"]


attractions_data = load_data()


# API 端點
@app.get("/api/attractions")
def get_attractions(
    page: int = Query(0, ge=0),
    keyword: str = Query(None),
    mrt: str = Query(None),
    category: str = Query(None),
):
    try:
        limit = 12
        offset = page * limit

        filtered_attractions = []

        for attraction in attractions_data:
            if (
                keyword
                and keyword.lower() not in attraction["name"].lower()
                and attraction["MRT"]
                and keyword.lower() not in attraction["MRT"].lower()
            ):
                continue
            if mrt and attraction["MRT"] != mrt:
                continue
            if category and attraction["CAT"] != category:
                continue

            images = attraction.get("file", "").split("https://")
            valid_images = []
            for img in images:
                if len(img) > 0:
                    url = "https://" + img
                    if url.lower().endswith((".jpg", ".jpeg", ".png")):
                        valid_images.append(url)
            filtered_attractions.append(
                {
                    "id": attraction["_id"],
                    "name": attraction["name"],
                    "description": attraction["description"],
                    "address": attraction["address"],
                    "lat": attraction["latitude"],
                    "lng": attraction["longitude"],
                    "transport": attraction["direction"],
                    "mrt": attraction["MRT"],
                    "category": attraction["CAT"],
                    "images": valid_images,
                }
            )

        next_page = page + 1 if len(filtered_attractions) > offset + limit else None
        return {
            "nextPage": next_page,
            "data": filtered_attractions[offset : offset + limit],
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": str(e)})


@app.get("/api/attraction/{attractionId}")
def get_attraction(attractionId: int):
    try:
        for attraction in attractions_data:
            if attraction["_id"] == attractionId:

                images = attraction.get("file", "").split("https://")
                valid_images = []
                for img in images:
                    if len(img) > 0:
                        url = "https://" + img
                        if url.lower().endswith((".jpg", ".jpeg", ".png")):
                            valid_images.append(url)

                return {
                    "data": {
                        "id": attraction["_id"],
                        "name": attraction["name"],
                        "description": attraction["description"],
                        "address": attraction["address"],
                        "lat": attraction["latitude"],
                        "lng": attraction["longitude"],
                        "transport": attraction["direction"],
                        "mrt": attraction["MRT"],
                        "category": attraction["CAT"],
                        "images": valid_images,
                    }
                }
        raise HTTPException(status_code=404, detail="景點編號不正確")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": str(e)})


@app.get("/api/mrts")
def get_mrts():
    try:
        # 計算每個捷運站的景點數量
        mrt_counts = defaultdict(int)
        for attraction in attractions_data:
            if attraction["MRT"]:
                mrt_counts[attraction["MRT"]] += 1

        # 將捷運站和景點數量轉換為列表，並根據景點數量排序
        mrts_with_counts = [(mrt, count) for mrt, count in mrt_counts.items()]
        mrts_with_counts.sort(key=lambda x: x[1], reverse=True)

        # 提取排序後的捷運站名稱列表
        sorted_mrts = [mrt for mrt, count in mrts_with_counts]

        return {"data": sorted_mrts}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": str(e)})
