# Server construction guide


Use any possible PC: my test server is running on old laptop.

현재 이 프로젝트를 돌리는 테스트 서버에 작업한 건 다음과 같으며, 이 프로젝트를 돌려보고 싶으시다면 아래의 부분을 준비해주셔야 합니다:

참고. 현재 이 테스트 서버는 Ubuntu Server 20.04 LTS 위에서 돌아가고 있으며, 이걸 기준으로 설명합니다.

## 목차
### Step 0. 서버로 사용할 리눅스 PC 구축
### Step 1. Python, Django, MySQL 설치 및 구성
#### Step 1-1. Python 설치, 그리고 `pip` 설치
#### Step 1-2. `virtualenvwrapper` 설치
#### Step 1-3. 가상환경 생성 및 `Django` 설치
#### Step 1-4. `MySQL` 설치 및 구성/연동
### Step 2. Apache 설치 및 구성/연동
#### Step 2-1. `Apache` 설치 및 구성/연동 프로젝트와 연결/연동
#### Step 2-2. `Let's Encrypt`, `Certbot` 설치 후 `https` 인증서 받기
### Step 3. Histudy 프로젝트 초기 설정
#### Step 3-1. `Google` 계정 로그인 설정하기
#### Step 3-2. 현재 연도/학기 설정하기
### ETC. 이외 확인하면 좋은 것들

---
---

## Step 0. 서버로 사용할 리눅스 PC 구축

GCP, NCP, AWS 등등...을 통해서 Ubuntu 20.04 서버를 만듭니다. 저는 집에 쓰지 않는 노트북에다 설치하였습니다.

Ubuntu 20.04가 설치되었다면, 시스템 업데이트를 진행합니다.

```bash
sudo apt update && sudo apt upgrade
```

업데이트가 끝나면, 프로젝트 폴더를 GitHub Repository에서 clone합니다.

```bash
git clone https://github.com/turbstructor/Histudy.git # forked repository
# git clone https://github.com/dodoyoon/Histudy.git # original repository
```

---

## Step 1. Python, Django, MySQL 설치 및 구성
### Step 1-1. Python 설치, 그리고 `pip` 설치

Ubuntu에는 `python`이 설치되어 있긴 합니다. 그런데 `pip`은 설치되어 있지 않습니다. 그러므로, 다음 명령어를 통하여 `pip`을 설치해 주어야 합니다.

```bash
sudo apt install python3-pip
```

---

### Step 1-2. `virtualenvwrapper` 설치

`histudy` 프로젝트는 가상환경을 사용해 돌아가며, 이 가상환경을 구성하는 데에 있어 `virtualenvwrapper`을 사용합니다. 가상환경을 만들기 앞서, 이 `virtualenvwrapper`를 설치해 줍시다.

```bash
sudo pip3 install virtualenvwrapper
```

#### `virtualenvwrapper`를 사용할 수 있게 설정하기

다음, `virtualenvwrapper`을 사용할 수 있게, `.bashrc` 파일을 열어, 파일 최하단에 아래 내용을 추가해주어야 합니다.

```bash
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh
```

그리고 바뀐 `.bashrc` 내용을 적용하기 위해 - 새로운 가상환경을 만들기 위해 -

```bash
source ~/.bashrc
```

...의 명령어를 실행해줍시다(아니면 나갔다 들어오셔도 됩니다. 쉘만 다시 로드되면 돼요).

---

### Step 1-3. 가상환경 생성 및 `Django` 설치

이제 원하는 이름으로 가상환경을 만들어줍시다.

```bash
# mkvirtualenv <가상환경 이름>
mkvirtualenv histudy
# histutor 파이썬 가상환경으로 activate되어있는 상태
```

`mkvirtualenv`를 거치면 만든 가상환경이 활성화되어 있습니다.

- 참고 : 가상환경 activate / deactivate 하는 법
    - activate : `source ~/.virtualenvs/<가상환경 이름>/bin/activate`
    - deactivate : `deactivate`

이제 clone한 `histudy` 폴더로 들어가, 프로젝트에 필요한 Python 모듈들을 가상환경에 받아줍시다.

```bash
chmod -R 777 ~/Histudy

cd ~/Histudy

# under virtual environment
pip3 install -r new_server_requirements.txt
```

`new_server_requirements.txt` 파일에 보면 필요한 Python 모듈들이 적혀 있으며, 여기에 `Django` 관련된 패키지들도 포함되어 있습니다. 그러니, 위 `pip3` 명령어를 실행했다면 `Django`도 같이 설치될 겁니다.

그 다음, `Django Secret Key`를 생성하여 받아놓도록 합니다. [Djecrety](https://djecrety.ir/)에서 Secret Key를 생성할 수 있습니다.

여기서 생성된 키를 복사하여, Histudy 폴더가 있는 곳(상위 폴더)에 HisSecret 폴더를 만들어, 아래와 같은 내용을 `HisSecret/secret.json`에 저장합시다.

```json
{
    "DJANGO_SECRET_KEY": "<생성된 Django Secret Key>",
    "DB_PASSWORD": "<MySQL에 설정(할)한 root의 비밀번호>"
}
```

- 참고. 아직 `MySQL` 설치가 안 되었다면 - 이 가이드에선 나중에(아랫 부분에) 이 부분을 다룹니다 - 비밀번호를 원하시는 걸로 하셔도 됩니다. 단, 이럴 경우 나중에 `root`의 `MySQL` 비밀번호를 위에서 설정하신 것과 동일하게 만들어주셔야 합니다.

다음으로, `~/Histudy/pystagram/settings.py`에 들어가, `SECRET_BASE` 부분을 이 `secret.json`이 있는 경로로 주도록 합니다(절대경로로 줘야 함).

```python
SECRET_BASE = '/home/<사용자 이름>/HisSecret'
```

---

### Step 1-4. `MySQL` 설치 및 구성/연동

`apt`로 MySQL(`mysql-server`)를 서버에다 설치해 줍니다.

```bash
sudo apt install mysql-server
```

일단 설치 중에는 비밀번호를 요구하지 않습니다만, 혹여나 초기 설정이 돌아갈 때 비밀번호를 요구할 경우 `1-3`에서 `HisSecret/secret.json`에다 설정한 `DB_PASSWORD` 항목의 그것과 동일하게 입력해주시면 됩니다.

#### `root` 비밀번호 변경

그 다음, 기본값으로 설정되어 있는 root의 비밀번호를 바꾸기 위해서 `mysql`을 실행, 아래의 명령어를 입력하여 비밀번호를 변경해줍니다(안의 'DB_PASSWORD'는 `1-3`의 `DB_PASSWORD`와 동일합니다).

```bash
sudo mysql

alter user 'root'@'localhost' identified with mysql_native_password by 'DB_PASSWORD';
```

#### `default characterset` 변경

root의 비밀번호 설정이 끝났다면, `MySQL`이 한글로 된 데이터를 저장할 수 있도록 `default character set`을 변경해줘야 합니다.

`/etc/mysql/my.cnf` 파일을 편집기로 열어 그 아래에 아래의 내용을 추가해줍니다.

```sql
[client]
default-character-set=utf8

[mysql]
default-character-set=utf8

[mysqld]
collation-server = utf8_unicode_ci
init-connect='SET NAMES utf8'
character-set-server = utf8
```

변경된 `my.cnf`를 저장한 후, `MySQL`을 재시작해 줍니다.

```bash
sudo systemctl restart mysql # sudo service mysql restart 도 가능
```

정상적으로 재시작이 되었다면 딱히 다른 메세지 없이 넘어갈 겁니다. 그렇게 됐다면, `MySQL`을 다시 실행하여 `status` 명령어를 입력, `character set`이 변경되었는지 확인해주세요.

```sql
mysql -u root -p

mysql> status
```

`character set`이 성공적으로 변경되었다면 - 반드시 변경되었는지 확인하고 넘어가주세요, 안 그러면 데이터베이스에 한글 내용이 안 들어갈 거에요 - 'study'라는 이름의 DB를 생성해 줍시다.

```sql
mysql> create database study;
```

저는 여기까지 에러가 일어나진 않았습니다만, 혹여나 일어났다면... [https://dodormitory.tistory.com/8](https://dodormitory.tistory.com/8) 링크로 가서 4 - 에러 수정 부분을 참고하여 고쳐주세요.


다음으로는 다운로드 받은 django project에서 방금 생성한 데이터베이스에 테이블들을 생성하는 과정입니다.

[manage.py](http://manage.py) 파일이 있는 디렉토리로 이동, `migrate` 명령어로 테이블을 생성해줍시다.

```bash
cd ~/Histudy

python3 manage.py makemigrations

python3 manage.py migrate

# static file을 .static_root 디렉토리에 모으는 명령어
python3 manage.py collectstatic
```

이 과정을 거치면 아까 생성했던 `study` 데이터베이스에 프로젝트에서 사용하는 `table`들이 만들어진 걸 볼 수 있습니다.

```sql
mysql -u root -p

mysql> use study;
mysql> show tables;
```

---
---

## Step 2. Apache 설치 및 구성/연동
### Step 2-1. `Apache` 설치 및 구성/연동 프로젝트와 연결/연동

#### `Apache` 설치

가상환경에서 우선 빠져나옵니다(`deactivate` 로 가능).

그 다음, `apache`와 `apache`의 `wsgi`(python3 사용) 모듈인 `libapache2-mod-wsgi-py3`를 설치해 줍니다(`libapache2-mod-wsgi`는 `python2`를 사용하므로 `python3`를 사용하는 경우엔 설치하면 안 됩니다).

```bash
sudo apt-get install apache2                  # apache2 설치
sudo apt-get install libapache2-mod-wsgi-py3
```

#### `apache` 설정 #1
`apache` 설치가 완료되었다면, `/etc/apache2/sites-available/000-default.conf`을 편집기로 열어 아래와 같이 수정해줍시다.

- `000-default.conf`:

```bash
<VirtualHost *:80>

ServerAdmin webmaster@localhost

DocumentRoot /var/www/html

ErrorLog ${APACHE_LOG_DIR}/error.log

CustomLog ${APACHE_LOG_DIR}/access.log combined

<Directory {wsgi.py가 있는 디렉토리 주소}>

	<Files wsgi.py>

		Require all granted

	</Files>

</Directory>

Alias {settings.py 속 STATIC_URL 변수 값} {settings.py 속 STATIC_ROOT 디렉토리의 절대주소}
<Directory {settings.py 속 STATIC_ROOT 디렉토리의 절대주소}>
        Require all granted
</Directory>

WSGIDaemonProcess tutor python-path={manage.py가 있는 디렉토리의 절대주소} python-home={이 프로젝트를 돌릴 때에 사용하는 가상환경 - 이전에 django를 설치해 놓은 가상환경 - 의 절대주소}
WSGIProcessGroup {프로젝트이름}
WSGIScriptAlias / {wsgi.py가 있는 디렉토리의 주소/wsgi.py}

</VirtualHost>
```

- `000-default.conf`(Histudy에 맞는 설정):

```bash
<VirtualHost *:80>

# The ServerName directive sets the request scheme, hostname and port that
# the server uses to identify itself. This is used when creating
# redirection URLs. In the context of virtual hosts, the ServerName
# specifies what hostname must appear in the request's Host: header to
# match this virtual host. For the default virtual host (this file) this
# value is not decisive as it is used as a last resort host regardless.
# However, you must set it for any further virtual host explicitly.
#ServerName www.example.com

ServerAdmin webmaster@localhost
DocumentRoot /var/www/html

# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
# error, crit, alert, emerg.
# It is also possible to configure the loglevel for particular
# modules, e.g.
#LogLevel info ssl:warn

ErrorLog ${APACHE_LOG_DIR}/error.log
CustomLog ${APACHE_LOG_DIR}/access.log combined

<Directory /home/<사용자 이름>/Histudy/pystagram>
	<Files wsgi.py>
		Require all granted
	</Files>
</Directory>

# Static file(js, css 등등)이 들어있는 폴더에 Apache가 접근하게 함
Alias /static /home/<사용자 이름>/Histudy/staticfiles
<Directory /home/<사용자 이름>/Histudy/staticfiles>
        Require all granted
</Directory>

WSGIDaemonProcess histudy python-path=/home/<사용자 이름>/Histudy python-home=/home/<사용자 이름>/.virtualenvs/histudy
WSGIProcessGroup histudy
WSGIScriptAlias / /home/<사용자 이름>/Histudy/pystagram/wsgi.py

</VirtualHost>
```

이후 가상환경을 다시 활성화하여, 파이썬 모듈 `uwsgi`를 `pip`을 통하여 설치해 줍니다.

```bash
pip install uwsgi
```

uwsgi 가 설치되지 않는다면 [pip3 install uwsgi 설치 에러 Failed building wheel for uwsgi](https://integer-ji.tistory.com/294) 링크의 블로그를 참고해 주세요.

#### `apache` 설정 #2

`django`에서 사용하는 포트가 있는데, 이걸 개방해줘야 합니다. 먼저 `ufw`로 방화벽에서 해당 포트를 개방하고, `iptables`로 해당 포트를 개방합니다. 마지막으로 테스트로 서버를 실행시켜서 해당 포트가 열린 것을 확인합니다.

```bash
sudo ufw allow 8000

sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT

python manage.py runserver 0.0.0.0:8000
```

`<서버 IP 주소>:8000`으로 접속해서 Histudy 초기 화면이 떠야 합니다.

그 다음, `/etc/apache2/ports.conf` 파일을 열고, 위에서 열게된 포트 8000을 추가합시다. Listen 80밑에 Listen 8000을 추가하면 됩니다.

```bash
Listen 80
Listen 8000 # newly added
```

파일 수정이 완료되었다면, `apache` 서비스를 재시작해 줍시다.

```bash
sudo systemctl restart apache2 # sudo service apache2 restart도 가능
```

이제 `Server_Ip_Address:8000`으로 접속하면 histutor가 성공적으로 보이는 것을 볼 수 있다.

---

### Step 2-2. `Let's Encrypt`, `Certbot` 설치 후 `https` 인증서 받기

외부에서의 접속을 위해 도메인을 구하셨으면 이 과정을 진행해주시면 됩니다.

[Let's Encrypt를 사용하여 HTTPS 설정하기](https://dodormitory.tistory.com/11) 링크의 블로그 포스트를 참고해 주세요.

---
---

## Step 3. Histudy 프로젝트 초기 설정
### Step 3-1. `Google` 계정 로그인 설정하기

[[Django] Google 계정으로 로그인하기 (로컬 서버 + 실제 서버)](https://dodormitory.tistory.com/9) 링크의 블로그 포스트를 참고해 주세요.

`Google OAuth`에서 연결한 도메인 주소를 등록하고 `Django Admin` 사이트에서 `Google Social Application`을 활성화해줘야 합니다.

---

### Step 3-2. 현재 연도/학기 설정하기

Histudy를 사용하기 위해선 현재 연도와 학기를 설정해주어야 합니다. 이를 위해선 관리자로 로그인할 필요가 있는데,

```bash
cd ~/Histudy/ # manage.py가 있는 디렉토리로 이동
python3 manage.py createsuperuser
```

로 관리자를 만들어주세요. 이후 `https://{histudy ip address 또는 domain name}/admin` 으로 접속하면 관리자 페이지가 나옵니다.
관리자로 로그인 후, `https://(histudy ip address 또는 domain name)/set_current (이번 년도 & 학기 지정하기)로 가서 현재 년도와 학기를 지정해줍시다.

---
---

### ETC. 이외 확인하면 좋은 것들

#### 개발 팁
**1. Super User 생성하기**

장고의 관리자 계정을 생성하기 위해서는 

	1. 먼저 가상환경을 켜고: source ~/.virtualenvs/histudy/bin/activate
	2. manage.py 파일이 있는 디렉토리로 이동한다. : cd ~/Histudy
	3. Super User를 생성한다. : python3 manage.py createsuperuser

이 과정을 거치면 Super User가 생성되고 장고 관리자 페이지(주소: Histutor_domain/admin)로 접속할 수 있게 된다.



**2. 더 자세한 에러메시지 보기**

서버에서 문제가 생기면 Server Internal Error만 달랑 떠서 문제의 원인을 정확히 알 수 없다.

그럴 때, ~/Histudy/pystagram/settings.py 파일에서 'DEBUG' 라는 변수를 True로 변경하면 됩니다.

하지만 실제 서비스에서는 보안상의 이유로 DEBUG는 False 이어야 합니다. 

따라서 에러를 고친 다음에는 DEBUG를 False로 변경해 주시기 바랍니다.



**3. Static File을 수정하거나 추가한 경우**

장고에서는 Static File(css, js) 들을 한 곳에 모아두고 사용한다. 

그래서 수정되거나 추가된 Static File들은 해당 디렉토리에 추가가 되어야 한다. 

이를 추가하기 위한 과정은 다음과 같다. 

	1. 먼저 가상환경을 켜고: source ~/.virtualenvs/histudy/bin/activate
	2. manage.py 파일이 있는 디렉토리로 이동한다. : cd ~/Histudy
	3. collectstatic 명령어를 실행한다. : python3 manage.py collectstatic

그러면 'This will overwrite existing files!' 와 같은 경고문이 뜨는데 그냥 yes를 치면 된다.



**4. 서버에서 자주 사용하는 명령어**

```bash
# Apache 관련
1. 에러로그파일 위치: /var/log/apache2/error.log
2. 아파치 Config파일 위치: /etc/apache2/sites-available/000-default-le-ssl.conf
3. 아파치 재시작: sudo service apache2 restart

```


### Reference

[https://dodormitory.tistory.com/](https://dodormitory.tistory.com/2)

[http://wanochoi.com/?p=3575](http://wanochoi.com/?p=3575)

[https://calvinjmkim.tistory.com/23](https://calvinjmkim.tistory.com/23)
