from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'created_at', 'assigned_to', 'is_sold']
        read_only_fields = ['id', 'created_at']
