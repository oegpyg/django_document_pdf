from django.core.cache import cache
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class PDFFont(models.Model):
    Code = models.CharField(max_length=15, unique=True)
    Font = models.FileField(upload_to='fonts/')

    def __str__(self):
        return self.Code


class FontStyleManager(models.Manager):
    def get(self, *args, **kwargs):
        cache_key = f"fontstyle_{kwargs.get('Code')}"
        cached_object = cache.get(cache_key)
        if cached_object:
            return cached_object
        # If the object is not in the cache, retrieve it from the database
        obj = super().get(*args, **kwargs)
        # Add the retrieved object to the cache with 5 mins duraction
        cache.set(cache_key, obj, timeout=300)
        return obj


class FontStyle(models.Model):
    Code = models.CharField(max_length=15, unique=True)
    PDFFont = models.ForeignKey(PDFFont, on_delete=models.PROTECT)
    Color = models.CharField(
        max_length=15, default="black", null=False, blank=False)
    Size = models.SmallIntegerField(default=12, null=False, blank=False)
    Bold = models.BooleanField(default=False)

    objects = FontStyleManager()

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
    ShowPlaceHolder = models.BooleanField(
        default=False, help_text="The expected attribute is displayed in case it is not found.")

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
    Width = models.IntegerField(null=True, blank=True)
    Y = models.IntegerField(null=False, blank=False)
    X = models.IntegerField(null=False, blank=False)
    Decimals = models.IntegerField(default=0)
    _align = ((0, 'Left'), (1, 'Centered'), (2, 'Right'))
    Alignment = models.SmallIntegerField(choices=_align, default=0)
    TextLimit = models.IntegerField(null=True, blank=True)

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
    Rounded = models.BooleanField(default=False)
    Radius = models.IntegerField(null=True, blank=True)
    Stroke = models.BooleanField(default=False)
    StrokeColor = models.CharField(max_length=10, blank=True)
    StrokeColorAlpha = models.IntegerField(default=100, validators=[
        MinValueValidator(0),
        MaxValueValidator(100),
    ])
    Fill = models.BooleanField(default=False)
    FillColor = models.CharField(max_length=10, blank=True)
    FillColorAlpha = models.IntegerField(default=100, validators=[
        MinValueValidator(0),
        MaxValueValidator(100),
    ])
    Show = models.BooleanField(default=True)

    no_admin = True


class DocumentSpecImages(models.Model):
    DocumentSpec = models.ForeignKey(DocumentSpec, on_delete=models.PROTECT)
    Height = models.IntegerField(null=False, blank=False)
    Width = models.IntegerField(null=False, blank=False)
    Y = models.IntegerField(null=False, blank=False)
    X = models.IntegerField(null=False, blank=False)
    Filename = models.FileField(upload_to='images/')
    Watermark = models.BooleanField(default=False)
    WatermarkOpacity = models.DecimalField(
        max_digits=1, decimal_places=1, help_text="Between 0.* to 1", blank=True, null=True)

    no_admin = True


class DocumentSpecFonts(models.Model):
    DocumentSpec = models.ForeignKey(DocumentSpec, on_delete=models.PROTECT)
    PDFFont = models.ForeignKey(PDFFont, on_delete=models.PROTECT)

    no_admin = True
