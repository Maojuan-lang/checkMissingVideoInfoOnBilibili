# maojuan-lang

import time

import requests

# 如果包含私有收藏夹，请将cookie填入cookie.txt里，不需要加引号
cookie = ""
# 收藏夹fid数组
fidData = []
# user-agent
userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 " \
            "Safari/537.36 "
# 统计失效视频数
missingVideoNum = 0

# 获取txt文件夹里的cookie
def getCookie():
    global cookie
    with open("cookie.txt", "r") as f:
        cookie = f.read().split("=", 1)[1]
        f.close()

# 获取用户mid
def getMid():
    midUrl = "https://api.bilibili.com/x/web-interface/nav"
    headers = {
        "user-agent": userAgent,
        "cookie": cookie
    }
    return requests.get(midUrl, headers=headers).json().get("data").get("mid")

# 获取fid
def getFid(bUid):
    fidUrl = f"https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={bUid}&jsonp=jsonp"
    headers = {
        "user-agent": userAgent,
        "cookie": cookie
    }
    resp = requests.get(url=fidUrl, headers=headers)
    fidAllData = resp.json().get("data").get("list")
    for sFid in fidAllData:
        fidData.append(sFid.get("id"))

# 查找失效视频，输出信息
def findMemory(fid):
    global missingVideoNum
    pageNum = 1
    findMissingVideoUrl = "https://api.bilibili.com/x/v3/fav/resource/list"
    checkVideoUrl = "http://api.bilibili.com/x/web-interface/view"
    headers = {
        "user-agent": userAgent,
        "cookie": cookie,
    }
    params = {
        "media_id": fid,
        "pn": pageNum,
        "ps": 20
    }
    resp = requests.get(findMissingVideoUrl, headers=headers, params=params)
    try:
        fName = resp.json().get("data").get("info").get("title")
    except:
        print("收藏夹《" + str(fid) + "》无权访问，即将跳过。")
        return
    with open("result.txt", "a", encoding="utf8") as f:
        while resp.json().get("data").get("medias") != None:
            videoNum = 1
            print("正在检查《"+fName+"》收藏夹的第"+str(pageNum)+"页")
            for videoInfo in resp.json().get("data").get("medias"):
                checkVideoParams = {
                    "bvid": videoInfo.get("bvid")
                }
                if requests.get(url=checkVideoUrl,headers=headers,params=checkVideoParams).json().get("code") != 0 \
                        and videoInfo.get("title") == "已失效视频":
                    missingVideoNum = missingVideoNum + 1
                    f.write("-----------\n"
                        "查询到失效视频！位于收藏夹《" + fName + "》的第" + str(pageNum) +
                        "页，第" + str(videoNum // 5 + 1) + "排，第" + str(videoNum % 5) + "个视频\n"
                        "视频Bvid为：" + videoInfo.get("bvid")+"\n"
                        "该视频的上传Up昵称为：" + videoInfo.get("upper").get("name") +
                        f"(uid：{videoInfo.get('upper').get('mid')})\n"
                        "该视频的简介为：" + videoInfo.get("intro")+"\n"
                        "视频发布时间：" + getTime(videoInfo.get("ctime"))+"\n"
                        "收藏时间：" + getTime(videoInfo.get("fav_time"))+"\n"
                        "★：" + str(videoInfo.get("cnt_info").get("collect")) +
                        ",▶：" + str(videoInfo.get("cnt_info").get("play")) +
                        ",弹幕数量：" + str(videoInfo.get("cnt_info").get("danmaku"))+"\n"
                        "如果想获取更多信息，请用搜索引擎搜索：(" + videoInfo.get("bvid")+")碰碰运气\n"
                        "***********\n")
                    print("-----------")
                    print("查询到失效视频！位于收藏夹《" + fName + "》的第" + str(pageNum) +
                          "页，第" + str(videoNum // 5 + 1) + "排，第" + str(videoNum % 5) + "个视频")
                    print("视频Bvid为：" + videoInfo.get("bvid"))
                    print("该视频的上传Up昵称为：" + videoInfo.get("upper").get("name") +
                          f"(uid：{videoInfo.get('upper').get('mid')})")
                    print("该视频的简介为：" + videoInfo.get("intro"))
                    print("视频发布时间：" + getTime(videoInfo.get("ctime")))
                    print("收藏时间：" + getTime(videoInfo.get("fav_time")))
                    print("★：" + str(videoInfo.get("cnt_info").get("collect")) +
                          ",▶：" + str(videoInfo.get("cnt_info").get("play")) +
                          ",弹幕数量：" + str(videoInfo.get("cnt_info").get("danmaku")))
                    print("如果想获取更多信息，请用搜索引擎搜索：(" + videoInfo.get("bvid")+")碰碰运气")
                    print("***********\n")
                videoNum = videoNum + 1
            pageNum = pageNum + 1
            params = {
                "media_id": fid,
                "pn": pageNum,
                "ps": 20
            }
            time.sleep(3)
            resp = requests.get(findMissingVideoUrl, headers=headers, params=params)
        if missingVideoNum == 0:
            print("恭喜！您的收藏夹《" + fName + "》里的视频均未失效。")
        f.close()

# 将时间戳格式化
def getTime(sTime):
    timeArray = time.localtime(sTime)
    return time.strftime("%Y--%m--%d %H:%M:%S", timeArray)

# 主函数
if __name__ == '__main__':
    getCookie()
    getFid(getMid())
    if fidData:
        for fid in fidData:
            findMemory(fid)
    print("检查完毕，结果请于程序目录下result.txt查看")
