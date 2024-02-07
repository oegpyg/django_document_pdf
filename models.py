from django.db import models
from django.core.exceptions import ValidationError


class PDFFont(models.Model):
    Code = models.CharField(max_length=15, unique=True)
    Font = models.FileField(upload_to='fonts/')

    def __str__(self):
        return self.Code


class FontStyle(models.Model):
    Code = models.CharField(max_length=15, unique=True)
    PDFFont = models.ForeignKey(PDFFont, on_delete=models.PROTECT)
    Color = models.CharField(
        max_length=15, default="black", null=False, blank=False)
    Size = models.SmallIntegerField(default=12, null=False, blank=False)
    Bold = models.BooleanField(default=False)

    def clean(self):
        if self.Code:
            existing = FontStyle.objects.filter(
                Code=self.Code).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("The FontStyle already exists.")
        super(FontStyle, self).clean()

    def __str__(self):
        return self.Code


class DocumentSpec(models.Model):
    Code = models.CharField(max_length=30, unique=True)
    Height = models.BigIntegerField(null=True)
    Width = models.BigIntegerField(null=True)
    ScreenDpi = models.BigIntegerField(null=True)
    RowsPerPage = models.BigIntegerField(null=True)

    no_admin = True

    def clean(self):
        if self.Code:
            existing = DocumentSpec.objects.filter(
                Code=self.Code).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    "The Document Specification already exists.")
        super(DocumentSpec, self).clean()

    def __str__(self):
        return self.Code


class DocumentSpecFields(models.Model):
    DocumentSpec = models.ForeignKey(DocumentSpec, on_delete=models.PROTECT)
    Field = models.CharField(max_length=50)
    Style = models.ForeignKey(FontStyle, on_delete=models.PROTECT)
    types = ((0, 'Header'), (1, 'Detail'))
    Type = models.SmallIntegerField(choices=types)
    Width = models.IntegerField(null=True)
    Y = models.IntegerField(null=False, blank=False)
    X = models.IntegerField(null=False, blank=False)
    Decimals = models.IntegerField(default=0)
    _align = ((0, 'Left'), (1, 'Centered'), (2, 'Right'))
    Alignment = models.SmallIntegerField(choices=_align)
    TextLimit = models.IntegerField(null=True)

    no_admin = True


class DocumentSpecLabels(models.Model):
    DocumentSpec = models.ForeignKey(DocumentSpec, on_delete=models.PROTECT)
    Text = models.CharField(max_length=255, blank=True)
    Style = models.ForeignKey(FontStyle, on_delete=models.PROTECT)
    Y = models.IntegerField(null=False, blank=False)
    X = models.IntegerField(null=False, blank=False)
    _align = ((0, 'Left'), (1, 'Centered'), (2, 'Right'))
    Alignment = models.SmallIntegerField(choices=_align)

    no_admin = True


class DocumentSpecRects(models.Model):
    DocumentSpec = models.ForeignKey(DocumentSpec, on_delete=models.PROTECT)
    Height = models.IntegerField(null=False, blank=False)
    Width = models.IntegerField(null=False, blank=False)
    Y = models.IntegerField(null=False, blank=False)
    X = models.IntegerField(null=False, blank=False)

    no_admin = True


class DocumentSpecImages(models.Model):
    DocumentSpec = models.ForeignKey(DocumentSpec, on_delete=models.PROTECT)
    Height = models.IntegerField(null=False, blank=False)
    Width = models.IntegerField(null=False, blank=False)
    Y = models.IntegerField(null=False, blank=False)
    X = models.IntegerField(null=False, blank=False)
    Filename = models.FileField(upload_to='images/')

    no_admin = True


class DocumentSpecFonts(models.Model):
    DocumentSpec = models.ForeignKey(DocumentSpec, on_delete=models.PROTECT)
    PDFFont = models.ForeignKey(PDFFont, on_delete=models.PROTECT)

    no_admin = True
