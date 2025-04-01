from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tickets.views import AgentTicketAssignmentView, AgentSellTicketView, AdminTicketViewSet

router = DefaultRouter()
router.register(r'admin/tickets', AdminTicketViewSet, basename='admin-tickets')

urlpatterns = [
    path('agent/tickets/assign/', AgentTicketAssignmentView.as_view(), name='agent-assign-tickets'),
    path('agent/tickets/sell/<int:ticket_id>/', AgentSellTicketView.as_view(), name='agent-sell-ticket'),
]

urlpatterns += router.urls
