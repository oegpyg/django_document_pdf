# django_document_pdf

A simple way to create pdf documents.
Use cases:
- Generate pdf reports
- Generate pdf documents from transactions such as invoices or other documents from a transaction.

The final goal is to offer a drag&drop interface to design the document.

This project is still in its early stages of development and all contributors are welcome.

It has only been tested in Django 4.0 and higher. For older versions of Django, use with caution.

If you would like to see something added, please request it! As I said, this is still in an early stage of development and I'm open to all suggestions.

If you find a bug, please report it!

## Installation

You will need to add `django_document_pdf` to your `INSTALLED_APPS` in your `settings.py` file:

```python
INSTALLED_APPS = [
    ...
    'django_document_pdf',
    ...
]
```

You will also need to add the following to your `urls.py` file:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('django_document_pdf/', include('django_document_pdf.urls')),
    ...
]
```

## Usage

Create **_fonts_** and **_images_** folder inside the MEDIA path.

Make sure to include `MEDIA_URL` and `MEDIA_ROOT` settings in your project's `settings.py` file:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```
