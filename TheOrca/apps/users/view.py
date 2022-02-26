import json
import os
import random
from datetime import datetime

from flask import Blueprint, request, render_template, flash, redirect, url_for
from pypinyin import lazy_pinyin
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename

from apps.users.models import User, Censor
from apps.works.models import Works, Comment
from extends import db

user_bp = Blueprint('users', __name__, url_prefix='/users')
censor_bp = Blueprint('censors', __name__, url_prefix='/censors')


def get_info_of_works(works_list):
    # get the list of the works_id
    works_id_list = []
    for works in works_list:
        works_id_list.append(works.id)

    # get the list of the works_title
    works_title_list = []
    for works in works_list:
        works_title_list.append(works.title)

    # get the list of the works_description
    works_description_list = []
    for works in works_list:
        works_description_list.append(works.description)

    # get the list of the works_posttime
    works_posttime_list = []
    for works in works_list:
        works_posttime_list.append(works.post_time)

    return works_id_list, works_title_list, works_description_list, works_posttime_list


@user_bp.route('/<id>')
def user_details(id):
    """
    the home page of each user
    :param id: the id of the user
    """
    user = User.query.get(id)

    print('>>>>>>>>>>user>>>>>>>>')
    print(user)
    print('>>>>>>>>>>user>>>>>>>>')

    user_name = user.username
    user_email = user.emailaddr

    # get the works of the user that is posted
    works_list = Works.query.filter(and_(Works.editor_id == id, Works.checked == 1)).all()

    works_id_list, works_title_list, works_description_list, works_posttime_list = \
        get_info_of_works(works_list)

    return render_template('user/details.html',
                           user_name=user_name,
                           user_email=user_email,
                           works_id_list=works_id_list,
                           works_title_list=works_title_list,
                           works_description_list=works_description_list,
                           works_posttime_list=works_posttime_list)


@user_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    # cookie 方式获取
    userid = request.cookies.get('userid')

    # 处于登陆则继续，否则去登陆
    if userid:
        if request.method == 'POST':
            user = User.query.get(userid)

            title = request.form.get('title')
            description = request.form.get('description')
            text = request.form.get('text')

            file_list = request.files.getlist('files')

            print(file_list)

            validate_types = ['png', 'jpeg', '.JPEG', 'jpg']

            if not file_list:
                return '上传失败，请至少选择一张图片'

            for file in file_list:
                filetype = file.filename.split('.')[-1]
                if filetype not in validate_types:
                    return '上传失败，仅限于png, jpeg, jpg文件'

            # 给作品一个随机id
            works_id = random.randint(0, 100000)
            works_db = Works.query.get(works_id)

            # 只到数据库没有该标号的时候退出循环
            while works_db:
                works_id = random.randint(0, 100000)
                works_db = Works.query.get(works_id)

            # 图片存放路径
            save_dir = 'static/photos/user' + str(userid) + '/works' + str(works_id) + '/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            file_urls_list = []
            for file in file_list:
                filename = secure_filename(''.join(lazy_pinyin(file.filename)))

                # 保存图片
                file.save(os.path.join(save_dir, filename))

                # 记录每张图片的路径
                file_urls_list.append(os.path.join('../../', save_dir, filename))

                # 调试语句
                print(filename)
                print(os.path.join(save_dir, filename))
                print('成功上传')

            db_photos_dict = {}
            i = 1
            for file_url in file_urls_list:
                db_photos_dict[i] = file_url
                i += 1

            db_photos_json = json.dumps(db_photos_dict)

            works = Works(id=works_id,
                          title=title,
                          description=description,
                          text=text,
                          upload_time=datetime.now(),
                          photos=db_photos_json,
                          editor_id=int(userid),
                          checked=0)

            db.session.add(works)
            db.session.commit()

            # 调试语句
            print(db_photos_dict)
            print('>>>>>>>>')
            print(db_photos_json)
            print(len(file_urls_list))

            return render_template('user/upload.html', msg='上传成功')

        else:
            return render_template('user/upload.html', msg='上传失败')

    else:
        return render_template('home/login.html', msg='投稿前需登录')


@user_bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_condition = request.form.get('search_condition')

        print('>>>>>>search_condition>>>>>>')
        print('>>>>>>search_condition>>>>>>')
        print(search_condition)
        print('>>>>>>search_condition>>>>>>')
        print('>>>>>>search_condition>>>>>>')

        users_list = User.query.filter(or_(User.id == search_condition, User.username == search_condition)).all()
        works_list = Works.query.filter(or_(Works.id == search_condition, Works.title == search_condition)).all()
        # works_list = Works.query.filter(or_(Works.id == search_condition, Works.title == search_condition), Works.checked == 1).all()

        works_editor_dict = {}
        works_coverage_dict = {}
        for works in works_list:
            works_editor_dict[works.id] = User.query.get(Works.query.get(works.id).editor_id)
            works_coverage_dict[works.id] = list(eval(works.photos.strip('"')).values())[0]
            print('>>>>>>>>')

        return render_template('user/search_res.html',
                               users_list=users_list,
                               works_list=works_list,
                               search_condition=search_condition,
                               works_editor_dict=works_editor_dict,
                               works_coverage_dict=works_coverage_dict)

    return render_template('home/orca.html')


@censor_bp.route('/<id>')
def censor_details(id):
    """
    the home page of each censor
    :param id:
    """
    censor = Censor.query.get(id)

    unchecked_works_list = Works.query.filter(Works.checked == 0).all()

    unchecked_works_id_list, unchecked_works_title_list, \
    unchecked_works_description_list, unchecked_works_posttime_list = \
        get_info_of_works(unchecked_works_list)

    return render_template('censor/check.html',
                           censor=censor,
                           unchecked_works_list=unchecked_works_list,
                           unchecked_works_id_list=unchecked_works_id_list,
                           unchecked_works_title_list=unchecked_works_title_list,
                           unchecked_works_description_list=unchecked_works_description_list,
                           unchecked_works_posttime_list=unchecked_works_posttime_list)


#  all the unchecked works page
@censor_bp.route('/check')
def censor_check():
    censor_id = request.cookies.get('userid')
    unchecked_works_list = Works.query.filter(Works.checked == 0).all()

    works_editor_dict = {}
    works_coverage_dict = {}
    for works in unchecked_works_list:
        works_editor_dict[works.id] = User.query.get(Works.query.get(works.id).editor_id)
        works_coverage_dict[works.id] = list(eval(works.photos.strip('"')).values())[0]

    return render_template('censor/check.html',
                           unchecked_works_list=unchecked_works_list,
                           works_editor_dict=works_editor_dict,
                           works_coverage_dict=works_coverage_dict)


#  the page of each unchecked works
@censor_bp.route('/works_check/<id>')
def works_check(id):

    works = Works.query.get(id)

    # get the details of the works
    photos_dict = eval(works.photos.strip('"'))
    works_title = works.title
    works_description = works.description
    post_time = works.post_time
    text = works.text
    editor_id = works.editor_id

    # get the editor name
    editor = User.query.get(editor_id)
    editor_name = editor.username

    # get the photos addresses list
    photos_addrs = list(photos_dict.values())
    print('>>>>>>>photo_addrs>>>>>>>')
    print(photos_addrs)
    print('>>>>>>>photo_addrs>>>>>>>')

    # get the comment list
    comment_list = Comment.query.filter(Comment.works_id == id).all()

    # get the (comment, user) list
    comment_user_list = []
    for comment in comment_list:
        comment_user = User.query.get(comment.user_id)
        comment_user_list.append((comment.content, comment_user.username))

    return render_template('works/works_check.html',
                           works_id=id,
                           works_title=works_title,
                           works_description=works_description,
                           post_time=post_time,
                           text=text,
                           editor_name=editor_name,
                           photos_addrs=photos_addrs,
                           comment_user_list=comment_user_list)


#  process of the check
@censor_bp.route('/works/works_check', methods=['GET', 'POST'])
def check_check():
    censor_id = request.cookies.get('userid')

    if censor_id is None:
        return render_template('home/login.html', msg='审查员未登录')

    if request.method == 'POST':

        checked_works_id = request.form.get('checked')
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')
        print(checked_works_id.split('_', 1))
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>check_works>>>>>>>>>>>>>>>>>')

        checked = int(checked_works_id.split('_', 1)[0])
        works_id = int(checked_works_id.split('_', 1)[1])

        works = Works.query.get(works_id)

        print('>>>>>>>>>>>>>>>>>>>>>check>>>>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>>>>>>check>>>>>>>>>>>>>>>>>>>>')
        print('censor_id', censor_id)
        print('works_id', works_id)
        print('works', works)
        print('checked', checked)
        print('>>>>>>>>>>>>>>>>>>>>>check>>>>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>>>>>>check>>>>>>>>>>>>>>>>>>>>')

        if checked == 1:
            works.checked = checked
            works.censor_id = censor_id
            works.post_time = datetime.now()
            db.session.commit()
        else:
            works.checked = checked
            works.censor_id = censor_id
            db.session.commit()

        return redirect(url_for('censors.censor_check'))

    return render_template('censor/check.html', msg='操作失败')
