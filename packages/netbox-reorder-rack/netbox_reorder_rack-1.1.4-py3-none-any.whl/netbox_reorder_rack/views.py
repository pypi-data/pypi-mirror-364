from dcim.models import Device
from dcim.models import DeviceType
from dcim.models import Rack
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import View
from netbox.config import get_config
from utilities.views import register_model_view


@register_model_view(
    Rack,
    name="reorder",
    path="reorder",
)
class ReorderView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ["dcim.change_device", "dcim.view_device"]
    template_name = "netbox_reorder_rack/rack.html"

    def get(self, request, pk):
        rack = get_object_or_404(Rack, pk=pk)
        # Get the 'view' query parameter from the URL, default to 'images-and-labels' if not provided
        selected_view = request.GET.get("view", "images-and-labels")

        # Now you can use the `selected_view` variable to handle the specific logic
        if selected_view == "images-and-labels":
            # Logic for handling 'Images and Labels' view
            images = True
            labels = True
        elif selected_view == "images-only":
            # Logic for handling 'Images only' view
            images = True
            labels = False
        elif selected_view == "labels-only":
            # Logic for handling 'Labels only' view
            images = False
            labels = True

        non_racked = Device.objects.filter(
            rack=rack, position__isnull=True, parent_bay__isnull=True
        )

        exclude_list = []
        # fix - exclude all child devices:
        for device in non_racked:
            device_type = DeviceType.objects.get(id=device.device_type.id)
            if device_type.subdevice_role == "child":
                exclude_list.append(device.id)

        non_racked_devices = non_racked.exclude(pk__in=exclude_list)
        config = get_config()

        base_url = f"{request.scheme}://{request.get_host().rstrip('/')}"

        return render(
            request,
            self.template_name,
            {
                "object": rack,
                "images": images,
                "labels": labels,
                "unit_width": config.RACK_ELEVATION_DEFAULT_UNIT_WIDTH,
                "base_url": base_url,
                "front_units": rack.get_rack_units(expand_devices=False, face="front"),
                "rear_units": rack.get_rack_units(expand_devices=False, face="rear"),
                "non_racked": non_racked_devices,
                "basepath": settings.BASE_PATH,
            },
        )
