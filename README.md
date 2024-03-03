# django_document_pdf

A simple way to generate PDF documents in Django apps.
Use cases:
- [x] Generate pdf reports
- [x] Generate PDF documents from transactions, such as invoices or other documents derived from a transaction.

## Positioning in the Document

**To define the position within the document, it uses X and Y coordinates.**
- Image of X and Y coordinate usage:
![](https://github.com/oegpyg/django_document_pdf/blob/main/pictures/images_xy.png)
- Image of rectangles with X and Y coordinates:
![](https://github.com/oegpyg/django_document_pdf/blob/main/pictures/rects_xy.png)

## Project Status and Contribution

The final goal is to offer a drag-and-drop interface for designing the document, enabling collaborative document creation. This project is still in its early stages of development and welcomes all contributors.

## Compatibility

Currently, it has only been tested with Django 4.0 and higher. For older versions of Django, use with caution.

## Feedback and Bug Reports

We encourage your input!
- If you would like to see a feature added, please request it!
- If you find a bug, please report it!

## Installation

1. Add to `INSTALLED_APPS` in your `settings.py` file:

```python
INSTALLED_APPS = [
    ...
    'django_document_pdf',
    ...
]
```

2. Include URLs in `urls.py` file:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('django_document_pdf/', include('django_document_pdf.urls')),
    ...
]
```

## Setting Up Media Folders

1. Create folders:
Create **_fonts_** and **_images_** folder inside the MEDIA path.

2. Configure settings:
Make sure to include `MEDIA_URL` and `MEDIA_ROOT` settings in your project's `settings.py` file:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## Usage

1. Manage Fonts and Styles

- Create and upload your fonts.
- Create your fonts styles.

2. Define Document Elements

Create a DocumentSpecs, fields, labels, rects, images, fonts

- Fields: Access values from model instances.
- Labels: Define static text elements.
- Rects: Create lines, rectangles with borders and/or fills.
- Images: Add images or logos, including transparency options for watermarks.
- Fonts: Specify fonts to prevent loading unused ones.

3. Accessing Data

With `django_document_pdf`, you can access not only the fields of the record but also related fields through foreign key relationships.

## Example:
```python
class Supplier(models.Model):
    Code = models.CharField(max_length=20)
    Name = models.CharField(max_length=100)

class PurchaseInvoice(models.Model):
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    Total = models.DecimalField(max_digits=10, decimal_places=2)
    ...

class Item(models.Model):
    Code = models.CharField(max_length=20, unique=True)
    Description = models.CharField(max_length=50)
    Price = models.DecimalField(max_digits=10, decimal_places=2)

class PurchaseInvoiceItems(models.Model):
    PurchaseInvoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE)
    Item = models.ForeignKey(Item, on_delete=models.CASCADE)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    ...
```

### Accessing Fields:
- Record Field:
![](https://github.com/oegpyg/django_document_pdf/blob/main/pictures/1_ddp.png)


- Foreign Key Field:
![](https://github.com/oegpyg/django_document_pdf/blob/main/pictures/2_ddp.png)

> Thats like `record.Supplier.Name`


- Detail Record Field:
![](https://github.com/oegpyg/django_document_pdf/blob/main/pictures/3_ddp.png)

> Thats like `record.purchaseinvoiceitems_set.all()[idx].Price`

- Related Detail Record Field:
To get field with the foreing key relation of detail related record:
![](https://github.com/oegpyg/django_document_pdf/blob/main/pictures/4_ddp.png)

> Thats like `record.purchaseinvoiceitems_set.all()[idx].Item.Description`


`Them` to make your document
```python
from django_document_pdf.document_wrapper import DocumentPDF
from .models import PurchaseInvoice

record = PurchaseInvoice.objects.get(pk=1)
doc = DocumentPDF(document_spec_code='Invoice_Test',
                  filename='file.pdf',
                  record=record)

doc.generatePDF()
```


[Demo](https://github.com/oegpyg/django_document_pdf_demo)
### Screen of File generated with demo project
![Screen of File generated with demo project](https://github.com/oegpyg/django_document_pdf_demo/blob/main/file.png)
