import requests
import json

# 配置目标地址
url = "http://127.0.0.1:8000/api/v1/futures/test/price"

# 配置你要修改的数据
payload = {
    "symbol": "BTC/USDT",
    "price": 98000  # 这里改成你想测试的价格
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("✅ 成功！价格已修改为:", payload['price'])
        print("服务器返回:", response.json())
    else:
        print("❌ 失败，状态码:", response.status_code)
        print("错误信息:", response.text)
except Exception as e:
    print("❌ 无法连接服务器:", e)