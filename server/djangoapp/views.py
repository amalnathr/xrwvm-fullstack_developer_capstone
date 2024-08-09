from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review
from .populate import initiate
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    """Handle user login."""
    data = json.loads(request.body)
    username = data.get('userName')
    password = data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
    else:
        response_data = {
            "userName": username,
            "status": "Authentication Failed"
        }

    return JsonResponse(response_data)


def logout_user(request):
    """Handle user logout."""
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    """Handle user registration."""
    data = json.loads(request.body)
    username = data.get('userName')
    password = data.get('password')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')

    username_exist = User.objects.filter(username=username).exists()

    if not username_exist:
        user = User.objects.create_user(
            username=username, first_name=first_name, last_name=last_name,
            password=password, email=email
        )
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
    else:
        response_data = {
            "userName": username,
            "error": "Already Registered"
        }

    return JsonResponse(response_data)


def get_dealerships(request, state="All"):
    """Retrieve list of dealerships."""
    endpoint = (
        "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    )
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """Retrieve reviews for a specific dealer."""
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)

        if reviews:
            for review in reviews:
                try:
                    response = analyze_review_sentiments(review['review'])
                    review['sentiment'] = response.get('sentiment', 'unknown')
                except KeyError:
                    review['sentiment'] = 'unknown'
                    logger.error("KeyError: 'sentiment' not found in the response")
                except Exception as e:
                    review['sentiment'] = 'unknown'
                    logger.error(f"Error analyzing sentiment: {e}")

            return JsonResponse({"status": 200, "reviews": reviews})
        else:
            logger.error(f"No reviews found for dealer_id: {dealer_id}")
            return JsonResponse({"status": 404, "message": "No reviews found"})
    else:
        logger.error("Bad Request: dealer_id is missing")
        return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_details(request, dealer_id):
    """Retrieve details for a specific dealer."""
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        response_data = {"status": 200, "dealer": dealership}
        return JsonResponse(response_data)
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    """Add a review if the user is authenticated."""
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.error(f"Error in posting review: {e}")
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review"
            })
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})


def get_cars(request):
    """Retrieve a list of cars."""
    count = CarMake.objects.count()
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        }
        for car_model in car_models
    ]

    return JsonResponse({"CarModels": cars})
