# Dictionary on DNS

「[滚去背单词](http://jianbing.org)」的查字典的工具，在 shell 下使用，通过网络查询，方便喜欢英文的 Linux/Mac Hackers 使用。

使用 DNS 查单词优点是速度快，并且无须客户端，随时可以查哦～

## Features
1. 速度快，跟本机一样快～
1. 支持词组

    ```sh
    $ j a little
    少量, 少许
    ```
1. 支持 任何语言->任何语言（理论上支持，暂缺词库）

    ```sh
    $ j 西藏
    Tibet
    ```
1. 区分大小写

    ```sh
    $ j frank
    [fræŋk]
    adj.
    坦白的, 率直的, 老实的
    vt.
    免费邮寄
    n.
    免费邮寄特权
    ```

    大写

    ```sh
    $ j Frank
    [fræŋk]
    n.
    弗兰克（男子名）
    ```
1. 模糊查找

    ```sh
    $ j appe
    No word 'appe' found, did you mean:
     1. nappe [næp] n. 越过水坝落下的水, 叠层结构, 等分半圆锥
     2. apple ['æpl] n. 苹果, 似苹果的果实
     3. appel [ә'pel] n. 灵快的踏足, 垫步
    ```

## Usage

1. 在 ~/.bashrc 的末尾添加下面几行

    ```sh
    # jianbing.org on DNS
    function j {
        dig "$*.jianbing.org" +short txt | perl -pe's/\\(\d{1,3})/chr $1/eg; s/(^"|"$)//g'
    }
    ```

2. 重新打开你的 shell 或者 $ . ~/.bashrc

3. Enjoy jianbing on DNS

    ```sh
    $ j cat
    [kæt]
    n.
    猫
    ```

## Installation

1. 安装virtualenv和依赖

    ```sh
    $ virtualenv env
    $ . ./env/bin/activate
    $ pip install dnslib # easy & fast than dnspython
    $ pip install gevent # fastest network library
    $ apt-get install aspell # spelling check. or $ yum install aspell
    ```

1. 下载星际译王词库

    ```sh
    $ #（因为比较难下载到，仓库里提供了一个压缩包
    $ # 如果你不是用的这个，需要修改 stardict.py 里的配置
    $ tar xvf stardict-lazyworm-ec-2.4.2.tar.bz2
    $ cd stardict-lazyworm-ec-2.4.2
    $ gunzip -S '.dz' lazyworm-ec.dict.dz
    ```

1. 运行

    ```sh
    $ sudo ./jianbing-dns.py
    ```

1. 如果需要管理进程，请使用 supervisor

1. 本机测试，在 ~/.bashrc 的末尾添加下面几行

    ```sh
    # jianbing.org on DNS
    function j {
        dig "$*.jianbing.org" +short txt @localhost | perl -pe's/\\(\d{1,3})/chr $1/eg; s/(^"|"$)//g'
    }
    ```

1. 部署到外网，修改解析（可选）

   1. 为 `ns1.youdomain.com` 添加一个 A 记录，指向你的服务器地址
   1. 添加一个DNS泛解析，在 `*.yourdomain.com` 添加 NS 记录指向 `ns1.yourdomain.com`
   1. 修改上一步的那几行，去掉 `@localhost`，将 `jianbing.org` 改为 `yourdomain.com`


1. 验证上一步

    ```sh
    $ dig +trace apple.yourdomain.com
    ```

## Changelog

### The Go Language Version - 2012-09-27
1. 新增了 Go 版本，没有全面测试，速度应该是比 python 快一些

    ```sh
    $ mkdir your-local-go-location
    $ cd your-local-go-location
    $ export GOPATH=/path/to/your-local-go-location
    $ go get github.com/chuangbo/jianbing-dictionary-dns/golang/jianbing-dns
    $ sudo ./bin/jianbing-dns
    ```

### 增加模糊查找功能 - 2012-11-22
使用了 [difflib.get_close_matches](http://docs.python.org/2/library/difflib.html#difflib.get_close_matches)，以及 https://github.com/miohtama/python-Levenshtein 进行算法加速


### 更换了模糊查找的实现 - 2013-01-15
换成 aspell，速度提高几十倍。原来是遍历字典，使用最短路径算法匹配最相似单词，现在使用 aspell 检查拼写，应该是用了基于统计模型的拼写检查算法。可能只支持 Linux，我在 Mac 上测试出现了段错误。计划下一步加上 nose / mock 测试，以及 travis-ci。

> 这里有徐宥老师翻译的文章，很值得一看 <http://blog.youxu.info/spell-correct.html>
