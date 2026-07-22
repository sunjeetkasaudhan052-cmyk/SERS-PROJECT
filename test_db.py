import pymysql

try:
    conn = pymysql.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        port=4000,
        user="otDZndFBCN8S6vm.root",
        password="YAHAN_NAYA_PASSWORD",
        database="sys",
        ssl={"ssl": {}},
        autocommit=True
    )

    print("Connected Successfully")
    conn.close()

except Exception as e:
    print(e)