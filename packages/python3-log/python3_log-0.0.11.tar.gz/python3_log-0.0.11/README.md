# log


## 安装
```bash
pip3 install python3-log
```

## 用法
* 配置日志
修改 [env.sh](env.sh), 然后执行如下命令使变量生效，若不执行此步骤，则默认会采用此文件中的值作为默认值
```bash
source env.sh 
```


```python
from log import log

log.info("info log")
log.warning("warnning log")
log.error("error log")
```
默认情况下，在Windows平台，日志文件存放在当前目录下，在linux平台，则按照 [env.sh](env.sh) 中配置的位置存放

