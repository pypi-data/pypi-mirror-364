"""Unit tests for nautobot_dns_models."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from nautobot.apps.testing import APIViewTestCases
from nautobot.extras.models.statuses import Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix
from rest_framework import status

from nautobot_dns_models import models
from nautobot_dns_models.models import (
    AAAARecordModel,
    ARecordModel,
    CNAMERecordModel,
    DNSZoneModel,
    MXRecordModel,
    NSRecordModel,
    PTRRecordModel,
    SRVRecordModel,
    TXTRecordModel,
)

User = get_user_model()


class DNSZoneModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot DnsZoneModel API."""

    model = models.DNSZoneModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "filename",
        "soa_mname",
        "soa_rname",
    ]

    @classmethod
    def setUpTestData(cls):
        DNSZoneModel.objects.create(
            name="test.com", filename="test.com.zone", soa_mname="ns1.test.com", soa_rname="admin@test.com"
        )
        DNSZoneModel.objects.create(
            name="test.org", filename="test.org.zone", soa_mname="ns1.test.org", soa_rname="admin@test.org"
        )
        DNSZoneModel.objects.create(
            name="test.net", filename="test.net.zone", soa_mname="ns1.test.net", soa_rname="admin@test.net"
        )

        cls.create_data = [
            {
                "name": "example.com",
                "filename": "example.com.zone",
                "soa_mname": "ns1.example.com",
                "soa_rname": "admin@example.com",
                "soa_refresh": 3600,
                "soa_retry": 600,
            },
            {
                "name": "example.org",
                "filename": "example.org.zone",
                "soa_mname": "ns1.example.org",
                "soa_rname": "admin@example.org",
            },
            {
                "name": "example.net",
                "filename": "example.net.zone",
                "soa_mname": "ns1.example.net",
                "soa_rname": "admin@example.net",
            },
        ]

    # def setUp(self):
    #     """Create a superuser and token for API calls."""
    #     self.user = User.objects.create(username="testuser", is_superuser=True)
    #     self.token = Token.objects.create(user=self.user)
    #     self.client = APIClient()
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    # def test_placeholder(self):
    #     """Verify that devices can be listed."""
    #     url = reverse("dcim-api:device-list")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["count"], 0)


class NSRecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot NSRecordModel API."""

    model = models.NSRecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "server",
    ]

    @classmethod
    def setUpTestData(cls):
        dns_zone = DNSZoneModel.objects.create(
            name="example.com", filename="example.com.zone", soa_mname="ns1.example.com", soa_rname="admin@example.com"
        )

        NSRecordModel.objects.create(name="ns1", server="ns1.example.com.", zone=dns_zone)
        NSRecordModel.objects.create(name="ns2", server="ns2.example.com.", zone=dns_zone)
        NSRecordModel.objects.create(name="ns3", server="ns3.example.com.", zone=dns_zone)

        cls.create_data = [
            {
                "name": "ns4",
                "server": "ns4.example.com.",
                "zone": dns_zone.id,
            },
            {
                "name": "ns5",
                "server": "ns5.example.com.",
                "zone": dns_zone.id,
            },
            {
                "name": "ns6",
                "server": "ns6.example.com.",
                "zone": dns_zone.id,
            },
        ]


class ARecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot ARecordModel API."""

    model = models.ARecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "address",
    ]

    @classmethod
    def setUpTestData(cls):
        dns_zone = DNSZoneModel.objects.create(
            name="example.com", filename="example.com.zone", soa_mname="ns1.example.com", soa_rname="admin@example.com"
        )

        namespace = Namespace.objects.get(name="Global")
        active_status = Status.objects.get(name="Active")
        Prefix.objects.create(prefix="10.0.0.0/24", namespace=namespace, type="Pool", status=active_status)
        ip_addresses = (
            IPAddress.objects.create(address="10.0.0.1/32", namespace=namespace, status=active_status),
            IPAddress.objects.create(address="10.0.0.2/32", namespace=namespace, status=active_status),
        )

        # IPv6 Test Data
        cls.ipv6_zone = DNSZoneModel.objects.create(name="example_ipv6.com")
        Prefix.objects.create(prefix="2001:db8::/64", namespace=namespace, type="Pool", status=active_status)
        cls.invalid_ipv6 = IPAddress.objects.create(
            address="2001:db8::1/128", namespace=namespace, status=active_status
        )

        ARecordModel.objects.create(name="example.com", address=ip_addresses[0], zone=dns_zone)
        ARecordModel.objects.create(name="www.example.com", address=ip_addresses[0], zone=dns_zone)
        ARecordModel.objects.create(name="site.example.com", address=ip_addresses[0], zone=dns_zone)

        cls.create_data = [
            {
                "name": "example.com",
                "address": ip_addresses[1].id,
                "zone": dns_zone.id,
            },
            {
                "name": "www.example.com",
                "address": ip_addresses[1].id,
                "zone": dns_zone.id,
            },
            {
                "name": "site.example.com",
                "address": ip_addresses[1].id,
                "zone": dns_zone.id,
            },
        ]

    def test_create_arecord_with_invalid_ipv6_fails(self):
        """Attempt to create an ARecordModel using an IPv6 address should fail."""
        self.add_permissions("nautobot_dns_models.add_arecordmodel")

        url = reverse("plugins-api:nautobot_dns_models-api:arecordmodel-list")
        data = {
            "name": "invalid.example.com",
            "address": str(self.invalid_ipv6.id),
            "zone": str(self.ipv6_zone.id),
            "ttl": 3600,
        }

        response = self.client.post(url, data=data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)


class AAAARecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot AAAARecordModel API."""

    model = models.AAAARecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "address",
    ]

    @classmethod
    def setUpTestData(cls):
        dns_zone = DNSZoneModel.objects.create(
            name="example.com", filename="example.com.zone", soa_mname="ns1.example.com", soa_rname="admin@example.com"
        )

        active_status = Status.objects.get(name="Active")
        namespace = Namespace.objects.get(name="Global")
        Prefix.objects.create(prefix="2001:db8:abcd:12::/64", namespace=namespace, type="Pool", status=active_status)
        ip_addresses = (
            IPAddress.objects.create(address="2001:db8:abcd:12::1/128", namespace=namespace, status=active_status),
            IPAddress.objects.create(address="2001:db8:abcd:12::2/128", namespace=namespace, status=active_status),
        )

        # IPv4 Test Data
        cls.zone = DNSZoneModel.objects.create(name="example_ipv4.com")
        Prefix.objects.create(prefix="10.0.0.0/24", namespace=namespace, type="Pool", status=active_status)
        cls.invalid_ipv4 = IPAddress.objects.create(address="10.0.0.1/32", namespace=namespace, status=active_status)

        AAAARecordModel.objects.create(name="example.com", address=ip_addresses[0], zone=dns_zone)
        AAAARecordModel.objects.create(name="www.example.com", address=ip_addresses[0], zone=dns_zone)
        AAAARecordModel.objects.create(name="site.example.com", address=ip_addresses[0], zone=dns_zone)

        cls.create_data = [
            {
                "name": "example.com",
                "address": ip_addresses[1].id,
                "zone": dns_zone.id,
            },
            {
                "name": "www.example.com",
                "address": ip_addresses[1].id,
                "zone": dns_zone.id,
            },
            {
                "name": "site.example.com",
                "address": ip_addresses[1].id,
                "zone": dns_zone.id,
            },
        ]

    def test_create_aaaarecord_with_invalid_ipv4_fails(self):
        """Attempt to create an AAAARecordModel using an IPv4 address should fail."""
        self.add_permissions("nautobot_dns_models.add_aaaarecordmodel")

        url = reverse("plugins-api:nautobot_dns_models-api:aaaarecordmodel-list")
        data = {
            "name": "invalid.example.com",
            "address": str(self.invalid_ipv4.id),
            "zone": str(self.zone.id),
            "ttl": 3600,
        }

        response = self.client.post(url, data=data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)


class CNAMERecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot CNAMERecordModel API."""

    model = models.CNAMERecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "alias",
    ]

    @classmethod
    def setUpTestData(cls):
        dns_zone = DNSZoneModel.objects.create(
            name="example.com", filename="example.com.zone", soa_mname="ns1.example.com", soa_rname="admin@example.com"
        )

        CNAMERecordModel.objects.create(name="www", alias="www.example.com", zone=dns_zone)
        CNAMERecordModel.objects.create(name="site", alias="site.example.com", zone=dns_zone)
        CNAMERecordModel.objects.create(name="blog", alias="blog.example.com", zone=dns_zone)

        cls.create_data = [
            {
                "name": "test01",
                "alias": "test01.example.com",
                "zone": dns_zone.id,
            },
            {
                "name": "test02",
                "alias": "test02.example.com",
                "zone": dns_zone.id,
            },
            {
                "name": "test03",
                "alias": "test03.example.com",
                "zone": dns_zone.id,
            },
        ]


class MXRecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot MXRecordModel API."""

    model = models.MXRecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "mail_server",
    ]

    @classmethod
    def setUpTestData(cls):
        dns_zone = DNSZoneModel.objects.create(
            name="example.com", filename="example.com.zone", soa_mname="ns1.example.com", soa_rname="admin@example.com"
        )

        MXRecordModel.objects.create(name="mail", mail_server="mail.example.com", zone=dns_zone)
        MXRecordModel.objects.create(name="mail2", mail_server="mail2.example.com", zone=dns_zone)
        MXRecordModel.objects.create(name="mail3", mail_server="mail3.example.com", zone=dns_zone)

        cls.create_data = [
            {
                "name": "mail4",
                "mail_server": "mail4.example.com",
                "zone": dns_zone.id,
            },
            {
                "name": "mail5",
                "mail_server": "mail5.example.com",
                "zone": dns_zone.id,
            },
            {
                "name": "mail6",
                "mail_server": "mail6.example.com",
                "zone": dns_zone.id,
            },
        ]


class TXTRecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot TXTRecordModel API."""

    model = models.TXTRecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "text",
    ]

    @classmethod
    def setUpTestData(cls):
        dns_zone = DNSZoneModel.objects.create(
            name="example.com", filename="example.com.zone", soa_mname="ns1.example.com", soa_rname="admin@example.com"
        )

        TXTRecordModel.objects.create(name="txt", text="spf-record-01", zone=dns_zone)
        TXTRecordModel.objects.create(name="txt2", text="spf-record-02", zone=dns_zone)
        TXTRecordModel.objects.create(name="txt3", text="spf-record-03", zone=dns_zone)

        cls.create_data = [
            {
                "name": "txt4",
                "text": "spf-record-04",
                "zone": dns_zone.id,
            },
            {
                "name": "txt5",
                "text": "spf-record-05",
                "zone": dns_zone.id,
            },
            {
                "name": "txt6",
                "text": "spf-record-06",
                "zone": dns_zone.id,
            },
        ]


class PTRRecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot PTRRecordModel API."""

    model = models.PTRRecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "ptrdname",
    ]

    @classmethod
    def setUpTestData(cls):
        dns_zone = DNSZoneModel.objects.create(
            name="example.com", filename="example.com.zone", soa_mname="ns1.example.com", soa_rname="admin@example.com"
        )

        PTRRecordModel.objects.create(name="ptr-record-01", ptrdname="ptr-01", zone=dns_zone)
        PTRRecordModel.objects.create(name="ptr-record-02", ptrdname="ptr-02", zone=dns_zone)
        PTRRecordModel.objects.create(name="ptr-record-03", ptrdname="ptr-03", zone=dns_zone)

        cls.create_data = [
            {
                "name": "ptr-record-04",
                "ptrdname": "ptr-04",
                "zone": dns_zone.id,
            },
            {
                "name": "ptr-record-05",
                "ptrdname": "ptr-05",
                "zone": dns_zone.id,
            },
            {
                "name": "ptr-record-06",
                "ptrdname": "ptr-06",
                "zone": dns_zone.id,
            },
        ]


class SRVRecordModelAPITestCase(APIViewTestCases.APIViewTestCase):
    """Test the Nautobot SRVRecordModel API."""

    model = models.SRVRecordModel
    view_namespace = "plugins-api:nautobot_dns_models"
    bulk_update_data = {
        "description": "Example bulk description",
    }
    brief_fields = [
        "name",
        "target",
    ]

    @classmethod
    def setUpTestData(cls):
        zone = DNSZoneModel.objects.create(name="example.com")
        SRVRecordModel.objects.create(
            name="_sip._tcp.example.com", priority=10, weight=5, port=5060, target="sip.example.com", zone=zone
        )
        SRVRecordModel.objects.create(
            name="_ldap._tcp.example.com", priority=20, weight=10, port=389, target="ldap.example.com", zone=zone
        )
        SRVRecordModel.objects.create(
            name="_xmpp._tcp.example.com", priority=30, weight=15, port=5222, target="xmpp.example.com", zone=zone
        )

        cls.create_data = [
            {
                "name": "_smtp._tcp.example.com",
                "priority": 40,
                "weight": 20,
                "port": 25,
                "target": "smtp.example.com",
                "zone": zone.id,
            },
            {
                "name": "_imap._tcp.example.com",
                "priority": 50,
                "weight": 25,
                "port": 143,
                "target": "imap.example.com",
                "zone": zone.id,
            },
            {
                "name": "_pop3._tcp.example.com",
                "priority": 60,
                "weight": 30,
                "port": 110,
                "target": "pop3.example.com",
                "zone": zone.id,
            },
        ]
