from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'comment': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    @jwt_required
    def post(self):
        """Register a new review"""
        review = api.payload
        place = facade.get_place(review['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404
        # users can only review places they do not own
        current_user = get_jwt_identity()
        if place.owner == current_user['id']:
            return {'error': 'You cannot review your own place'}
        # users can only create one review per place
        place_reviews = facade.get_reviews_by_place(review['place_id'])
        for existing_review in place_reviews:
            if existing_review.user_id == current_user['id']:
                return {'error': 'You have already reviewed this place'}, 400
        try:
            new_review = facade.create_review(review)
            return {'id': new_review.id, 'comment': new_review.comment, 'rating': new_review.rating, 'user_id': new_review.user_id, 'place_id': new_review.place_id}, 201
        except ValueError:
            return {'error': 'Invalid input data'}, 400


    @api.response(200, 'List of reviews retrieved successfully')
    @api.response(404, 'No reviews found')
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        if not reviews:
            return {'error': 'No reviews found'}, 404
        return [{'id': review.id, 'comment': review.comment, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id} for review in reviews], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return {'id': review.id, 'comment': review.comment, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id}, 200
    
    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @api.response(500, 'Failed to update this review')
    @jwt_required()
    def put(self, review_id):
        """Update a review's information by ID"""
        review = facade.get_review(review_id)
        # check if review exists in the database
        if not review:
            return {'error': 'Review not found'}, 404

        current_user = get_jwt_identity()
        # users can only modify reviews they created
        if review.user_id != current_user['id']:
            return {'error': 'Unauthorized action'}, 403

        review_data = api.payload
        review.comment = review_data.get('comment', review.comment)
        review.rating = review_data.get('rating', review.rating)
        # update review in the database
        updated_review = facade.update_review(review.id, {
            'comment': review.comment,
            'rating': review.rating,
        })
        # check if database issue occured when updating review
        if not updated_review:
            return {'error': 'Failed to update this review'}, 500
        return {'id': review.id, 'comment': review.comment, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id}, 200

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @api.response(500, 'Failed to delete this review')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        review = facade.get_review(review_id)
        # check if review exists in the database
        if not review:
            return {'error': 'Review not found'}, 404
        # users can only delete reviews they created expect if is_admin=True
        current_user = get_jwt_identity()
        if review.user_id != current_user['id'] and not current_user.get('is_admin'):
            return {'error': 'Unauthorized action'}, 403
        # delete review in the database
        deleted_review = facade.delete_review(review_id)
        # check if database issue occured when deleting review
        if not deleted_review:
            return {'error': 'Failed to delete this review'}, 500
        return {'message': 'Review deleted successfully'}, 200

@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        reviews = facade.get_reviews_by_place(place_id)
        if not reviews:
            return {'error': 'No reviews found for this place'}, 404
        return [{'id': review.id, 'comment': review.comment, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id} for review in reviews], 200