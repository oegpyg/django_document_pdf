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

## Installing

Create **_fonts_** and **_images_** folder inside the MEDIA path.

Make sure to include `MEDIA_URL` and `MEDIA_ROOT` settings in your project's `settings.py` file:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## Usage

Create a DocumentSpecs, fields, labels, rects, images

- Fields: will take the values of the fields of an instance of a model.
- Labels: to define static texts.
- Rects: to create lines, rectangles with borders and/or fills
- Images: to add images or logos, you can also specify definitions such as transparency for watermarks.

### Fields from model instance

With django_document_pdf you can access not only the fields of the record but also the fields through the relationship by the foreign key.

#### Example:
```
class Supplier(models.Model):
    Code = models.CharField(max_length=20)
    Name = models.CharField(max_length=100)

class PurchaseInvoice(models.Model):
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    Total = models.FloatField()
    ...
```
In your Document Spec Fields definition to get a record fields your need to define like this:
```
Field = Total
```
To get a fields with de foreign key relation of the record:
```
Field = Supplier.Name
```




