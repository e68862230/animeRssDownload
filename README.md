# animeRssDownload
支持浏览器右键自动添加动画的RSS链接到QB，并处理下载剧名的一系列文件集合

#教程
# 1.浏览器插件安装
chromeTest里是插件的解压包，如何安装可以百度一下，以后会上架edge商店

# 2.启动浏览器访问的fastapi服务
## ①python环境
安装python3和pip，然后运行`pip install -r requirements.txt`装一下requirement里的依赖
## ②启动服务
把python文件下载下来，修改`settings.json`里的用户名密码，并`api_key`和`download_path`为你自己的，然后执行`uvicorn main:app --reload --host 0.0.0.0 --port 8001`,这里端口和IP可以自己指定

# 3.qb下载完成时执行的外部程序(docker版本的qb需要带python环境)
## ①下载脚本
把`test.sh`下载下来，需要和python文件放一起，然后修改`test.sh`中的`/data/pythonService/aniNameTrans.py"`，把路径设置为你自己的py文件路径
## ②更改QB的设置
点击torrent完成时运行外部环境，然后填写`bash xxxxx/test.sh "%N" "%F"  "%C" "%D"`,其中xxxxx为你的test.sh脚本路径

# 以上设置完成

# 接下来为使用教程，以萌番组网站为例
# 1.设置浏览器选项
在浏览器的扩展选项中作如下设置，用户名密码填你settings.json里的，然后服务的IP端口对应你fastapi的IP和端口，QB的填你QB的
![UW{GF4KQ0F4$QI07PBW508H](https://user-images.githubusercontent.com/24666325/150326519-469a2ee9-1da3-4025-9f9b-ffd67ee65d0b.png)
# 2.RSS自动下载
打开萌番组网页，搜索你的番剧，然后在RSS订阅处右击，选择RSS下载到服务器即可
![image](https://user-images.githubusercontent.com/24666325/150326991-8ff9c101-ac01-4148-86b7-ff389d3feb5f.png)

## 成功提示
![image](https://user-images.githubusercontent.com/24666325/150327256-2affcf4e-7205-4410-8ebb-21c98343770d.png)

## 失败提示
![CN$@M{QA%5C~FNT)42DZ)WK](https://user-images.githubusercontent.com/24666325/150327330-2a21d904-b97c-4808-8c8f-c8eb6b22e123.png)


# 有问题可以随时issue咨询

