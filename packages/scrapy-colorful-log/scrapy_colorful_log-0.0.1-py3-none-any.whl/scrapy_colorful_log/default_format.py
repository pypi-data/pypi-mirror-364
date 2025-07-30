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
