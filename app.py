from fastapi import *
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

import json
import mysql.connector
import jwt
import requests


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


@app.post("/api/booking")
def booking(
    booking: dict, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        decoded = jwt.decode(token, key, algorithms=["HS256"])
        email = decoded["email"]
        name = decoded["name"]
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=403, content={"error": True, "message": "Token expired"}
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=403, content={"error": True, "message": "Invalid token"}
        )
    except Exception as e:
        print("ex:", e)
        return JSONResponse(
            status_code=500, content={"error": True, "message": "伺服器內部錯誤"}
        )

    try:
        booking["email"] = email
        if check_booking_exists(booking["email"]):
            update_booking(booking, email)
        else:
            booking["name"] = name
            create_booking(booking, email, name)

        res_content = {
            "attractionId": booking["attractionId"],
            "date": booking["date"],
            "time": booking["time"],
            "price": booking["price"],
        }

        return JSONResponse(content=res_content, status_code=200)

    except mysql.connector.IntegrityError:
        res_content = {
            "error": True,
            "message": "建立失敗，景點編號不正確或其他原因",
        }
        return JSONResponse(content=res_content, status_code=400)

    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


def check_booking_exists(email):
    con = get_db()
    cursor = con.cursor()
    cursor.execute(
        "SELECT * FROM booking WHERE email = %s",
        (email,),
    )
    booking_data = cursor.fetchone()
    con.close()
    return booking_data is not None


def update_booking(booking: dict, email: str):
    con = get_db()
    cursor = con.cursor()
    cursor.execute(
        """
        UPDATE booking
        SET attraction_id = %s, date = %s, time = %s, price = %s
        WHERE email = %s
        """,
        (
            booking["attractionId"],
            booking["date"],
            booking["time"],
            booking["price"],
            email,
        ),
    )
    con.commit()
    con.close()


def create_booking(booking: dict, email: str, name: str):
    con = get_db()
    cursor = con.cursor()
    cursor.execute(
        """
        INSERT INTO booking (attraction_id, date, time, price, email, name)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            booking["attractionId"],
            booking["date"],
            booking["time"],
            booking["price"],
            email,
            name,
        ),
    )
    con.commit()
    con.close()


def get_email(token):
    try:
        decoded = jwt.decode(token, key, algorithms=["HS256"])
        email = decoded["email"]
        return email
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=403, content={"error": True, "message": "Token expired"}
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=403, content={"error": True, "message": "Invalid token"}
        )
    except Exception as e:
        print("ex:", e)
        return JSONResponse(
            status_code=500, content={"error": True, "message": "伺服器內部錯誤"}
        )


@app.get("/api/booking")
def get_booking(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = get_email(credentials.credentials)
    if isinstance(email, JSONResponse):
        return email

    try:
        con = get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "select date, time, price, b.attraction_id, a.name, address, url image from booking b join attractions a on a._id = b.attraction_id left join images i on i.attraction_id = b.attraction_id WHERE email = %s",
            (email,),
        )
        booking_data = cursor.fetchone()
        con.close()

        if booking_data is None:
            res_content = {"data": None}
            return JSONResponse(content=res_content, status_code=200)

        res_content = {
            "data": {
                "attraction": {
                    "id": booking_data["attraction_id"],
                    "name": booking_data["name"],
                    "address": booking_data["address"],
                    "image": booking_data["image"],
                },
                "date": str(booking_data["date"]),
                "time": booking_data["time"],
                "price": booking_data["price"],
            }
        }

        return JSONResponse(content=res_content, status_code=200)

    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


@app.delete("/api/booking")
def delete_booking(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = get_email(credentials.credentials)
    if isinstance(email, JSONResponse):
        return email

    try:
        con = get_db()
        cursor = con.cursor()
        cursor.execute("DELETE FROM booking WHERE email = %s", (email,))
        con.commit()
        con.close()

        res_content = {"ok": True, "message": "刪除成功"}
        return JSONResponse(content=res_content, status_code=200)

    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


@app.post("/api/orders")
def createOrder(
    orders: dict, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    email = get_email(credentials.credentials)
    if isinstance(email, JSONResponse):
        return email
    booking_id = get_booking_id(orders["contact"]["email"])
    if isinstance(booking_id, JSONResponse):
        return booking_id
    order = get_order_from_db(booking_id)
    if isinstance(order, JSONResponse):
        return order
    if order is None:
        result = create_order_to_db(orders, booking_id)
        if result is not None:
            return result
        order = get_order_from_db(booking_id)
        if isinstance(order, JSONResponse):
            return order
    response = tap_pay(orders, order["id"])
    if isinstance(response, JSONResponse):
        return response
    result = update_order(response, order["id"])
    if isinstance(result, JSONResponse):
        return result
    return JSONResponse(
        content={
            "data": {
                "number": response["order_number"],
                "payment": {"status": response["status"], "message": "付款成功"},
            }
        },
        status_code=200,
    )


def get_booking_id(email: str):
    try:
        con = get_db()
        cursor = con.cursor()
        cursor.execute(
            """
            SELECT id FROM booking WHERE email = %s
            """,
            (email,),
        )
        booking_id = cursor.fetchone()
        con.close()
        return booking_id[0] if booking_id else None
    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


def create_order_to_db(orders: dict, order_id: int):
    try:
        con = get_db()
        cursor = con.cursor()
        cursor.execute(
            """
            INSERT INTO orders (booking_id, order_phone, payment_status)
            VALUES (%s, %s, %s)
            """,
            (
                order_id,
                orders["contact"]["phone"],
                "UNPAID",
            ),
        )
        con.commit()
        con.close()
        return
    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


def get_order_from_db(booking_id: str):
    try:
        con = get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT * FROM orders WHERE booking_id = %s and payment_status = 'UNPAID'
            """,
            (booking_id,),
        )
        order_data = cursor.fetchone()
        con.close()
        return order_data
    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


def tap_pay(orders: dict, order_id: int):
    url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "partner_xmmPhJr75LeGUcEXx1xxrAVgKW8S9mRUgbUlJt2GgflymYFJtIg71D0m",
    }

    now = datetime.now()
    # 格式化為 YYYYMMDDHHMMSS
    current_datetime = now.strftime("%Y%m%d%H%M%S")

    # 將年月日和 order_id 拼接成新的訂單編號
    new_order_number = current_datetime + str(order_id)

    body = {
        "prime": orders["prime"],
        "partner_key": "partner_xmmPhJr75LeGUcEXx1xxrAVgKW8S9mRUgbUlJt2GgflymYFJtIg71D0m",
        "merchant_id": "jean_ESUN",
        "amount": orders["order"]["price"],
        "currency": "TWD",
        "details": "Taipei Tour",
        "order_number": new_order_number,
        "cardholder": {
            "phone_number": orders["contact"]["phone"],
            "name": orders["contact"]["name"],
            "email": orders["contact"]["email"],
        },
    }
    response = requests.post(url, headers=headers, json=body)
    response_data = response.json()
    if response_data["status"] == 0:
        return response_data
    else:
        res_content = {
            "error": True,
            "message": "付款失敗，請檢查信用卡資訊或其他原因\n" + response_data["msg"],
        }
        return JSONResponse(content=res_content, status_code=400)


def update_order(orders: dict, order_id: int):
    try:
        con = get_db()
        cursor = con.cursor()
        cursor.execute(
            """
            UPDATE orders
            SET payment_status = %s, payment_serial = %s
            WHERE id = %s
            """,
            (
                "PAID",
                orders["order_number"],
                order_id,
            ),
        )
        con.commit()
        con.close()
    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


def get_order(orders: dict, order_id: int):
    try:
        con = get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT * FROM orders WHERE id = %s
            """,
            (order_id,),
        )
        order_data = cursor.fetchone()
        con.close()
        return order_data
    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)


@app.get("/api/order/{orderNumber}")
def get_order_by_number(
    orderNumber: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    email = get_email(credentials.credentials)
    if isinstance(email, JSONResponse):
        return email

    try:
        con = get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT * FROM orders o join booking b on o.booking_id = b.id join attractions a on b.attraction_id = a._id  left join images i on i.attraction_id = b.attraction_id WHERE payment_serial = %s
            """,
            (orderNumber,),
        )
        order_data = cursor.fetchone()
        con.close()

        if order_data is None:
            res_content = {"data": None}
            return JSONResponse(content=res_content, status_code=200)

        res_content = {
            "data": {
                "number": order_data["payment_serial"],
                "payment": {
                    "status": order_data["payment_status"],
                    "message": (
                        "付款成功"
                        if order_data["payment_status"] == "PAID"
                        else "付款失敗"
                    ),
                },
                "price": order_data["price"],
                "trip": {
                    "attraction": {
                        "id": order_data["attraction_id"],
                        "name": order_data["name"],
                        "address": order_data["address"],
                        "image": order_data["url"],
                    },
                    "date": str(order_data["date"]),
                    "time": order_data["time"],
                },
                "contact": {
                    "name": order_data["name"],
                    "email": order_data["email"],
                    "phone": order_data["order_phone"],
                },
            }
        }

        return JSONResponse(content=res_content, status_code=200)

    except Exception as e:
        print("ex:", e)
        res_content = {"error": True, "message": str(e)}
        return JSONResponse(content=res_content, status_code=500)
