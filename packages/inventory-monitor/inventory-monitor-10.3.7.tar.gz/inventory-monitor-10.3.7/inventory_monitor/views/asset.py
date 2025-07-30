from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.forms.asset import AssetABRAAssignmentForm
from inventory_monitor.models import Asset


class AssetView(generic.ObjectView):
    queryset = models.Asset.objects.all()


class AssetListView(generic.ObjectListView):
    queryset = (
        models.Asset.objects.all()
        .prefetch_related("services")
        .prefetch_related("tags")
        .prefetch_related("abra_assets")
        .prefetch_related("rmas")  # Prefetch RMAs to avoid N+1 queries in get_related_probes
        .prefetch_related("type")  # Prefetch asset types for table display
        .select_related("assigned_object_type")  # Optimize generic foreign key queries
        .annotate(services_count=Count("services"))
        .annotate(services_to=ArrayAgg("services__service_end"))
        .annotate(services_contracts=ArrayAgg("services__contract__name"))
    )
    filterset = filtersets.AssetFilterSet
    filterset_form = forms.AssetFilterForm
    table = tables.EnhancedAssetTable  # Changed to show probe status with green rows
    template_name = "inventory_monitor/asset_list.html"  # Custom template with CSS
    actions = {
        "add": {},
        "import": {},
        "export": {},
        "bulk_edit": {},
        "bulk_delete": {},
    }


class AssetEditView(generic.ObjectEditView):
    queryset = models.Asset.objects.all()
    form = forms.AssetForm

    def alter_object(self, instance, request, url_args, url_kwargs):
        if not instance.pk:
            assigned_object_type = request.GET.get("assigned_object_type")
            assigned_object_id = request.GET.get("assigned_object_id")

            if assigned_object_type and assigned_object_id:
                instance.assigned_object_type = ContentType.objects.get(pk=assigned_object_type)
                instance.assigned_object_id = assigned_object_id

        return instance


class AssetDeleteView(generic.ObjectDeleteView):
    queryset = models.Asset.objects.all()


class AssetBulkEditView(generic.BulkEditView):
    queryset = models.Asset.objects.all()
    filterset = filtersets.AssetFilterSet
    table = tables.AssetTable
    form = forms.AssetBulkEditForm


class AssetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Asset.objects.all()
    filterset = filtersets.AssetFilterSet
    table = tables.AssetTable


class AssetBulkImportView(generic.BulkImportView):
    queryset = models.Asset.objects.all()
    model_form = forms.AssetBulkImportForm


class AssetABRAAssignmentView(generic.ObjectEditView):
    """
    View for assigning ABRA objects to an Asset
    """

    queryset = Asset.objects.all()
    form = AssetABRAAssignmentForm
    template_name = "inventory_monitor/asset_abra_assignment.html"

    def get_object(self, **kwargs):
        """Get the Asset object to assign ABRA objects to"""
        if not kwargs:
            return self.queryset.model()

        if "pk" not in kwargs:
            return super().get_object(**kwargs)

        return get_object_or_404(Asset, pk=self.kwargs["pk"])

    def get_return_url(self, request, instance=None):
        """Return to the asset detail page after successful assignment"""
        return reverse("plugins:inventory_monitor:asset", args=[self.kwargs["pk"]])

    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)

        # Add success message
        abra_count = form.cleaned_data["abra_assets"].count()
        messages.success(
            self.request, _("Successfully assigned {} ABRA object(s) to asset {}").format(abra_count, form.instance)
        )

        return response

    def get_extra_context(self, request, instance):
        """Add extra context for the template"""
        device_asset_tag = (
            instance.assigned_object.asset_tag
            if (
                instance.assigned_object_type.model == "device"
                and getattr(instance.assigned_object, "asset_tag", None)
                and getattr(instance.assigned_object, "serial", None) == instance.serial
            )
            else None
        )
        return {
            "asset": instance,
            "title": f"Assign ABRA Objects to {instance}",
            "device_asset_tags": device_asset_tag,
        }
