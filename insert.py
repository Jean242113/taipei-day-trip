import json
import mysql.connector


def insert_data_to_mysql(json_file, db_config):
    """
    從 JSON 檔案讀取資料，並將其插入到 MySQL 資料庫的兩個資料表中。

    Args:
        json_file (str): JSON 檔案的路徑。
        db_config (dict): MySQL 資料庫連線設定。
    """
    try:
        # 讀取 JSON 檔案
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        attractions = data["result"]["results"]

        # 連線到 MySQL 資料庫
        mydb = mysql.connector.connect(**db_config)
        mycursor = mydb.cursor()

        # 插入 attractions 資料表
        for attraction in attractions:
            sql_attractions = """
                INSERT INTO attractions (_id, name, description, address, latitude, longitude, direction, MRT, CAT)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            val_attractions = (
                attraction["_id"],
                attraction["name"],
                attraction["description"],
                attraction["address"],
                attraction["latitude"],
                attraction["longitude"],
                attraction["direction"],
                attraction["MRT"],
                attraction["CAT"],
            )
            mycursor.execute(sql_attractions, val_attractions)

            # 插入 images 資料表
            images = attraction.get("file", "").split("https://")
            for img in images:
                if len(img) > 0:
                    url = "https://" + img
                    if url.lower().endswith((".jpg", ".jpeg", ".png")):
                        sql_images = (
                            "INSERT INTO images (attraction_id, url) VALUES (%s, %s)"
                        )
                        val_images = (attraction["_id"], url)
                        mycursor.execute(sql_images, val_images)

        # 提交事務
        mydb.commit()
        print("資料插入成功！")

    except Exception as e:
        print(f"資料插入失敗：{e}")

    finally:
        if "mydb" in locals() and mydb.is_connected():
            mycursor.close()
            mydb.close()


# MySQL 資料庫連線設定 (請替換為您的實際設定)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "taipei",
}

# JSON 檔案路徑
json_file = "data/taipei-attractions.json"

# 執行插入資料的函式
insert_data_to_mysql(json_file, db_config)
