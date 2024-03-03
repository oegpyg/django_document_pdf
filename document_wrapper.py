# from reportlab.lib.colors import *
from typing import Union
from reportlab.lib import pagesizes
from reportlab.lib.colors import HexColor, getAllNamedColors, lightgrey, black, PCMYKColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab import lib
from django_document_pdf.text_utils import latin1_to_ascii, wrapText
from .models import DocumentSpec, PDFFont, FontStyle


class DocumentPDF:

    LEFT = 0
    CENTER = 1
    RIGHT = 2

    _title = ""
    _lastPage = False
    _Fields = {}
    _record = None
    __cached__ = {}

    a4_w, a4_h = pagesizes.A4
    legal_w, legal_h = pagesizes.LEGAL
    ledger_w, ledger_h = pagesizes.LEDGER

    def __init__(self, document_spec_code, filename, record) -> None:
        document_spec = DocumentSpec.objects.get(
            Code=document_spec_code)
        if not document_spec:
            raise ValueError("Document Spec doesnt exists")
        active_fonts = document_spec.documentspecfonts_set.all()
        if not active_fonts:
            raise AttributeError("Needs active fonts for current document")
        self.registerFonts(active_fonts)
        required_keys = ['Width', 'Height']

        if all(getattr(document_spec, key) for key in required_keys):
            self._Width = document_spec.Width
            self._Height = document_spec.Height
            self._RowsPerPage = document_spec.RowsPerPage
            self._ShowPlaceHolder = document_spec.ShowPlaceHolder

            self._Fields = document_spec.documentspecfields_set.all()
            self._Rects = document_spec.documentspecrects_set.all()
            self._Images = document_spec.documentspecimages_set.all()
            self._Labels = document_spec.documentspeclabels_set.all()
            self._filename = f"{filename}"

            self._record = record
        else:
            missing_keys = [
                key for key in required_keys if key not in getattr(document_spec, key)]
            raise ValueError(
                f"The document spec have missing conf: {missing_keys}")

    def createCanvas(self, filename, pagesize=pagesizes.A4):
        # To properly configure documents to genPDF set the PDF FontStyle
        curCanvas = canvas.Canvas(filename, pagesize)
        return curCanvas

    def lastPageNr(self):
        # returns 0 if the record has no details.
        # Otherwise returns the number of rows of the detail wich has the biggest number of rows
        res = 1
        self._lastPage = res
        return res

    def generatePDF(self, curCanvas=None, documentspec=None, pagesize=pagesizes.A4):

        saveCanvas = False
        if not curCanvas:
            saveCanvas = True
            curCanvas = self.createCanvas(self._filename, pagesize)

        curCanvas.getAvailableFonts()
        availableColors = getAllNamedColors()
        curCanvas.setAuthor("Django_document_pdf Generator")
        curCanvas.setTitle(self._title)

        resizeFieldFactor = 1
        curCanvas.setPageSize((self._Width, self._Height))
        page_width = curCanvas._pagesize[0]
        page_height = curCanvas._pagesize[1]
        wrate = page_width / self._Width
        hrate = page_height / self._Height

        def translateCoords(x, y, invert_Y=True):
            x = int(x * wrate)
            if invert_Y:
                y = int(page_height - (y * hrate))
            else:
                y = int(y * hrate)
            return x, y
        rows_per_page = self._RowsPerPage
        if not rows_per_page:
            rows_per_page = 999999999
        cur_page = 1
        max_rows = 1
        while cur_page <= self.lastPageNr():
            if cur_page == self.lastPageNr():
                # If this method exists call it to set the values for the fields in the lastPage
                lastPageMethod = "onLastPage"
                runLast = None
                if hasattr(self, lastPageMethod):
                    runLast = getattr(self, lastPageMethod)
                if runLast:
                    runLast()
            for dsimage in self._Images:
                x = dsimage.X
                y = dsimage.Y
                xx, yy = translateCoords(x, y)
                w, dummy = translateCoords(dsimage.Width, 1, False)
                h = int(hrate * float(dsimage.Height))
                yy -= h
                try:
                    if dsimage.Watermark:
                        curCanvas.setFillColor(
                            lightgrey, alpha=float(dsimage.WatermarkOpacity))
                    curCanvas.drawImage(
                        f'media/{dsimage.Filename}', xx, yy, w, h)
                except IOError:
                    pass
            curCanvas.setFillColor(black, alpha=1)
            for dsfield in self._Fields:
                fstyle = FontStyle.objects.get(Code=dsfield.Style.Code)
                if not fstyle:
                    continue
                if dsfield.Type == 0:  # header
                    fvalues = self.getFields(self._record, dsfield.Field, [])
                else:
                    # detail
                    dsfield_clean = dsfield.Field.split(".")
                    check = hasattr(
                        self._record, f'{dsfield_clean[0]}_set'.lower())
                    if check:
                        rows = getattr(
                            self._record, f'{dsfield_clean[0]}_set'.lower())
                        rows = self.cacheGetorCreate(
                            rows, f'{dsfield_clean[0]}_set'.lower())
                    else:
                        rows = []
                    data = []
                    for row in rows:
                        data = self.getFields(
                            row, ".".join(dsfield_clean[1:]), data)
                    fvalues = data
                x = dsfield.X
                y = dsfield.Y
                # show place holder when record wasnt have attr
                if not fvalues and self._ShowPlaceHolder:  # and dsfield.Type == 0:
                    xx, yy = translateCoords(x, y)
                    curCanvas.setFillColor(
                        self.get_color_with_opacity("red", 100))
                    curCanvas.drawString(xx, yy, dsfield.Field)
                    curCanvas.setFillColor(
                        self.get_color_with_opacity("black", 100))

                max_rows = max(max_rows, len(fvalues))
                fromidx = 0
                toidx = 9999999
                if dsfield.Type == 1:  # detail
                    fromidx = (cur_page-1)*rows_per_page
                    toidx = cur_page*rows_per_page
                for fvalue in fvalues[fromidx:toidx]:
                    xx, yy = translateCoords(x, y)
                    if fstyle.Color.startswith("#"):
                        rgb = HexColor(fstyle.Color)
                    elif fstyle.Color in availableColors.keys():
                        rgb = availableColors[fstyle.Color]
                    else:
                        rgb = HexColor("#000000")
                    curCanvas.setFillColorRGB(rgb.red, rgb.green, rgb.blue)
                    curCanvas.setFont(fstyle.PDFFont.Code, int(
                        fstyle.Size*resizeFieldFactor), True)
                    asc, desc = pdfmetrics.getAscentDescent(
                        fstyle.PDFFont.Code, int(fstyle.Size*resizeFieldFactor))
                    yy -= +asc-desc
                    tlimit, width = (dsfield.TextLimit, dsfield.Width)
                    if (tlimit):
                        # tx.textLines
                        # c.drawText(tx)
                        lines = self.wrapText(fvalue, tlimit)
                        fvalue = "\n".join(lines)
                    elif (width):
                        print("No implemented yet")
                    fvalue = "%s" % fvalue  # temp
                    jumps = len(fvalue.split("\n"))
                    for value in fvalue.split("\n"):
                        try:
                            if dsfield.Alignment and dsfield.Width:
                                if dsfield.Alignment == self.CENTER:
                                    xx += int((dsfield.Width)/2)
                                    curCanvas.drawCentredString(xx, yy, value)
                                elif dsfield.Alignment == self.RIGHT:
                                    xx += int(dsfield.Width)
                                    curCanvas.drawRightString(xx, yy, value)
                            else:
                                curCanvas.drawString(xx, yy, value)
                        except UnicodeDecodeError:
                            if fvalue is not None:
                                fvalue = latin1_to_ascii(value)
                            try:
                                if dsfield.Alignment and dsfield.Width:
                                    if dsfield.Alignment == self.CENTER:
                                        xx += int((dsfield.Width)/2)
                                        curCanvas.drawCentredString(
                                            xx, yy, value)
                                    elif dsfield.Alignment == self.RIGHT:
                                        xx += int(dsfield.Width)
                                        curCanvas.drawRightString(
                                            xx, yy, value)
                                else:
                                    curCanvas.drawString(xx, yy, value)
                            except UnicodeDecodeError:
                                if dsfield.Alignment and dsfield.Width:
                                    if dsfield.Alignment == self.CENTER:
                                        xx += int((dsfield.Width)/2)
                                        curCanvas.drawCentredString(
                                            xx, yy, repr(value))
                                    elif dsfield.Alignment == self.RIGHT:
                                        xx += int(dsfield.Width)
                                        curCanvas.drawRightString(
                                            xx, yy, repr(value))
                                else:
                                    curCanvas.drawString(xx, yy, repr(value))
                        yy -= 12
                    y += 15 * jumps

            for dslabel in self._Labels:
                fstyle = FontStyle.objects.get(Code=dslabel.Style.Code)
                if not fstyle:
                    continue
                x = dslabel.X
                y = dslabel.Y
                xx, yy = translateCoords(x, y)
                if fstyle.Color.startswith("#"):
                    rgb = HexColor(fstyle.Color)
                # elif fstyle.Color in availableColors.keys():
                #    rgb = availableColors[fstyle.Color]
                else:
                    rgb = HexColor("#000000")
                curCanvas.setFillColorRGB(rgb.red, rgb.green, rgb.blue)
                curCanvas.setFont(fstyle.PDFFont.Code, int(
                    fstyle.Size*resizeFieldFactor), True)
                asc, desc = pdfmetrics.getAscentDescent(
                    fstyle.PDFFont.Code, int(fstyle.Size*resizeFieldFactor))
                yy -= +asc-desc
                try:
                    curCanvas.drawString(xx, yy, dslabel.Text)
                except UnicodeDecodeError:
                    if dslabel['Text'] is not None:
                        fvalue = latin1_to_ascii(dslabel.Text)
                    try:
                        curCanvas.drawString(xx, yy, fvalue)
                    except UnicodeDecodeError:
                        curCanvas.drawString(xx, yy, repr(fvalue))

            for dsrect in self._Rects:
                if not dsrect.Show:
                    continue
                x = dsrect.X
                y = dsrect.Y
                w = dsrect.Width
                h = dsrect.Height

                bx, by = translateCoords(x, y)
                ex, ey = translateCoords(x+w, y+h)
                if not dsrect.Rounded:
                    curCanvas.rect(bx, by, ex-bx, ey-by)
                else:
                    if dsrect.Radius:
                        if dsrect.Fill:
                            curCanvas.setFillColor(
                                self.get_color_with_opacity(dsrect.FillColor, dsrect.FillColorAlpha))
                        if dsrect.Stroke:
                            curCanvas.setStrokeColor(
                                self.get_color_with_opacity(dsrect.StrokeColor, dsrect.StrokeColorAlpha))
                        curCanvas.roundRect(
                            bx, by, ex-bx, ey-by, 10, fill=dsrect.Fill, stroke=dsrect.Stroke)
                        curCanvas.setFillColor(black, alpha=1)
                    else:
                        raise AttributeError(
                            "Needs define radius for rounded rects")

            curCanvas.showPage()
            cur_page += 1

        if saveCanvas:
            curCanvas.save()
        return curCanvas

    def get_color_with_opacity(self, color: str, opacity: float) -> Union[PCMYKColor, None]:
        COLOR_MAP = {
            "red": PCMYKColor(0, 100, 100, 0),
            "orange": PCMYKColor(0, 50, 100, 0),
            "black": PCMYKColor(0, 0, 0, 100),
            "blue": PCMYKColor(100, 50, 0, 0),
            "pink": PCMYKColor(0, 100, 0, 0),
            "purple": PCMYKColor(50, 100, 0, 0),
            "brown": PCMYKColor(30, 60, 90, 40),
            "green": PCMYKColor(100, 0, 100, 0),
            "yellow": PCMYKColor(0, 0, 100, 0),
        }
        color = color.lower()
        matched_color = COLOR_MAP.get(color)

        if matched_color is not None:
            return matched_color.clone(alpha=opacity)
        else:
            print(
                f"(get_color_with_opacity)Color '{color}' not found. Skipped.")
            return None

    @classmethod
    def registerFonts(cls, fonts):
        for font in fonts:
            pdfmetrics.registerFont(
                TTFont(font.PDFFont.Code, f'media/{font.PDFFont.Font}'))

    def getFields(self, record, field, data):
        """Retrieves fields from a nested record structure by fk, handling dotted field paths.

        Args:
            record (any): The record object to extract fields from.
            field (str): The field path, potentially containing dots for nested fields.
            data (list): The list to append the retrieved values to.

        Returns:
            list: The updated list with the retrieved fields.
        """

        try:
            field_parts = field.split(".")
            current_value = record

            for part in field_parts[:-1]:  # Iterate through nested parts
                current_value = getattr(current_value, part)

            # Append final field value
            data.append(getattr(current_value, field_parts[-1]))

        except Exception:
            return []

        return data

    def cacheGetorCreate(self, record, key):
        """prevent incur multiple queries on the same transaction row table """
        if key not in self.__cached__:
            self.__cached__[key] = record.all()
        return self.__cached__[key]
