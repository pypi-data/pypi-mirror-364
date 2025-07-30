# Scrapy-Colorful-Log

基于[python-*colorlog*](https://github.com/borntyping/python-colorlog)的轻量级scrapy日志样式自定义模块。

## 安装

Install by pip or pip3:

```python
pip install scrapy-colorful-log
```



## 快速开始

In setting.py

```python
import scrapy_colorful_log
scrapy_colorful_log.set_color()
```

接下来，您可以在终端查看输出日志



##	默认参数

无需另外设置，按以下默认参数展示日志

```python
# 默认日志格式 asctime name levelname message 具体对应参照截图
LOG_DEFAULT_FORMAT = (
    "%(asctime_log_color)s%(asctime)s%(reset)s "
    "%(name_log_color)s [%(name)s] %(reset)s "
    # "%(bold_white)s[%(module)s]%(reset)s "
    "%(log_color)s  %(levelname)s  %(reset)s :\n"
    "%(message_log_color)s%(message)s%(reset)s\n"
    "%(white)s" + "-"*100 + "%(reset)s"
)

# 默认日期格式
LOG_DEFAULT_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# 默认asctime颜色配置
LOG_DEFAULT_ASCTIME_COLORS = {
  "DEBUG": "bold_white",
  "INFO": "bold_white",
  "WARNING": "bold_white",
  "ERROR": "bold_white",
  "CRITICAL": "bold_white",
}

# 默认name颜色配置
LOG_DEFAULT_NAME_COLORS = {
  "DEBUG": "bold_black,bg_white",
  "INFO": "bold_black,bg_white",
  "WARNING": "bold_black,bg_white",
  "ERROR": "bold_black,bg_white",
  "CRITICAL": "bold_black,bg_white",
}

# 默认levelname颜色配置
LOG_DEFAULT_LEVEL_COLORS = {
  "DEBUG": "bold_white,bg_blue",
  "INFO": "bold_white,bg_cyan",
  "WARNING": "bold_white,bg_yellow",
  "ERROR": "bold_white,bg_red",
  "CRITICAL": "bold_white,bg_purple",
}

# 默认message颜色配置
LOG_DEFAULT_MESSAGE_COLORS = {
  "DEBUG": "light_blue",
  "INFO": "light_cyan",
  "WARNING": "light_yellow",
  "ERROR": "light_red",
  "CRITICAL": "light_purple",
}

```



## 自定义

在setting.py中设置对应参数，则覆盖默认参数展示日志，参数key值与默认参数一致

```python
import scrapy_colorful_log
scrapy_colorful_log.set_color()

# 自定义日志格式 asctime name levelname message 可按需展示或增加特定输出
# 不建议直接修改日志格式，除非是对最后一行分界线做修改 
LOG_DEFAULT_FORMAT = (
   'xxxxxxxxxxxxxxxxxxxxxx'
)


# 默认日期格式
LOG_DEFAULT_DATEFORMAT = "xxxxxxx"

# 默认asctime颜色配置
LOG_DEFAULT_ASCTIME_COLORS = {
   "DEBUG": "xxxx",
  "INFO": "xxxx",
  "WARNING": "xxxx",
  "ERROR": "xxxx",
  "CRITICAL": "xxxx",
}

# 默认name颜色配置
LOG_DEFAULT_NAME_COLORS = {
   "DEBUG": "xxxx",
  "INFO": "xxxx",
  "WARNING": "xxxx",
  "ERROR": "xxxx",
  "CRITICAL": "xxxx",
}

# 默认levelname颜色配置
LOG_DEFAULT_LEVEL_COLORS = {
  "DEBUG": "xxxx",
  "INFO": "xxxx",
  "WARNING": "xxxx",
  "ERROR": "xxxx",
  "CRITICAL": "xxxx",
}

# 默认message颜色配置
LOG_DEFAULT_MESSAGE_COLORS = {
   "DEBUG": "xxxx",
  "INFO": "xxxx",
  "WARNING": "xxxx",
  "ERROR": "xxxx",
  "CRITICAL": "xxxx",
}

```



## 截图

#### INFO logs in iterm2

![INFO logs in iterm2](https://github.com/Manjusaka-N/images/blob/master/202507241636/info-log.jpg?raw=true)

#### DEBUG logs in iterm2

![DEBUG logs in iterm2](https://github.com/Manjusaka-N/images/blob/master/202507241636/debug-log.jpg?raw=true)

#### WARNING logs in iterm2

![WARNING logs in iterm2](https://github.com/Manjusaka-N/images/blob/master/202507241636/warning-log.jpg?raw=true)

#### ERROR logs in iterm2

![ERROR logs in iterm2](https://github.com/Manjusaka-N/images/blob/master/202507241636/error-log.jpg?raw=true)

#### CRITICAL logs in iterm2

![CRITICAL logs in iterm2](https://github.com/Manjusaka-N/images/blob/master/202507241636/critical-log.jpg?raw=true)

#### All kinds in iterm2

![All kinds in iterm2](https://github.com/Manjusaka-N/images/blob/master/202507241636/all-kind-logs.jpg?raw=true)
