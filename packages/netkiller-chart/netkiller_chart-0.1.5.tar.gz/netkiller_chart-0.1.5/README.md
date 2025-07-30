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
usage: mindmap.py [-h] [-m /path/to/yout.md] [-s] [-o example.svg]

Markdown To Mindmap

options:
  -h, --help            show this help message and exit
  -m, --markdown /path/to/yout.md
                        Markfown file
  -s, --stdin           Standard input from the terminal
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

### 从标准输入创建思维导图

```shell
(.venv) neo@netkiller netkiller-chart % cat test/mindmap/os.md 
# Operating System History

- Operating System
  - Linux
    - Redhat
      - Fedora
      - SUSE
      - CentOS
        - Rocky Linux
        - AlmaLinux
    - Gentoo
    - Slackware
    - Debian
      - Ubuntu
    - Arch Linux
  - Apple OS
    - macOS
      - Yosemite
      - Capitan
      - Sierra / High Sierra
      - Mojave
      - Catalina
      - Big Sur
      - Monterry
      - Ventura
      - Sonoma
      - Sequoia
    - iPadSO
    - tvOS
    - iOS
    - watchOS
  - Unix
    - Solaris
    - Aix
    - Hp-Ux
    - Sco Unix
    - Irix
    - BSD
      - FreeBSD
      - NetBSD
      - OpenBSD
  - Microsoft
    - MsDos 6.22
    - Win3.2
    - Win 95 / 98 / 2000
    - Windows Phone
    - Windows Vista
    - Windows 10/11
    - Windows NT%    
```

```shell
(.venv) neo@netkiller netkiller-chart % cat test/mindmap/os.md | mindmap -o test/mindmap/os.svg -s

```