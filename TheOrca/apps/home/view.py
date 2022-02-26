import re
from datetime import date

from flask import Blueprint, request, render_template, redirect, url_for, session
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from apps.users.models import User, Censor
from apps.works.models import Works
from extends import db

home_bp = Blueprint('home', __name__, url_prefix='/')


# length of the password 8~20
def password_validate(password):
    return 8 <= len(password) <= 20


# format of the email address
def emailaddr_validate(emailaddr):
    # test data:
    # email = '1306516881@qq.com'
    # email1 = 'sadad'
    # email2 = '1306516881qq.com'
    # email3 = '1306516881@qq.edu.cn.cn'
    # email4 = 'jiang.yilong@icloud.com'
    # email5 = 'jiangyilong@163.com'
    # email6 = 'jiang.yilong@ncepu.edu.cn'

    # 但是如果是asdasdasd@qq.co 的话也是可以通过的。。。解决？？？

    email_format = '[a-zA-Z0-9_\-]+[\.a-zA-Z0-9_\-]+@[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]{1,}[\.a-zA-Z0-9]{0,1}$'
    email_format_edu = '[a-zA-Z0-9_\-]+[\.a-zA-Z0-9_\-]+@[a-zA-Z0-9_\-]+\.edu([\.a-zA-Z0-9]{,5})$'

    res = None

    if re.match(email_format, emailaddr) is not None:
        res = re.match(email_format, emailaddr)

    if re.match(email_format_edu, emailaddr) is not None:
        res = re.match(email_format_edu, emailaddr)

    return res


# confirm the validation of the username
def username_validate(username):
    # test data:
    # username = 'Jason Jiang'
    # username1 = 'Jason123'
    # username2 = 'Jason@'
    # username3 = 'Jason!'
    # username4 = 'Jason?'
    # username5 = 'JJJJJJJJJJJJJJJJJJJJJ'
    # username6 = 'JasonJiang'
    # username7 = '王大佬几吊滴'
    # username8 = '艾耶两个王大佬几吊滴大佬就是大佬嘞'
    if len(username) < 2 or len(username) > 12:
        return False

    # check the duplication of the username
    if User.query.filter_by(username=username).first():
        return False

    # \W matches any character which is not a word character (the opposite of [a-zA-Z0-9_])
    if re.search("\W", username):
        return False

    return True


@home_bp.route('/')
def index():
    return redirect('/welcome')


@home_bp.route('/welcome')
def welcome():
    return render_template('home/welcome.html')


@home_bp.route('/orca')
def orca():
    # cookie 方式获取
    userid = request.cookies.get('userid')

    # get the works_list
    works_list = Works.query.filter(Works.checked == 1)
    works_list = works_list[0:5]

    works_editor_dict = {}
    works_coverage_dict = {}
    works_post_time = {}
    for works in works_list:
        works_editor_dict[works.id] = User.query.get(Works.query.get(works.id).editor_id)
        works_coverage_dict[works.id] = list(eval(works.photos.strip('"')).values())[0]
        print('>>>>>>>>')
        print(works_coverage_dict[works.id])
        print('>>>>>>>>')
        works_post_time[works.id] = Works.query.get(works.id).post_time.strftime("%Y-%m-%d")
        print('>>>>>>>>>>>>date>>>>>>>>>')
        print('>>>>>>>>>>>>date>>>>>>>>>')
        print('>>>>>>>>>>>>date>>>>>>>>>')
        print(works_post_time[works.id])
        print('>>>>>>>>>>>>date>>>>>>>>>')
        print('>>>>>>>>>>>>date>>>>>>>>>')
        print('>>>>>>>>>>>>date>>>>>>>>>')

    print('>>>>>>>photos_dict>>>>>>>')
    print(works_coverage_dict)
    print('>>>>>>>photos_dict>>>>>>>')

    if userid:
        user = User.query.get(userid)
        return render_template('home/orca.html',
                               user=user,
                               works_list=works_list,
                               works_editor_dict=works_editor_dict,
                               works_coverage_dict=works_coverage_dict,
                               works_post_time=works_post_time)
    else:
        return render_template('home/orca.html',
                               works_list=works_list,
                               works_editor_dict=works_editor_dict,
                               works_coverage_dict=works_coverage_dict,
                               works_post_time=works_post_time)


# here we implement register, login
@home_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        emailaddr = request.form.get('emailaddr')
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        if not emailaddr_validate(emailaddr):
            # pop window???
            return '邮箱格式错误，请重新注册'

        if not username_validate(username):
            # pop window???
            return '用户名不合格或已重复，请重新注册'

        if not password_validate(password):
            # pop window???
            return '密码长度不合格，请重新注册'

        if password == repassword:
            user = User()
            user.username = username
            user.password = generate_password_hash(password)
            user.emailaddr = emailaddr

            db.session.add(user)
            db.session.commit()

            # return '注册成功'
            response = redirect(url_for('home.orca'))
            response.set_cookie('userid', str(user.id), max_age=1800)  # half an hour
            return response
        else:
            return '两次输入的密码不一致，请重新注册'

    return render_template('home/register.html')


@home_bp.route('/login', methods=['GET', 'POST'])
def login():
    # user login
    if request.method == 'POST':
        is_censor = int(request.form.get('is_censor'))
        print('>>>>>>>')
        print(is_censor)
        print('>>>>>>>')

        if is_censor == 0:  # 普通用户
            name_or_email = request.form.get('name_or_email')
            password = request.form.get('password')

            user = User.query.filter(or_(User.username == name_or_email, User.emailaddr == name_or_email)).first()

            if user:
                if check_password_hash(user.password, password):
                    # 1. cookie 机制实现
                    response = redirect(url_for('home.orca'))
                    response.set_cookie('userid', str(user.id), max_age=1800)  # half an hour
                    return response

                else:
                    return render_template('home/login.html', message='用户名或密码错误')
            else:
                return render_template('home/login.html', message='用户名或密码错误')

        else:  # 审查员
            name_or_email = request.form.get('name_or_email')
            password = request.form.get('password')

            censor = Censor.query.filter(
                or_(Censor.censor_name == name_or_email, Censor.emailaddr == name_or_email)).first()

            if censor:
                if check_password_hash(censor.password, password):

                    unchecked_works_list = Works.query.filter(Works.checked == 0)

                    works_editor_dict = {}
                    works_coverage_dict = {}
                    for works in unchecked_works_list:
                        works_editor_dict[works.id] = User.query.get(Works.query.get(works.id).editor_id)
                        works_coverage_dict[works.id] = list(eval(works.photos.strip('"')).values())[0]

                    response = redirect(url_for('censors.censor_check'))
                    response.set_cookie('userid', str(censor.id), max_age=1800)  # half an hour
                    return response

                else:
                    return render_template('home/login.html', message='用户名或密码错误')

            else:
                return render_template('home/login.html', message='用户名或密码错误')

    return render_template('home/login.html')


@home_bp.route('/logout')
def logout():
    response = redirect(url_for('home.orca'))
    response.delete_cookie('userid')
    return response
