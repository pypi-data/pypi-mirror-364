# netkiller-chart

https://www.netkiller.cn

## 安装

下载地址：https://pypi.org/project/netkiller-chart/

```shell
pip install netkiller-chart
```

## Gantt 甘特图

![数据图表](https://raw.githubusercontent.com/netkiller/netkiller-chart/main/doc/gantt.svg)

## Mindmap 思维导图

![数据图表](https://github.com/netkiller/netkiller-chart/raw/main/doc/mindmap.svg)

### 命令行

```shell
usage: mindmap.py [-h] [-m /path/to/yout.md] [-o example.svg]

Markdown To Mindmap

options:
  -h, --help            show this help message and exit
  -m, --markdown /path/to/yout.md
                        Markfown file
  -o, --output example.svg
                        output picture
```

创建 Mindmap

```shell
mindmap -m /path/to/neo.md -o /path/to/netkiller.svg
```

### 编程方式

```python

from netkiller.mindmap import Mindmap

markdown = """
# 操作系统
- Operating System
  - Linux
    - Redhat
    - CentOS
    - Rocky Linux
  - Apple OS  
    - macOS
      - nojava
      - catalina
    - iPadSO
    - tvOS 
    - iOS
    - watchOS 
  - Unix
    - Solaris
    - Aix
    - Hp-Ux
    - Sco Unix
"""
mindmap = Mindmap(markdown)
mindmap.save('example.svg')

```