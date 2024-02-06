from django.contrib import admin
from django.apps import apps
from .models import DocumentSpec, DocumentSpecFields, DocumentSpecLabels, DocumentSpecRects, DocumentSpecImages


# Gets all the models registered in the specified application
modelos = apps.get_app_config('django_document_pdf').get_models()

# Register all the models in the admin provided they do not have the 'no_admin' attribute.
# If it has the Admin class inside the model, it is considered as the custom model admin.
for modelo in modelos:
    if 'no_admin' not in modelo.__dict__:
        if 'Admin' in modelo.__dict__:
            admin.site.register(modelo, modelo.Admin)
        else:
            admin.site.register(modelo)


class DocumentSpecFieldsAdminTabular(admin.TabularInline):
    model = DocumentSpecFields
    extra = 1


class DocumentSpecLabelsAdminTabular(admin.TabularInline):
    model = DocumentSpecLabels
    extra = 1


class DocumentSpecRectsAdminTabular(admin.TabularInline):
    model = DocumentSpecRects
    extra = 1


class DocumentSpecImagesAdminTabular(admin.TabularInline):
    model = DocumentSpecImages
    extra = 1


class DocumentSpecAdmin(admin.ModelAdmin):
    list_display = ['Code']
    inlines = [DocumentSpecFieldsAdminTabular,
               DocumentSpecLabelsAdminTabular,
               DocumentSpecRectsAdminTabular,
               DocumentSpecImagesAdminTabular]


admin.site.register(DocumentSpec, DocumentSpecAdmin)
