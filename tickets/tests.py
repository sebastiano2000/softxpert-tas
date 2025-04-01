import json
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from tickets.models import Ticket

User = get_user_model()

class TicketAPITest(TestCase):
    def setUp(self):
        # Create an admin user (for admin tests)
        self.admin_user = User.objects.create_user(username="admin", password="adminpass", is_admin=True)
        # Create an agent user (for agent tests)
        self.agent_user = User.objects.create_user(username="agent", password="agentpass", is_agent=True)

    def test_admin_create_ticket(self):
        # Log in as admin
        self.client.login(username="admin", password="adminpass")
        url = reverse('admin-tickets-list')
        # For your Ticket model (which has no title/description), sending an empty POST is fine.
        response = self.client.post(url, {})  
        # Expect the created ticket to have an 'id'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
    
    def test_agent_fetch_assign_tickets(self):
        # Log in as agent
        self.client.login(username="agent", password="agentpass")
        # Create 15 unassigned tickets
        for _ in range(15):
            Ticket.objects.create(assigned_to=None, is_sold=False)
        url = reverse('agent-assign-tickets')
        response = self.client.get(url)
        # Expect a 200 OK response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assume the view returns a dict with key 'assigned_tickets' containing a list of ticket IDs
        self.assertIn('assigned_tickets', response.data)
        self.assertEqual(len(response.data['assigned_tickets']), 15)
    
    def test_agent_fetch_when_already_has_15(self):
        # Log in as agent
        self.client.login(username="agent", password="agentpass")
        # Create 15 tickets already assigned to the agent
        for _ in range(15):
            Ticket.objects.create(assigned_to=self.agent_user, is_sold=False)
        url = reverse('agent-assign-tickets')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('assigned_tickets', response.data)
        self.assertEqual(len(response.data['assigned_tickets']), 15)
    
    def test_agent_sell_ticket(self):
        # Log in as agent
        self.client.login(username="agent", password="agentpass")
        # Create a ticket assigned to the agent that is unsold
        ticket = Ticket.objects.create(assigned_to=self.agent_user, is_sold=False)
        url = reverse('agent-sell-ticket', kwargs={'ticket_id': ticket.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that the ticket is now marked as sold
        ticket.refresh_from_db()
        self.assertTrue(ticket.is_sold)
    
    def test_agent_sell_ticket_security(self):
        # Log in as agent
        self.client.login(username="agent", password="agentpass")
        # Create a ticket assigned to the admin user
        ticket = Ticket.objects.create(assigned_to=self.admin_user, is_sold=False)
        url = reverse('agent-sell-ticket', kwargs={'ticket_id': ticket.id})
        response = self.client.post(url)
        # Expecting a forbidden response because the agent is not allowed to sell a ticket that isn't assigned to them.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_concurrent_ticket_assignment(self):
        # Create two agent users
        agent1 = User.objects.create_user(username="agent1", password="pass1", is_agent=True)
        agent2 = User.objects.create_user(username="agent2", password="pass2", is_agent=True)
        
        # Create 30 unassigned tickets (to allow each agent to get 15)
        for _ in range(30):
            Ticket.objects.create(assigned_to=None, is_sold=False)
        
        # Use two separate client sessions
        from rest_framework.test import APIClient
        client1 = APIClient()
        client2 = APIClient()
        
        client1.login(username="agent1", password="pass1")
        client2.login(username="agent2", password="pass2")
        
        url = reverse('agent-assign-tickets')
        response1 = client1.get(url)
        response2 = client2.get(url)
        
        tickets_agent1 = set(response1.data.get('assigned_tickets', []))
        tickets_agent2 = set(response2.data.get('assigned_tickets', []))
        
        # They should have disjoint sets
        self.assertTrue(tickets_agent1.isdisjoint(tickets_agent2))

