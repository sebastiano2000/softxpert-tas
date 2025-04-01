from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Ticket
from .serializers import TicketSerializer
from django.http import JsonResponse

# Custom permissions
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class IsAgentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_agent

# Admin endpoints for full CRUD operations
class AdminTicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('created_at')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

# Agent endpoint for ticket assignment

class AgentTicketAssignmentView(APIView):
    """
    GET: Returns a batch of up to 15 unsold tickets assigned to the requesting agent.
         If the agent has fewer than 15 tickets, new tickets are assigned (if available).
    """
    def get(self, request, *args, **kwargs):
        agent = request.user
        # Retrieve unsold tickets already assigned to the agent, ordered by creation time.
        current_tickets = list(Ticket.objects.filter(assigned_to=agent, is_sold=False).order_by('created_at'))
        num_current = len(current_tickets)

        if num_current < 15:
            needed = 15 - num_current
            # Use a transaction to avoid race conditions.
            with transaction.atomic():
                new_tickets = list(
                    Ticket.objects.select_for_update(skip_locked=True)
                    .filter(assigned_to__isnull=True, is_sold=False)
                    .order_by('created_at')[:needed]
                )
                for ticket in new_tickets:
                    ticket.assigned_to = agent
                    ticket.save()
            assigned = current_tickets + new_tickets
        else:
            assigned = current_tickets[:15]

        # Return the list of assigned ticket IDs.
        return Response({'assigned_tickets': [ticket.id for ticket in assigned]}, status=status.HTTP_200_OK)

# Agent endpoint for selling a ticket
class AgentSellTicketView(APIView):
    """
    POST: Marks a ticket as sold if it is assigned to the requesting agent.
          Returns 403 Forbidden if the ticket is not assigned to the agent.
    """
    def post(self, request, ticket_id, *args, **kwargs):
        agent = request.user
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # If the ticket exists but is not assigned to the agent, return 403.
        if ticket.assigned_to != agent:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        # If the ticket is already sold, you might want to handle that as well.
        if ticket.is_sold:
            return Response({'detail': 'Ticket already sold.'}, status=status.HTTP_400_BAD_REQUEST)
        
        ticket.is_sold = True
        ticket.save()
        return Response({'id': ticket.id, 'is_sold': ticket.is_sold}, status=status.HTTP_200_OK)
