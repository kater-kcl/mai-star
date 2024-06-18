# mai-star舞萌多功能查分器
## 运行指南
**1. 安装Python3.7及以上版本**   
**2. 安装依赖库**
```shell
pip install -r requirements.txt
```
**3. 安装gunicorn**
```shell
pip install gunicorn
```
**4. 配置/config/config.ini**   
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
**5. 运行**   
请将命令修改为你的url和端口
```shell
gunicorn -b {your_url}:{your_port} main:app
```