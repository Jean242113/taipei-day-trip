from fastapi import *
from fastapi.responses import JSONResponse, FileResponse
import json
from collections import defaultdict
import mysql.connector


def get_db():  # 連接資料庫
    return mysql.connector.connect(
        user="user1", password="1234", host="localhost", database="taipei"
    )


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
        mydb = get_db()
        mycursor = mydb.cursor()

        limit = 12
        offset = page * limit

        sql = """
            SELECT a.*, GROUP_CONCAT(i.url) AS images
            FROM attractions a
            LEFT JOIN images i ON a._id = i.attraction_id
            WHERE 1=1
        """
        val = []

        if keyword:
            sql += " AND (LOWER(a.name) LIKE %s OR LOWER(a.MRT) LIKE %s)"
            val.extend([f"%{keyword.lower()}%", f"%{keyword.lower()}%"])

        if mrt:
            sql += " AND a.MRT = %s"
            val.append(mrt)

        if category:
            sql += " AND a.CAT = %s"
            val.append(category)

        sql += " GROUP BY a._id LIMIT %s OFFSET %s"
        val.extend([limit, offset])

        mycursor.execute(sql, tuple(val))
        results = mycursor.fetchall()

        attractions = []
        for row in results:
            images = row[9].split(",") if row[9] else []
            attractions.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "address": row[3],
                    "lat": row[4],
                    "lng": row[5],
                    "transport": row[6],
                    "mrt": row[7],
                    "category": row[8],
                    "images": images,
                }
            )

        next_page = page + 1 if len(attractions) > limit else None
        return {
            "nextPage": next_page,
            "data": attractions,
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": str(e)})
    finally:
        if "mydb" in locals() and mydb.is_connected():
            mycursor.close()
            mydb.close()


@app.get("/api/attraction/{attractionId}")
def get_attraction(attractionId: int):
    try:
        mydb = get_db()
        mycursor = mydb.cursor()

        sql = """
            SELECT a.*, GROUP_CONCAT(i.url) AS images
            FROM attractions a
            LEFT JOIN images i ON a._id = i.attraction_id
            WHERE a._id = %s
            GROUP BY a._id
        """
        val = (attractionId,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        # print(result)

        if result:
            images = result[9].split(",") if result[9] else []
            attraction = {
                "id": result[0],
                "name": result[1],
                "description": result[2],
                "address": result[3],
                "lat": result[4],
                "lng": result[5],
                "transport": result[6],
                "mrt": result[7],
                "category": result[8],
                "images": images,
            }
            return {"data": attraction}
        else:
            raise HTTPException(status_code=404, detail="景點編號不正確")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": True, "message": str(e)})
    finally:
        if "mydb" in locals() and mydb.is_connected():
            mycursor.close()
            mydb.close()


@app.get("/api/mrts")
def get_mrts():
    try:
        # 建立資料庫連線
        conn = get_db()
        mycursor = conn.cursor()

        # SQL 查詢，計算每個捷運站的景點數量並排序
        sql = """
            SELECT MRT, COUNT(*) AS attraction_count
            FROM attractions
            WHERE MRT IS NOT NULL
            GROUP BY MRT
            ORDER BY attraction_count DESC
        """

        mycursor.execute(sql)
        results = mycursor.fetchall()

        # 提取排序後的捷運站名稱列表
        sorted_mrts = [row[0] for row in results]

        return {"data": sorted_mrts}

    except mysql.connector.Error as e:
        # 處理資料庫相關的異常
        print(f"Database Error: {e}")
        return {"error": True, "message": str(e)}

    except Exception as e:
        # 處理其他異常
        print(f"Error: {e}")
        return {"error": True, "message": str(e)}

    finally:
        # 確保資料庫連線關閉
        if "conn" in locals() and conn.is_connected():
            mycursor.close()
            conn.close()
