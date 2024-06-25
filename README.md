# mai-star舞萌多功能查分器
## 后端部署指南
**1. 从github clone项目**
```shell
git clone https://github.com/kater-kcl/mai-star.git
```
**2. 从[此链接](www.diving-fish.com/maibot/static.zip)下载资源文件，解压后将/mai/cover里的内容移动至/resources/mai_cover**   
**资源仅供学习使用**
**3. 安装Python3.7及以上版本**   
**4. 安装依赖库**
```shell
pip install -r requirements.txt
```
**5. 安装gunicorn**
```shell
pip install gunicorn
```
**6. 配置/config/config.ini**   
复制config_tempelate.ini为config.ini，然后修改其中的配置
```ini
[default]
jwt_sec = 你的jwt密钥

[mysql]
host = sql服务器地址
port = sql服务器端口
username = sql用户名
password = sql密码
database_name = sql数据库名
```
**7. 运行**   
请将命令修改为你的url和端口
```shell
gunicorn -b {your_url}:{your_port} main:app
```

**特别鸣谢**   
感谢水鱼的diving-fish-api项目提供的查分器API