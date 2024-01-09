from flask import Blueprint, request, jsonify
from src.database import Bookmark, db
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime

bookmarks = Blueprint("bookmarks",__name__,url_prefix="/api/v1/bookmarks")

@bookmarks.route('/',methods = ['POST','GET'])
@jwt_required()
def handle_bookmarks():
    current_user_id = get_jwt_identity()

    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), 404

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), 409

        current_time = datetime.utcnow()
        bookmark = Bookmark(
            url=url,
            body=body,
            user_id=current_user_id, 
            created_at=current_time,
        )
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'created_at': bookmark.created_at,
            'check_updated_at': bookmark.check_updated_at
        }), 201


    else:

        page = request.args.get('page',1,type=int) 
        per_page = request.args.get('per_page',5,type=int)

        bookmark_pagination = Bookmark.query.filter_by(user_id=current_user_id).paginate(page=page,per_page=per_page)

        data = []

        for bookmark in bookmark_pagination.items:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visit': bookmark.visits,
                'created_at': bookmark.created_at,
                'check_updated_at': bookmark.check_updated_at
            })

            # Pagination metadata

        meta = {
            'page':bookmark_pagination.page,
            'pages':bookmark_pagination.pages,
            'total_count': bookmark_pagination.total, 
            'prev_page':bookmark_pagination.prev_num, 
            'next_page':bookmark_pagination.next_num,
            'has_next':bookmark_pagination.has_next, 
            'has_prev':bookmark_pagination.has_prev, 

        }

        return jsonify({'data': data, 'meta': meta }), 

                                        # Retrieving The Records

@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id = current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message": f"Bookmark with the following id does not exist: '{id}'"
        }), 400
    
    return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'created_at': bookmark.created_at,
            'check_updated_at': bookmark.check_updated_at
        }), 200


                                # Editing The Records 
@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def editbookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id = current_user, id = id).first()
    if not bookmark:
        return jsonify({
            'message':'Item not found'
        })
    body = request.get_json().get('body','')
    url = request.get_json().get('url','')

    if not validators.url(url):
        return jsonify({
            "error":"Invalid URL"
            }), 400   # bad request
    

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'body': bookmark.body,
        'visit': bookmark.visits,
        'created_at': bookmark.created_at,
        'check_updated_at': bookmark.check_updated_at

    })

@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id = current_user, id = id).first()
    if not bookmark:
        return jsonify({'message':'item doesnot exist'}), 404   
    
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({
        'Message':'Bookmark deleted successfully',
    }), 204

@bookmarks.get("/stats")
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()
    data = []
    
    items = Bookmark.query.filter_by(user_id = current_user).all() 
    for item in items:
        new_link = {
            "visits":item.visits,
            "urls":item.url,
            "id":item.id,
            "short_url":item.short_url
        }
        data.append(new_link)

    return jsonify({"data":data})   , 200