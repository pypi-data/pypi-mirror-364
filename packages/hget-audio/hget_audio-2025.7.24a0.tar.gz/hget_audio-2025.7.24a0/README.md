# hget-audio - Website Audio Downloader

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![Scrapy Version](https://img.shields.io/badge/scrapy-2.5%2B-orange.svg)](https://scrapy.org/)

[English]
## Comprehensive Error Handling

hget-audio implements robust error handling throughout the application. When errors occur:

1. **Non-verbose mode (default)**:
   - Captures all exceptions and displays a user-friendly message
   - Recommends using `--verbose` for detailed error information
   - Provides a unique error code for reference
   - Logs full error details to a file for later analysis

2. **Verbose mode (`--verbose`)**:
   - Displays complete error tracebacks
   - Shows internal state information for debugging
   - Includes additional diagnostic data
   - Does not capture exceptions - allows full error propagation

### Error Handling Examples

**Without verbose flag**:
2023-10-15 14:30:25 [ERROR] Download failed (Error Code: DL-102)
Error: Connection timeout while downloading audio file.
Solution: Try increasing timeout with --timeout option
For more details, run with --verbose flag or check error log: errors_20231015_143025.log

text

**With verbose flag**:
2023-10-15 14:30:25 [ERROR] Full traceback:
File "/path/to/hget_audio/pipelines.py", line 215, in media_downloaded
response = super().media_downloaded(response, request, info, item=item)
File "/path/to/scrapy/pipelines/files.py", line 320, in media_downloaded
raise FileException("Connection timeout")

scrapy.exceptions.FileException: Connection timeout

Request details:

URL: https://example.com/audio/large.mp3

Referer: https://example.com/audio-page

Size: 150 MB (exceeds max size of 100 MB)

Format: audio/mpeg

Retry count: 2/3

System information:

Python: 3.9.12

Scrapy: 2.7.1

Platform: Linux-5.15.0-86-generic-x86_64-with-glibc2.31

text

### Error Code Reference

| Code Range | Error Type               | Example Codes       |
|------------|--------------------------|--------------------|
| 100-199    | Network Errors          | 101: Connection, 102: Timeout |
| 200-299    | File Validation Errors  | 201: Invalid type, 202: Size |
| 300-399    | Configuration Errors    | 301: Invalid URL, 302: Invalid depth |
| 400-499    | Scraping Errors         | 401: Parser, 402: Spider |
| 500-599    | System Errors           | 501: Disk full, 502: Permissions |

### Error Logging

All errors are logged to timestamped files in the `error_logs` directory:
error_logs/
├── errors_20231015_143025.log
├── errors_20231016_093412.log
└── errors_20231017_154723.log

text

Each log file contains:
1. Full error traceback
2. Request and response details
3. System environment information
4. Configuration settings at time of error
5. Memory usage statistics

## Installation

### Using pip
```bash
pip install hget-audio
From source
bash
git clone https://github.com/hyy-PROG/hget_audio.git
cd hget_audio
pip install .
Command Line Usage
Basic command
bash
hget-audio "https://example.com/audio-page" -o "my_audios"
Advanced options
bash
hget-audio "https://example.com" \
  -d 3 \
  -c 8 \
  -f "mp3,wav" \
  --exclude "admin,private" \
  --max-size 50 \
  --timeout 30 \
  --retries 3 \
  -o "filtered_audios"
Full options
bash
hget-audio --help
API Usage
python
from hget_audio.api import download_audio

# Download website audio
result = download_audio(
    url="https://example.com/audio-page",
    output_dir="my_audios",
    depth=2,
    formats="mp3,wav",
    verbose=True  # Enable detailed error reporting
)

print(f"Downloaded {result['audio_downloaded']} audio files")
print(f"Total size: {result['total_size'] / (1024*1024):.2f} MB")
Configuration Options
Option	Description	Default
-o, --output	Output directory	hget.output
-d, --depth	Crawl depth	2
-c, --concurrency	Concurrent requests	16
-f, --formats	Audio formats (comma-separated)	mp3,wav,ogg,m4a,flac,aac
--ignore-robots	Ignore robots.txt rules	False
--user-agent	Custom User-Agent	Default UA
--delay	Request delay (seconds)	0.5
--timeout	Request timeout (seconds)	30
--retries	Max retry attempts	3
--max-size	Max file size (MB)	100
--min-size	Min file size (KB)	1
--include	Include URL patterns (regex)	Empty
--exclude	Exclude URL patterns (regex)	logout,admin,login
--dry-run	Simulation mode (no download)	False
-v, --verbose	Verbose output and error reporting	False
Example Output
text
2023-10-15 14:30:25 [INFO] Starting crawl: https://example.com/audio-page
2023-10-15 14:30:26 [DEBUG] Parsing page (depth=0): https://example.com/audio-page
2023-10-15 14:30:27 [INFO] Audio found: https://example.com/audio/sample1.mp3
2023-10-15 14:30:28 [INFO] Download successful: my_audios/example_com/sample1.mp3
...
2023-10-15 14:31:05 [INFO] Spider closed
==================================================
Scraping Summary
==================================================
Website: https://example.com/audio-page
Output Directory: /path/to/my_audios
Total Pages Crawled: 42
Audio Files Found: 15
Audio Files Downloaded: 12
Audio Files Skipped: 3
Errors Encountered: 0
Total Download Size: 245.7 MB
Contribution Guidelines
Fork the repository

Create your feature branch (git checkout -b feature/your-feature)

Commit your changes (git commit -am 'Add some feature')

Push to the branch (git push origin feature/your-feature)

Create a Pull Request

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For issues or suggestions: support@hget-audio.example

[中文]

全面的错误处理
hget-audio 在整个应用程序中实现了强大的错误处理机制。当发生错误时：

非详细模式（默认）:

捕获所有异常并显示用户友好的消息

建议使用 --verbose 参数获取详细错误信息

提供唯一的错误代码供参考

将完整错误详情记录到文件以供后续分析

详细模式 (--verbose):

显示完整的错误跟踪信息

显示内部状态信息用于调试

包含额外的诊断数据

不捕获异常 - 允许错误完全传播

错误处理示例
不使用详细标志:

text
2023-10-15 14:30:25 [ERROR] 下载失败 (错误代码: DL-102)
错误: 下载音频文件时连接超时
解决方案: 尝试使用 --timeout 选项增加超时时间
更多详情请使用 --verbose 参数运行或查看错误日志: errors_20231015_143025.log
使用详细标志:

text
2023-10-15 14:30:25 [ERROR] 完整错误跟踪:
  File "/path/to/hget_audio/pipelines.py", line 215, in media_downloaded
    response = super().media_downloaded(response, request, info, item=item)
  File "/path/to/scrapy/pipelines/files.py", line 320, in media_downloaded
    raise FileException("连接超时")
    
scrapy.exceptions.FileException: 连接超时

请求详情:
- URL: https://example.com/audio/large.mp3
- 来源页面: https://example.com/audio-page
- 大小: 150 MB (超过最大 100 MB 限制)
- 格式: audio/mpeg
- 重试次数: 2/3

系统信息:
- Python: 3.9.12
- Scrapy: 2.7.1
- 平台: Linux-5.15.0-86-generic-x86_64-with-glibc2.31
错误代码参考
代码范围	错误类型	示例代码
100-199	网络错误	101: 连接错误, 102: 超时
200-299	文件验证错误	201: 无效类型, 202: 大小不符
300-399	配置错误	301: 无效URL, 302: 无效深度
400-499	抓取错误	401: 解析错误, 402: 爬虫错误
500-599	系统错误	501: 磁盘已满, 502: 权限错误
错误日志记录
所有错误都记录在 error_logs 目录的时间戳文件中：

text
error_logs/
├── errors_20231015_143025.log
├── errors_20231016_093412.log
└── errors_20231017_154723.log
每个日志文件包含：

完整的错误跟踪信息

请求和响应详情

系统环境信息

错误发生时的配置设置

内存使用统计

安装
使用 pip 安装
bash
pip install hget-audio
从源码安装
bash
git clone https://github.com/hyy-PROG/hget_audio.git
cd hget-audio
pip install .
命令行使用
基本命令
bash
hget-audio "https://example.com/audio-page" -o "my_audios"
高级选项
bash
hget-audio "https://example.com" \
  -d 3 \
  -c 8 \
  -f "mp3,wav" \
  --exclude "admin,private" \
  --max-size 50 \
  --timeout 30 \
  --retries 3 \
  -o "filtered_audios"
完整选项
bash
hget-audio --help
API 使用
python
from hget_audio.api import download_audio

# 下载网站音频
result = download_audio(
    url="https://example.com/audio-page",
    output_dir="my_audios",
    depth=2,
    formats="mp3,wav",
    verbose=True  # 启用详细错误报告
)

print(f"下载了 {result['audio_downloaded']} 个音频文件")
print(f"总大小: {result['total_size'] / (1024*1024):.2f} MB")
配置选项
选项	描述	默认值
-o, --output	输出目录	hget.output
-d, --depth	爬取深度	2
-c, --concurrency	并发请求数	16
-f, --formats	音频格式 (逗号分隔)	mp3,wav,ogg,m4a,flac,aac
--ignore-robots	忽略 robots.txt 规则	False
--user-agent	自定义 User-Agent	默认 UA
--delay	请求延迟 (秒)	0.5
--timeout	请求超时时间 (秒)	30
--retries	最大重试次数	3
--max-size	最大文件大小 (MB)	100
--min-size	最小文件大小 (KB)	1
--include	包含的 URL 模式 (正则)	空
--exclude	排除的 URL 模式 (正则)	logout,admin,login
--dry-run	模拟运行模式 (不下载)	False
-v, --verbose	详细输出和错误报告	False
示例输出
text
2023-10-15 14:30:25 [INFO] 开始爬取: https://example.com/audio-page
2023-10-15 14:30:26 [DEBUG] 解析页面 (depth=0): https://example.com/audio-page
2023-10-15 14:30:27 [INFO] 发现音频: https://example.com/audio/sample1.mp3
2023-10-15 14:30:28 [INFO] 下载成功: my_audios/example_com/sample1.mp3
...
2023-10-15 14:31:05 [INFO] 爬虫结束
==================================================
爬取统计
==================================================
网站: https://example.com/audio-page
输出目录: /path/to/my_audios
爬取页面: 42
发现音频: 15
下载音频: 12
跳过音频: 3
错误: 0
总下载大小: 245.7 MB
贡献指南
Fork 项目仓库

创建特性分支 (git checkout -b feature/your-feature)

提交更改 (git commit -am '添加新功能')

推送到分支 (git push origin feature/your-feature)

创建 Pull Request

许可证
本项目采用 MIT 许可证 - 详情请见 LICENSE 文件。