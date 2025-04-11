from fastapi import *
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

import json
import mysql.connector
import jwt


def get_db():  # 連接資料庫
    return mysql.connector.connect(
        user="user1", password="1234", host="localhost", database="taipei"
    )


app = FastAPI()
security = HTTPBearer()

app.mount("/static", StaticFiles(directory="static"), name="static")

key = "jzB42joCEFRnYVU34bTq"


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
        sql = "SELECT COUNT(*) FROM attractions a WHERE 1=1"
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

        mycursor.execute(sql, tuple(val))
        result_count = mycursor.fetchone()[0]

        next_page = page + 1 if result_count > offset + limit else None
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
            return JSONResponse(
                status_code=400, content={"error": True, "message": "景點編號不正確"}
            )

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


class User(BaseModel):
    name: str
    email: str
    password: str


@app.post("/api/user")
def user(user: User):
    con = get_db()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM member WHERE email = %s", (user.email,))
    existing_user = cursor.fetchone()
    con.close()
    if existing_user is not None:
        res_content = {
            "error": True,
            "message": "註冊失敗，重複的 Email 或其他原因",
        }
        return JSONResponse(content=res_content, status_code=400)
    if not user.name or not user.email or not user.password:
        res_content = {
            "error": True,
            "message": "註冊失敗，請檢查輸入的資料是否完整",
        }
        return JSONResponse(content=res_content, status_code=400)
    # 插入資料庫
    con = get_db()
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO member (name, email, password) VALUES (%s,%s, %s)",
        (user.name, user.email, user.password),
    )
    con.commit()
    con.close()
    res_content = {
        "ok": True,
        "message": "註冊成功",
    }

    return JSONResponse(content=res_content, status_code=200)


class LoginUser(BaseModel):
    email: str
    password: str


@app.put("/api/user/auth")
def signin(user: LoginUser):
    if not user.email or not user.password:
        res_content = {"error": True, "message": "登入失敗，帳號或密碼錯誤或其他原因"}
        return JSONResponse(content=res_content, status_code=400)
    try:
        con = get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT email, password, name FROM member WHERE email = %s",
            (user.email,),
        )
        existing_user = cursor.fetchone()
        con.close()
        if existing_user is None:
            res_content = {
                "error": True,
                "message": "登入失敗，帳號或密碼錯誤或其他原因",
            }
            return JSONResponse(content=res_content, status_code=400)
        if (
            user.email == existing_user["email"]
            and user.password == existing_user["password"]
        ):
            data = {
                "email": existing_user["email"],
                "name": existing_user["name"],
                "exp": datetime.now(timezone.utc) + timedelta(days=7),
            }
            res_content = {"token": jwt.encode(data, key, algorithm="HS256")}
            return JSONResponse(content=res_content, status_code=200)
        else:
            res_content = {
                "error": True,
                "message": "登入失敗，帳號或密碼錯誤或其他原因",
            }
            return JSONResponse(content=res_content, status_code=400)
    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": "伺服器內部錯誤"}
        return JSONResponse(content=res_content, status_code=500)


@app.get("/api/user/auth")
def getUserInfo(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, key, algorithms=["HS256"])
        email = decoded["email"]
        name = decoded["name"]
        return {"data": {"email": email, "name": name}}
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401, content={"error": True, "message": "Token expired"}
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=401, content={"error": True, "message": "Invalid token"}
        )
    except Exception as e:
        print("ex:", e)
        return JSONResponse(
            status_code=500, content={"error": True, "message": "伺服器內部錯誤"}
        )
