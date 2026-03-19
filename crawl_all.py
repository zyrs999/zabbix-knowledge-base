import requests
from bs4 import BeautifulSoup
import json

# 爬取来源配置（含Zabbix官网+上海宏时数据+国内社区）
SOURCES = [
    # 1. Zabbix官方中文文档
    {
        "name": "zabbix_official_cn",
        "urls": [
            "https://www.zabbix.com/documentation/current/zh/manual/installation",
            "https://www.zabbix.com/documentation/current/zh/manual/config",
            "https://www.zabbix.com/documentation/current/zh/manual/monitoring",
            "https://www.zabbix.com/documentation/current/zh/manual/alerting",
            "https://www.zabbix.com/documentation/current/zh/manual/api"
        ]
    },
    # 2. 上海宏时数据（国内Zabbix官方合作伙伴）
    {
        "name": "grandage_cn",
        "urls": [
            "https://www.grandage.cn/index.php",
            "https://www.grandage.cn/zabbix.php",
            "https://www.grandage.cn/case.php",
            "https://www.grandage.cn/support.php",
            "https://www.grandage.cn/news.php"
        ]
    },
    # 3. 国内Zabbix社区（补充中文资料）
    {
        "name": "zabbix_cn_community",
        "urls": [
            "https://www.zabbix.net.cn/",
            "https://www.zabbix.net.cn/news.html",
            "https://www.zabbix.net.cn/help.html"
        ]
    }
]

def crawl_zabbix_knowledge():
    """爬取所有来源的Zabbix中文资料，生成结构化知识库"""
    knowledge_data = []
    
    # 通用请求头（避免被反爬）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive"
    }

    # 遍历所有来源爬取
    for source in SOURCES:
        source_name = source["name"]
        for url in source["urls"]:
            try:
                # 发送请求（超时15秒）
                response = requests.get(url, headers=headers, timeout=15)
                response.encoding = "utf-8"  # 强制UTF-8编码，避免乱码
                
                # 解析网页内容
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 提取正文（优先取content/div，兜底取body）
                content = soup.find("div", class_="doc-content") or soup.find("div", class_="content") or soup.find("body")
                if not content:
                    print(f"⚠️ 无正文内容：{url}")
                    continue
                
                # 清理文本（去空格、换行）
                clean_text = content.get_text(strip=True, separator="\n")
                if len(clean_text) < 200:  # 过滤太短的无效内容
                    print(f"⚠️ 内容过短：{url}")
                    continue
                
                # 结构化存储
                knowledge_data.append({
                    "source": source_name,
                    "url": url,
                    "title": soup.title.string.strip() if soup.title else url,
                    "content": clean_text[:12000]  # 限制长度，避免文件过大
                })
                print(f"✅ 爬取成功：{url}")

            except Exception as e:
                print(f"❌ 爬取失败 {url}：{str(e)}")
                continue

    # 保存到JSON文件（GitHub云端存储）
    with open("zabbix_knowledge_all.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 爬取完成！共获取 {len(knowledge_data)} 条有效内容")

if __name__ == "__main__":
    crawl_zabbix_knowledge()
