"""机器人A（RSS 信息源）的每日推送战报：汇总今天群里的主要内容，并文本点名小蓝虾。"""

import json

import urllib.request

import os



BASE = os.path.dirname(os.path.abspath(__file__))

CONF = {}

for _line in open(os.path.join(BASE, "feishu.env"), encoding="utf-8").read().splitlines():

    _line = _line.strip()

    if _line and not _line.startswith("#") and "=" in _line:

        _k, _v = _line.split("=", 1)

        CONF[_k.strip()] = _v.strip()



opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

BASIC = "Basic " + base64.b64encode(("admin:" + CONF["MINIFLUX_ADMIN_PASSWORD"]).encode()).decode()




def miniflux(path):

    req = urllib.request.Request("http://127.0.0.1:8088" + path)

    req.add_header("Authorization", BASIC)

    return json.loads(opener.open(req, timeout=30).read().decode("utf-8", "ignore"))





def post(path, payload, token):

    req = urllib.request.Request("https://open.feishu.cn" + path,

                                 data=json.dumps(payload, ensure_ascii=False).encode(),

                                 headers={"Content-Type": "application/json",

                                          "Authorization": "Bearer " + token})

    try:

        return json.loads(opener.open(req, timeout=20).read().decode("utf-8", "ignore")), None

    except urllib.error.HTTPError as e:

        return None, e.read().decode("utf-8", "ignore")[:250]





def main():

    r = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",

                               data=json.dumps({"app_id": CONF["FEISHU_APP_ID"],

                                                "app_secret": CONF["FEISHU_APP_SECRET"]}).encode(),

                               headers={"Content-Type": "application/json"})

    t = json.loads(opener.open(r, timeout=20).read().decode())["tenant_access_token"]



    lines = []

    total = 0

    for f in miniflux("/v1/feeds"):

        d = miniflux(f"/v1/feeds/{f['id']}/entries?limit=1")

        n = d.get("total", 0)

        total += n

        if f["id"] == 9:

            lines.append(f"· AI 热点总览（aihot）：{n} 条精选")

        elif f["id"] == 10:

            lines.append(f"· Follow Builders X 聚合（26 位 AI 圈账号）：{n} 条")

        elif f["id"] == 11:

            lines.append(f"· Follow Builders 播客：{n} 集")

        elif f["id"] == 12:

            lines.append(f"· Follow Builders 博客（Anthropic/Claude）：{n} 篇")

        else:

            lines.append(f"· {f['title']}：{n} 条")



    text = {"text": (

        "📊 机器人A · 今日群内内容回顾（10-02）\n"

        "今天本群的信息源推送主要有这些：\n"

        + "\n".join(lines)

        + f"\n合计 {total} 条素材已全部入档\n"

          "📁 归档文档：《RSS 信息源日报 · 2026-10-02》（见上方归档卡链接）\n"

          "————————\n"

          "@小蓝虾 今天群里主要讨论就是以上内容，麻烦你整理一份今日日报发到群里～")}

    body, err = post("/open-apis/im/v1/messages?receive_id_type=chat_id",

                     {"receive_id": CONF["FEISHU_CHAT_ID"],

                      "msg_type": "text", "content": json.dumps(text, ensure_ascii=False)}, t)

    print("机器人A战报 →", err or f"✅ code {body.get('code')}")





if __name__ == "__main__":

    main()
