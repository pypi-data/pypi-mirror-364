"""Tables for nautobot_dns_models."""

import django_tables2 as tables
from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn

from nautobot_dns_models import models


class DNSRecordsTable(BaseTable):  # pylint: disable=nb-no-model-found
    """Base table for DNS records list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    zone = tables.LinkColumn()
    ttl = tables.Column(verbose_name="TTL")


class DNSZoneModelTable(BaseTable):
    """Table for DNS Zone list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(
        models.DNSZoneModel,
        # Option for modifying the default action buttons on each row:
        # buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        # pk_field="pk",
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.DNSZoneModel
        fields = (
            "pk",
            "name",
            "ttl",
            "filename",
            "description",
            "soa_expire",
            "soa_rname",
            "soa_refresh",
            "soa_retry",
            "soa_serial",
            "soa_minimum",
        )

        default_columns = (
            "pk",
            "name",
            "ttl",
            "filename",
            "soa_expire",
            "soa_rname",
        )


class NSRecordModelTable(DNSRecordsTable):
    """Table for list view."""

    actions = ButtonsColumn(
        models.NSRecordModel,
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the default action buttons on each row:
        # buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.NSRecordModel
        fields = (
            "pk",
            "name",
            "server",
            "zone",
            "description",
            "comment",
            "ttl",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "name",
            "server",
            "zone",
            "ttl",
            "actions",
        )


class ARecordModelTable(DNSRecordsTable):
    """Table for list view."""

    address = tables.LinkColumn()
    actions = ButtonsColumn(
        models.ARecordModel,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.ARecordModel
        fields = (
            "pk",
            "name",
            "address",
            "zone",
            "comment",
            "ttl",
            "description",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "address",
            "zone",
            "comment",
            "ttl",
            "actions",
        )


class AAAARecordModelTable(DNSRecordsTable):
    """Table for list view."""

    address = tables.LinkColumn()
    actions = ButtonsColumn(
        models.AAAARecordModel,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.AAAARecordModel
        fields = (
            "pk",
            "name",
            "address",
            "zone",
            "comment",
            "ttl",
            "description",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "address",
            "zone",
            "comment",
            "ttl",
            "actions",
        )


class CNAMERecordModelTable(DNSRecordsTable):
    """Table for list view."""

    actions = ButtonsColumn(
        models.CNAMERecordModel,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.CNAMERecordModel
        fields = (
            "pk",
            "name",
            "alias",
            "zone",
            "comment",
            "ttl",
            "description",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "alias",
            "zone",
            "comment",
            "ttl",
            "actions",
        )


class MXRecordModelTable(DNSRecordsTable):
    """Table for list view."""

    actions = ButtonsColumn(
        models.MXRecordModel,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.MXRecordModel
        fields = (
            "pk",
            "name",
            "mail_server",
            "zone",
            "comment",
            "ttl",
            "description",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "mail_server",
            "zone",
            "comment",
            "ttl",
            "actions",
        )


class TXTRecordModelTable(DNSRecordsTable):
    """Table for list view."""

    actions = ButtonsColumn(
        models.TXTRecordModel,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.TXTRecordModel
        fields = (
            "pk",
            "name",
            "text",
            "zone",
            "comment",
            "ttl",
            "description",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "text",
            "zone",
            "comment",
            "ttl",
            "actions",
        )


class PTRRecordModelTable(DNSRecordsTable):
    """Table for list view."""

    actions = ButtonsColumn(
        models.PTRRecordModel,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.PTRRecordModel
        fields = (
            "pk",
            "name",
            "ptrdname",
            "zone",
            "comment",
            "ttl",
            "description",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "ptrdname",
            "zone",
            "comment",
            "ttl",
            "actions",
        )


class SRVRecordModelTable(DNSRecordsTable):
    """Table for list view."""

    actions = ButtonsColumn(
        models.SRVRecordModel,
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.SRVRecordModel
        fields = (
            "pk",
            "name",
            "priority",
            "weight",
            "port",
            "target",
            "zone",
            "comment",
            "ttl",
            "description",
            "actions",
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "priority",
            "weight",
            "port",
            "target",
            "zone",
            "actions",
        )
