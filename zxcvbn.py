import requests
import json
import sqlite3
class MySpider:
    def __init__(self):
        self.con=None
        self.cursor=None
    def openDB(self):
        self.con=sqlite3.connect("rates.db")
        self.cursor=self.con.cursor()
        sql = "CREATE TABLE IF NOT EXISTS rates (Currency varchar(256) primary key, TSP float, CSP float, TBP float, CBP float, Time varchar(256))"
        self.cursor.execute(sql)
        print("Initializing database successfully,table ready!")
    def insertData(self,currency,tsp,csp,tbp,cbp,time_str):
        sql="INSERT OR REPLACE INTO rates (Currency,TSP,CSP,TBP,CBP,Time)VALUES (?,?,?,?,?,?)"
        self.cursor.execute(sql,(currency,tsp,csp,tbp,cbp,time_str))
    def closeDB(self):
        if self.con:
            self.con.commit()
            self.con.close()
def main():
    api_url = "https://fx.cmbchina.com/api/v1/fx/rate"
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding":"gzip, deflate",
        "Connection":"keep-alive",
        "Upgrade-Insecure-Requests":"1",
        "Sec-Fetch-Dest":"document",
        "Sec-Fetch-Mode":"navigate",
        "Sec-Fetch-Site":"none",
        "Sec-Fetch-User":"?1",
        "Cache-Control":"max-age=0",
        "Referer":"https://fx.cmbchina.com/",
    }
    spider = MySpider()
    spider.openDB()
    try:
        resp = requests.get(api_url,headers=headers,timeout=10)
        if resp.status_code == 200:
            print("Request OK")
            data=resp.json()
            formatted_json=json.dumps(data,ensure_ascii=False,indent=4)
            print(formatted_json)
            count=0
            for item in data["body"]:
                currency=item["ccyNbrEng"]
                tsp=float(item["rthOfr"])
                csp=float(item["rtcOfr"])
                tbp=float(item["rthBid"])
                cbp=float(item["rtcBid"])
                time_str=item["ratTim"]
                spider.insertData(currency,tsp,csp,tbp,cbp,time_str)
                count+=1
                print(f"inserted {currency}")
            print(f"Total {count} records inserted")
        else:
            print(f"Request Failed with status code: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        spider.closeDB()
if __name__ == "__main__":
    main()