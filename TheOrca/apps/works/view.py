from flask import Blueprint, render_template

from apps.users.models import User
from apps.works.models import Works, Comment

works_bp = Blueprint('works', __name__, url_prefix='/works')


@works_bp.route('/<id>')
def details(id):
    """
    :param id: id of the works
    :return: the list of the addrs
    """
    # get the works by the id
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
    # photos_addrs = []
    # for photos_addrs_origin in photos_addrs_origin_list:
    #     photos_addrs.append(photos_addrs_origin.strip("/"))

    # print(photos_addrs)

    # get the comment list
    comment_list = Comment.query.filter(Comment.works_id == id).all()

    # get the (comment, user) list
    comment_user_list = []
    for comment in comment_list:
        comment_user = User.query.get(comment.user_id)
        comment_user_list.append((comment.content, comment_user.username))

    return render_template('works/works.html',
                           works_title=works_title,
                           works_description=works_description,
                           post_time=post_time,
                           text=text,
                           editor_name=editor_name,
                           photos_addrs=photos_addrs,
                           comment_user_list=comment_user_list)
