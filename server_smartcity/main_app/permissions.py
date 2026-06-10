from rest_framework import permissions


class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        # Semua user login boleh membaca data
        if request.method in permissions.SAFE_METHODS:
            return True

        # Hanya pemilik laporan DAN status DRAFT
        return (
            obj.reporter == request.user
            and obj.status == 'DRAFT'
        )