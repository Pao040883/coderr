from rest_framework.response import Response
from rest_framework import status
from app_offers.models import DetailOffer

def prepare_order_data(request):
    """
    Validates the request and returns prepared order data or a Response with an error.
    """
    offer_detail_id = request.data.get("offer_detail_id")

    if not offer_detail_id:
        return Response({"error": "offer_detail_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        offer_detail_id = int(offer_detail_id)
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid offer_detail_id. Must be a valid integer."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        offer = DetailOffer.objects.select_related("offer__user").get(id=offer_detail_id)
    except DetailOffer.DoesNotExist:
        return Response({"error": "OfferDetail not found"}, status=status.HTTP_404_NOT_FOUND)

    return {
        "customer_user": request.user.id,
        "business_user": offer.offer.user.id,
        "title": offer.offer.title,
        "revisions": offer.revisions,
        "delivery_time_in_days": offer.delivery_time_in_days,
        "price": offer.price,
        "features": offer.features,
        "offer_type": offer.offer_type,
        "status": "in_progress",
    }
