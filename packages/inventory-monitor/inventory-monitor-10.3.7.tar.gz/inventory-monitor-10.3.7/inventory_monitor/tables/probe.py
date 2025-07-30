import django_tables2 as tables
from netbox.tables import NetBoxTable

from inventory_monitor.models import Probe


class ProbeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    changes_count = tables.Column(orderable=False)
    discovered_data = tables.JSONColumn()

    class Meta(NetBoxTable.Meta):
        model = Probe
        fields = (
            "pk",
            "id",
            "time",
            "name",
            "device_descriptor",
            "site_descriptor",
            "location_descriptor",
            "description",
            "part",
            "serial",
            "device",
            "site",
            "location",
            "comments",
            "changes_count",
            "actions",
            "category",
            "creation_time",
        )
        default_columns = (
            "id",
            "time",
            "creation_time",
            "name",
            "serial",
            "part",
            "device_descriptor",
            "device",
            "site_descriptor",
            "site",
            "location_descriptor",
            "location",
            "changes_count",
        )

        # Add row attributes for styling based on probe status - using data attributes for CSS targeting
        row_attrs = {
            "data-probe-status": lambda record: ("recent" if record.is_recently_probed() else "stale"),
            "data-serial": lambda record: record.serial,
        }
