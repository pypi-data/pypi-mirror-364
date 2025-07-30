#    Copyright © 2024 Andrei Puchko
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import glob
import re
import json
import html
import subprocess
from io import BytesIO
import os
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from decimal import Decimal
from datetime import datetime
import logging
from .excel_format import format_number

BUILTIN_FORMATS = {
    "0": "General",
    "1": "0",
    "2": "0.00",
    "3": "#,##0",
    "4": "#,##0.00",
    "5": '"$"#,##0_);("$"#,##0)',
    "6": '"$"#,##0_);[Red]("$"#,##0)',
    "7": '"$"#,##0.00_);("$"#,##0.00)',
    "8": '"$"#,##0.00_);[Red]("$"#,##0.00)',
    "9": "0%",
    "10": "0.00%",
    "11": "0.00E+00",
    "12": "# ?/?",
    "13": "# ??/??",
    "14": "mm-dd-yy",
    "15": "d-mmm-yy",
    "16": "d-mmm",
    "17": "mmm-yy",
    "18": "h:mm AM/PM",
    "19": "h:mm:ss AM/PM",
    "20": "h:mm",
    "21": "h:mm:ss",
    "22": "m/d/yy h:mm",
    "37": "#,##0_);(#,##0)",
    "38": "#,##0_);[Red](#,##0)",
    "39": "#,##0.00_);(#,##0.00)",
    "40": "#,##0.00_);[Red](#,##0.00)",
    "41": r'_(* #,##0_);_(* \(#,##0\);_(* "-"_);_(@_)',
    "42": r'_("$"* #,##0_);_("$"* \(#,##0\);_("$"* "-"_);_(@_)',
    "43": r'_(* #,##0.00_);_(* \(#,##0.00\);_(* "-"??_);_(@_)',
    "44": r'_("$"* #,##0.00_)_("$"* \(#,##0.00\)_("$"* "-"??_)_(@_)',
    "45": "mm:ss",
    "46": "[h]:mm:ss",
    "47": "mmss.0",
    "48": "##0.0E+0",
    "49": "@",
}


FIRST_SHEET_CELLS_LIMIT = 500


WHITE_LIST = ["abs", "min", "max", "len", "round"]


NS_SPREADSHEET = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_WORD = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

ET.register_namespace("w", NS_WORD)


def _num(t):
    try:
        return Decimal(f"{t}")
    except Exception:
        return 0


class DefDict(dict):
    def __getitem__(self, key):
        if key not in self:
            return ""
        return super().__getitem__(key)


def my_eval(compiledCode, rawCode, data_dict):
    data_dict["_num"] = _num

    for key in data_dict:
        if key in dir(__builtins__):
            del data_dict[key]

    if [
        x
        for x in compiledCode.co_names
        if x.startswith("__") or (x not in WHITE_LIST and x not in data_dict and x in dir(__builtins__))
    ]:
        logging.warning(f"Whilelist rule broken:'{rawCode}'")
        return False
    try:
        result = eval(compiledCode, data_dict)
        del data_dict["__builtins__"]
        del data_dict["_num"]
        return result
    except Exception as e:
        logging.warning(f"Evaluation error in expression '{rawCode}': {e}")
        return False


def merge(file1, file2, outputFile):
    d2d = q2data2docx()
    for x in [file1, file2]:
        if not d2d.loadFile(x):
            print(f"Input file not found: {x}")
            return False
    if d2d.merge():
        outputFile = d2d.checkOutputFileName(outputFile)
        if d2d.saveFile(outputFile):
            print(f"Processing finished. See result in {outputFile}")
            return True
        else:
            print(f"Can't create output file: {outputFile}")
    else:
        print(f"Processing error: {d2d.error}")
    return False


def get_re_pattern(text):
    return r"#\s*" + text + r"\s*#"


re_search_html_char = re.compile(r"^x[\dABCDEF]+;")
re_sharp = re.compile(r"#(?!(?:(?!&#x).)*;)")
re_get_keys = re.compile(r"#[^#]+#")


def remove_hash_fragments(text):
    result = []
    splited_text = text.split("#")
    cutted = False
    for index, value in enumerate(splited_text):
        if index == 0:
            result.append(value)
        elif cutted and index < len(splited_text) - 1:
            result.append(value)
            if splited_text[index + 1][-1] == "&":
                result.append("#")
        elif value[:2] == "ff" and splited_text[index - 1][-1] == '"':
            result.append("#" + value)
        elif re_search_html_char.search(value) and splited_text[index - 1][-1] == "&":
            result.append("#" + value)
        elif index < len(splited_text) - 1 and re_search_html_char.search(splited_text[index + 1]) and value[-1] == "&":
            result.append(value)
        elif index == len(splited_text) - 1:
            if value == "":
                result.append("#")
            else:
                result.append(value)
        else:
            cutted = True
            continue
        cutted = False

    return "".join(result)


def compare_table_definitions(tbl1: str, tbl2: str, max_diff: int = 25) -> bool:
    # Extract w:tblW values
    def get_tblW(text):
        match = re.search(r'<w:tblW[^>]*w:w="(-?\d+)"', text)
        return int(match.group(1)) if match else None

    # Extract list of gridCol values
    def get_gridCols(text):
        return [int(w) for w in re.findall(r'<w:gridCol[^>]*w:w="(\d+)"', text)]

    # Clean text: remove tblW and gridCol lines to compare the rest
    def clean_text(text):
        text = re.sub(r'<w:tblW[^>]*w:w="[^"]+"[^>]*/>', "", text)
        text = re.sub(r'<w:gridCol[^>]*w:w="[^"]+"[^>]*/>', "", text)
        return text.strip()

    tblW1 = get_tblW(tbl1)
    tblW2 = get_tblW(tbl2)

    if tblW1 is None or tblW2 is None:
        return False
    if abs(tblW1 - tblW2) > max_diff:
        return False

    grid1 = get_gridCols(tbl1)
    grid2 = get_gridCols(tbl2)

    if len(grid1) != len(grid2):
        return False
    if any(abs(a - b) > max_diff for a, b in zip(grid1, grid2)):
        return False

    if clean_text(tbl1) != clean_text(tbl2):
        return False

    return True


def cut_table_defs(word_xml):
    spl = re.split(r"(<w:tbl>|</w:tbl>)", word_xml)
    levels = 0
    levels_tbl = {}
    rez = []
    for index, value in enumerate(spl):
        if value.strip():
            if value == "<w:tbl>":
                if spl[index + 2] == "</w:tbl>":  # not table in table
                    if "<w:tr" in spl[index + 1]:
                        tr_start_index = spl[index + 1].index("<w:tr")
                        tbl_defs = spl[index + 1][:tr_start_index].replace(" ", "").replace("\n", "")
                        if levels not in levels_tbl:
                            levels_tbl[levels] = tbl_defs
                        else:
                            # if levels_tbl[levels] != tbl_defs:  # New table
                            if not compare_table_definitions(levels_tbl[levels], tbl_defs):  # New table
                                levels_tbl[levels] = tbl_defs
                            else:  # cut table defs
                                if rez[-1] == "</w:tbl>":
                                    rez.pop()
                                    spl[index + 1] = spl[index + 1][tr_start_index - 1 :]
                                    continue
                else:  # table in table
                    levels += 1
            rez.append(value)
    return "".join(rez)


def convert_r_to_word_r(spreadsheetml_input):
    root = ET.fromstring(f'<root xmlns="{NS_SPREADSHEET}">{spreadsheetml_input}</root>')
    r_elements = root.findall(f"{{{NS_SPREADSHEET}}}r")
    w_p = ET.Element(f"{{{NS_WORD}}}p")
    for r_element in r_elements:
        w_r = ET.Element(f"{{{NS_WORD}}}r")

        # Create run properties
        rPr_src = r_element.find(f"{{{NS_SPREADSHEET}}}rPr")
        if rPr_src is not None:
            w_rPr = ET.SubElement(w_r, f"{{{NS_WORD}}}rPr")

            # Font size
            sz = rPr_src.find(f"{{{NS_SPREADSHEET}}}sz")
            if sz is not None:
                val = int(_num(sz.attrib["val"])) * 2  # Word uses half-points
                ET.SubElement(w_rPr, f"{{{NS_WORD}}}sz", {"w:val": str(val)})

            # Font
            rFont = rPr_src.find(f"{{{NS_SPREADSHEET}}}rFont")
            if rFont is not None:
                font_val = rFont.attrib["val"]
                ET.SubElement(w_rPr, f"{{{NS_WORD}}}rFonts", {"w:ascii": font_val})

            # Color (remove FF alpha)
            color = rPr_src.find(f"{{{NS_SPREADSHEET}}}color")
            if color is not None:
                if rgb := color.attrib.get("rgb"):
                    if rgb.startswith("FF"):
                        rgb = rgb[2:]
                    ET.SubElement(w_rPr, f"{{{NS_WORD}}}color", {"w:val": rgb})

        # Text content
        t = r_element.find(f"{{{NS_SPREADSHEET}}}t")
        if t is not None:
            w_t = ET.SubElement(w_r, f"{{{NS_WORD}}}t")
            w_t.set("xml:space", "preserve")
            w_t.text = t.text
        w_p.append(w_r)

    word_xml = ET.tostring(w_p, encoding="unicode")
    return "".join([f"<w:r>{x}</w:r>" for x in re.findall(r"<w:r>(.*?)</w:r>", word_xml, re.DOTALL)])


def get_rich_text_tags(xml_part, tag):
    res = []
    for match in re.finditer(tag, xml_part):
        start_position = match.start()
        end_position = match.end()
        while True:
            r_start = xml_part[:start_position].rfind("<w:r")
            if xml_part[r_start + 4] in [" ", ">"]:
                break
            else:
                start_position = r_start - 1
        r_end = xml_part[end_position:].find("</w:r>") + end_position + 6
        if (s := xml_part[r_start:r_end]) not in res:
            res.append(s)
    return res


class q2data2docx:
    def __init__(
        self,
        dataDic={},
        docxTemplateBinary="",
        xlsxBinary="",
        jsonBinary="",
        dataRowLimit=0,
        dataSectionLimit=0,
    ):

        self.error = ""
        self.warning = ""
        self.dataRowLimitWarning = ""
        self.xlsxBinary = None
        self.jsonBinary = None
        self.docxTemplateBinary = None
        self.dataDic = dataDic

        self.usedFormatStrings = {}

        self.dataRowsCount = 0
        self.dataSectionCount = 0

        self.docxSizeLimit = 0
        self.xlsxSizeLimit = 0

        self.dataRowLimit = dataRowLimit
        self.dataSectionLimit = dataSectionLimit

        self.rawFilterRowLimit = 200

        self.xlsxSheetLimit = 0

        self.setJsonBinary(jsonBinary)
        self.setDocxTemplateBinary(docxTemplateBinary)
        self.setXlsxBinary(xlsxBinary)

        self.docxResultBinary = ""

    def setDataRowLimit(self, dataRowLimit=100):
        self.dataRowLimit = dataRowLimit

    def setDataSectionLimit(self, dataSectionLimit=100):
        self.dataSectionLimit = dataSectionLimit

    def setDocxSizeLimit(self, sizeLimit):
        self.docxSizeLimit = sizeLimit

    def setXlsxSizeLimit(self, sizeLimit):
        self.xlsxSizeLimit = sizeLimit

    def setRawFilterRowLimit(self, rawFilterRowLimit):
        self.rawFilterRowLimit = rawFilterRowLimit

    def loadFile(self, fileName):
        return {
            ".json": self.loadJsonFile,
            ".docx": self.loadDocxFile,
            ".xlsx": self.loadXlsxFile,
        }.get(
            os.path.splitext(fileName)[1].lower(), lambda x: None
        )(fileName)

    # prepare excel data
    def loadXlsxFile(self, fileIn):
        if glob.glob(fileIn):
            binXls = None
            try:
                binXls = open(fileIn, "rb").read()
            except Exception:
                return False
            if binXls:
                self.setXlsxBinary(binXls)
            return True
        else:
            return False

    def setXlsxBinary(self, xlsxBinary=None):
        if self.xlsxSizeLimit > 0 and (fileSize := len(xlsxBinary)) > self.xlsxSizeLimit:
            raise ValueError(f"Data file size limit exceeded: {fileSize} bytes > {self.xlsxSizeLimit}")
        self.jsonBinary = ""
        if xlsxBinary:
            self.xlsxBinary = xlsxBinary
            self.xlsxBinary2dataDic()

    def xlsxBinary2dataDic(self):
        if not self.xlsxBinary:
            return
        self.dataRowsCount = 0
        self.dataRowLimitWarning = ""

        memzip = BytesIO()
        memzip.write(self.xlsxBinary)
        xlsxZip = ZipFile(memzip)

        sheetNames = self.extractSheetNames(xlsxZip)
        cellXfs, numFmts = self.extractFormats(xlsxZip)
        sharedStrings = self.extractSharedString(xlsxZip)
        sheetIdDic = self.extractSheets(xlsxZip)

        for x in xlsxZip.namelist():
            if not x.startswith("xl/worksheets/s"):
                continue
            sheetName = sheetIdDic[sheetNames[os.path.basename(x)]]
            if not sheetName:
                return
            sheetText = xlsxZip.open(x).read().decode("utf-8")
            # remove empty cells
            sheetText = "".join(
                [
                    y
                    for y in re.split(r"(<[^<]+>)", sheetText)
                    if y != "" and not (y.startswith("<c") and y.endswith("/>"))
                ]
            )
            for child in ET.fromstring(sheetText):
                if not child.tag.endswith("sheetData"):
                    continue
                for row in child:
                    rowNumber = int(_num(row.attrib["r"]))
                    sheetRow = {}
                    for cell in row:
                        colLetter = re.sub(r"\d", "", cell.attrib["r"])
                        for st in cell:
                            if not st.tag.endswith("}v"):
                                continue
                            # cell.attrib: r = Reference, s = Style Index, t = Cell Data Type
                            # cel datatypes:
                            #   b - boolean
                            #   d - date in ISO8601 format
                            #   e - error
                            #   inlineStr - string that doesn't use the shared string table
                            #   n - number
                            #   s - shared string
                            #   str - formula string
                            if cell.attrib.get("t", "") in ["s"]:  # in sharedStrings
                                sheetRow[colLetter] = sharedStrings[int(st.text)]
                            else:
                                if st.text:  # if any text
                                    sheetRow[colLetter] = st.text
                                    formatStr = numFmts.get(cellXfs.get(cell.attrib.get("s"), ""), "")
                                    # Special case - numeric data w/o datatype and format - exported from GSheets
                                    # if (
                                    #     formatStr == ""
                                    #     and cell.attrib.get("t") is None
                                    #     and re.match(r"^\d*\.*\d*$", sheetRow[colLetter])
                                    # ):
                                    #     formatStr = "#"
                                    sheetRow[colLetter] = self.setNmFmt(sheetRow[colLetter], formatStr)
                                else:
                                    sheetRow[colLetter] = ""
                        if sheetRow[colLetter] == "":
                            del sheetRow[colLetter]
                    if sheetRow != {}:
                        self.check4char(sheetRow)
                        self.dataDic[sheetName][rowNumber] = sheetRow
                        self.dataRowsCount += 1
                    if self.dataRowLimit and self.dataRowsCount > self.dataRowLimit:
                        if (
                            w := f"Data row limit ({self.dataRowLimit}) exceeded."
                        ) not in self.dataRowLimitWarning:
                            self.dataRowLimitWarning += ("\n" if self.dataRowLimitWarning else "") + w
                        break

    def extractSheetNames(self, xlsxZip):
        sheetNames = {}
        for child in ET.fromstring(xlsxZip.open("xl/_rels/workbook.xml.rels").read()):
            if child.attrib["Type"].endswith("/worksheet"):
                sheetNames[os.path.basename(child.attrib["Target"])] = child.attrib["Id"]
        return sheetNames

    def extractFormats(self, xlsxZip):
        cellXfs = {}
        numFmts = {}
        for child in ET.fromstring(xlsxZip.open("xl/styles.xml").read()):
            if child.tag.endswith("cellXfs"):
                fCo = 0
                for xf in child:
                    cellXfs[f"{fCo}"] = xf.attrib.get("numFmtId", "")
                    fCo += 1
            if child.tag.endswith("numFmts"):
                for numFmt in child:
                    numFmts[numFmt.attrib.get("numFmtId", "")] = numFmt.attrib.get("formatCode", "")
        numFmts.update(BUILTIN_FORMATS)
        return cellXfs, numFmts

    def extractSharedString(self, xlsxZip):
        strings = xlsxZip.open("xl/sharedStrings.xml").read()
        sharedStrings = []
        for child in re.findall(r"<si>(.*?)</si>", strings.decode("utf8"), re.DOTALL):
            if child.startswith("<t"):
                sharedStrings.append(ET.fromstring(child).text)
            else:
                sharedStrings.append(convert_r_to_word_r(child))
        return sharedStrings

    def extractSheets(self, xlsxZip):
        self.dataDic = {}
        sheetIdDic = {}
        for child in ET.fromstring(xlsxZip.open("xl/workbook.xml").read()):
            if child.tag.endswith("sheets"):
                for sheet in child:
                    for rid in sheet.attrib:
                        if rid.endswith("}id"):
                            sheetIdDic[sheet.attrib[rid]] = sheet.attrib["name"]
                    self.dataDic[sheet.attrib["name"]] = {}
        return sheetIdDic

    def check4char(self, row):
        for key, value in row.items():
            if value is None:
                value = row[key] = ""
            elif value.startswith("<w:r>"):
                continue
            elif "&" in value:
                row[key] = html.escape(value)
            elif "<" in value:
                row[key] = html.escape(value)
            if "#" in value:
                row[key] = re_sharp.sub("&#x23;", value)

    def setNmFmt(self, cellText, formatStr):
        if formatStr not in self.usedFormatStrings:
            self.usedFormatStrings[formatStr] = cellText

        if re.match(r"0\.0*E\+00", formatStr):  # scientific
            ln = len(re.sub(r"0\.|E\+00", "", formatStr))
            cellText = ("{:.%sE}" % ln).format(_num(cellText))
        else:
            cellText = format_number(cellText, formatStr.replace("\\", ""))

        return cellText

    # prepare json data
    def loadJsonFile(self, fileIn):
        if glob.glob(fileIn):
            binJson = None
            try:
                binJson = open(fileIn).read()
            except Exception:
                return False
            if binJson:
                self.setJsonBinary(binJson)
                return True
        return False

    def setJsonBinary(self, jsonBinary=None):
        if self.xlsxSizeLimit > 0 and (fileSize := len(jsonBinary)) > self.xlsxSizeLimit:
            raise ValueError(f"Data file size limit exceeded: {fileSize} bytes > {self.xlsxSizeLimit}")

        self.xlsxBinary = ""
        if jsonBinary:
            self.jsonBinary = jsonBinary
            self.jsonBinary2dataDic()

    def jsonBinary2dataDic(self):
        self.dataDic = json.loads(self.jsonBinary)
        if isinstance(self.dataDic, dict):
            for x in self.dataDic:
                if isinstance(self.dataDic[x], list):
                    self.dataDic[x] = {y: self.dataDic[x][y] for y in range(len(self.dataDic[x]))}
                elif isinstance(self.dataDic[x], dict):
                    self.dataDic[x] = {int(y): self.dataDic[x][y] for y in self.dataDic[x]}
        else:
            self.dataDic = {}
        self.prepareData(self.dataDic)

    def prepareData(self, dataDic):
        pass

    def setDataDic(self, dataDic):
        self.dataDic = dataDic

    # prepare template
    def loadDocxFile(self, fileIn=""):
        if glob.glob(fileIn):
            try:
                binDocx = open(fileIn, "rb").read()
            except Exception:
                return False
            if binDocx:
                self.setDocxTemplateBinary(binDocx)
                return True
        return False

    def setDocxTemplateBinary(self, docxTemplateBinary=None):
        if self.docxSizeLimit > 0 and (fileSize := len(docxTemplateBinary)) > self.docxSizeLimit:
            raise ValueError(f"Template file size limit exceeded: {fileSize} bytes > {self.docxSizeLimit}")

        if docxTemplateBinary:
            self.docxTemplateBinary = docxTemplateBinary

    def cleanPar(self, parList):  # clean paragraph dummy tags
        rez = []
        dxTmp = ""
        for x in parList:
            co = x.count("#")
            if x.startswith("<"):
                if not dxTmp:
                    rez.append(x)
            elif dxTmp:
                dxTmp += x
                if dxTmp.count("#") % 2 == 0:
                    rez.append(dxTmp)
                    dxTmp = ""
            elif co % 2 == 0:
                rez.append(x)
            elif co:
                dxTmp += x
            else:
                rez.append(x)
        return "".join(rez)

    def prepareDocxTemplate(self):
        if self.docxTemplateBinary is None:
            self.error = "Template not found or not loaded"
            return (
                False,
                False,
                False,
            )
        memzip = BytesIO()
        memzip.write(self.docxTemplateBinary)
        docxZip = ZipFile(memzip)
        if "word/document.xml" not in docxZip.namelist():
            return (
                False,
                False,
                False,
            )
        dxDoc = docxZip.open("word/document.xml").read().decode("utf-8").replace("\n", "").replace("\t", "")
        dxDocList = []
        dxBinary = []
        parList = []
        # remove intag formats
        for x in [x for x in re.split(r"(<[^<]+>)", dxDoc) if x != ""]:
            if (x == "<w:p>" or x.startswith("<w:p ") or parList) and x not in ["##"]:  # collecting paragaph
                parList.append(x)
                if x == "</w:p>":  # end of paragraph
                    parXml = "".join(parList)
                    dCount = parXml.count("#")
                    if dCount == 0 or dCount % 2 == 1:  # no or bad template paragraph
                        dxBinary.append(parXml)
                        dxDocList.append(f"<@{(len(dxBinary) - 1)}@>")
                    else:  # template-prepare paragraph
                        dxDocList.append(self.cleanPar(parList))
                    parList = []
            else:
                if "#" in x:
                    dxBinary.append(x)
                    x = f"<@{(len(dxBinary) - 1)}@>"
                dxDocList.append(x)
        return "".join(dxDocList), dxBinary, docxZip

    def merge(self):
        self.error = ""
        self.warning = self.dataRowLimitWarning
        self.dataSectionCount = 0
        dxDoc, dxBinary, docxZip = self.prepareDocxTemplate()
        if not dxDoc:
            return
        tableTags2clean = []
        # table processing
        for tableName in self.dataDic:
            if not isinstance(self.dataDic[tableName], dict):
                continue
            # process snippets
            docxRowXml = self.getSnippetRow(dxDoc, tableName)
            docxRows = []
            for y, docxRowXml_value in enumerate(docxRowXml):
                self.dataSectionCount += 1
                tableTags2clean.append(docxRowXml_value["start_tag"])
                tableTags2clean.append(docxRowXml_value["end_tag"])
                docxRows.append([])
                if self.dataSectionLimit and self.dataSectionCount > self.dataSectionLimit:
                    if (w := f"Data section limit ({self.dataSectionLimit}) exceeded.") not in self.warning:
                        self.warning += ("\n" if self.warning else "") + w
                    break
                # process datatable rows
                (
                    startRow,
                    columnNamesRow,
                    endRow,
                    compiledFilterRow,
                    rawFilterRow,
                    columnNamesProxy,
                ) = self.getTableParams(docxRowXml_value, tableName)

                docDataField = re_get_keys.findall(
                    docxRowXml_value["snippet"][
                        len(docxRowXml_value["start_tag"]) : -len(docxRowXml_value["end_tag"])
                    ]
                )
                if len(self.dataDic[tableName]) == 0:  # got empty sheet
                    continue
                for rowCount in range(1, max(self.dataDic[tableName]) + 1):
                    if startRow and rowCount < startRow or rowCount == columnNamesRow:
                        continue
                    if endRow and rowCount > endRow:
                        break
                    row = DefDict(self.dataDic[tableName].get(rowCount, {}))
                    if not row:
                        continue

                    row.update({columnNamesProxy[x]: row.get(x, "") for x in columnNamesProxy})

                    if compiledFilterRow:
                        if not my_eval(compiledFilterRow, rawFilterRow, row):
                            continue
                    tmpDocxXml = docxRowXml_value["snippet"]
                    # process datatable column:  x:column name
                    for columnName in docDataField:
                        if columnValue := row.get(columnName.replace("#", "").strip(), ""):
                            columnValue = self.preserve_new_line(columnValue)
                            if columnValue.startswith("<w:r>"):
                                tmpDocxXml = self.process_rich_text(tmpDocxXml, columnName, columnValue)
                            else:
                                tmpDocxXml = tmpDocxXml.replace(columnName, columnValue)

                    docxRows[y].append(tmpDocxXml)
            for z, value in enumerate(docxRowXml):
                if docxRows and z < len(docxRows):
                    dxDoc = dxDoc.replace(value["snippet"], "".join(docxRows[z]))
        # processing non table data
        for dataKey, dataValue in self.dataDic.items():
            if dataKey == "":
                continue
            dataValue = self.preserve_new_line(dataValue)
            if not isinstance(self.dataDic[dataKey], dict):
                if dataValue.startswith("<w:r>"):
                    dxDoc = self.process_rich_text(dxDoc, dataKey, dataValue)
                else:
                    dxDoc = re.sub(
                        get_re_pattern(dataKey),
                        dataValue,
                        dxDoc,
                    )
        # process first sheet as non table data
        first_sheet = self.dataDic[list(self.dataDic.keys())[0]]
        if isinstance(first_sheet, dict):
            data_sheet = {
                f"{key}{row_key}": value
                for row_key in first_sheet
                for key, value in first_sheet[row_key].items()
            }
            for cell_key, cell_value in {
                k: data_sheet[k] for k in list(data_sheet)[:FIRST_SHEET_CELLS_LIMIT]
            }.items():
                cell_value = self.preserve_new_line(cell_value)
                if not isinstance(cell_value, dict):
                    if cell_value.startswith("<w:r>"):
                        dxDoc = self.process_rich_text(dxDoc, f"#{cell_key}#", cell_value)
                    else:
                        dxDoc = dxDoc.replace(f"#{cell_key}#", cell_value)
        # remove datatables tags first
        # replace table names to #@#
        for x in tableTags2clean:
            dxDoc = dxDoc.replace(x, "#@#")
        # remove #@# gaps
        startPoint = 0
        while "#@#" in dxDoc[startPoint:]:
            startPoint = parEnd = parStart = dxDoc.index("#@#", startPoint)
            while parStart > 0:
                parStart = dxDoc.rfind("<w:p", 0, parStart)
                if dxDoc[parStart : parStart + 5] in ["<w:p ", "<w:p>"]:
                    break
                if parStart == 0:
                    break
            parEnd = dxDoc.find("</w:p>", parStart)
            if parStart > 0 and parEnd > 0:
                startPoint = parStart
                parXml = dxDoc[parStart : parEnd + 6]
                xmlns = "".join(
                    [
                        f"""xmlns:{y}="{y}{y}" """
                        for y in {
                            x.translate("".maketrans("", "", "</: "))
                            for x in re.findall(r"\W(\w*):", parXml)
                            if x != "xml" and x != ""
                        }
                        if y != "xmlns"
                    ]
                )
                gg = ET.fromstring(f"""<r {xmlns}>{parXml}</r>""")
                parText = (
                    ("".join([x.text for x in gg.findall("./{ww}p/{ww}r/{ww}t")])).replace("#@#", "").strip()
                )
                if parText == "":
                    dxDoc = dxDoc.replace(parXml, "")
                    startPoint = parStart + 1
                else:
                    startPoint = parEnd
            startPoint += 1
        # replace absolute links to table.colLetterRowNumber
        for y in dxDoc.split("</w:t>"):
            y = y.split("<w:t")[-1].split(">")[-1]
            for x in re.findall(r"#\s*(\w*)\.([a-zA-Z]*)(\d*)\s*#", y):
                colRowData = self.dataDic.get(x[0], {}).get(int(_num(x[2])), {}).get(x[1], "")
                if colRowData:
                    colRowData = self.preserve_new_line(colRowData)
                    if colRowData.startswith("<w:r>"):
                        dxDoc = self.process_rich_text(dxDoc, f"#{x[0]}.{x[1]}{x[2]}#", colRowData)
                    else:
                        dxDoc = re.sub(
                            get_re_pattern(x[0] + r"\s*" + "." + r"\s*" + x[1] + r"\s*" + x[2]),
                            colRowData,
                            dxDoc,
                        )

        # remove other unused tags
        dxDoc = dxDoc.replace("##", "")
        # dxDoc = re.sub(r"#(\s*[^#]+\s*)#", "", dxDoc)
        dxDoc = remove_hash_fragments(dxDoc)
        dxDoc = dxDoc.replace("&#x23;", "#")
        if "</w:tbl><w:sectPr>" in dxDoc:  # fix last row at the end of docs
            dxDoc = dxDoc.replace("</w:tbl><w:sectPr>", """</w:tbl><w:p></w:p><w:sectPr>""")
        if "</w:tbl></w:tc>" in dxDoc:  # fix last row at the end of docs
            dxDoc = dxDoc.replace("</w:tbl></w:tc>", """</w:tbl><w:p></w:p></w:tc>""")
        dxDoc = dxDoc.replace("\n", "")

        dxDoc = cut_table_defs(dxDoc)
        dxDoc = dxDoc.replace("&x23;", "#")

        # put back binary data
        for x, value in enumerate(dxBinary):
            dxDoc = dxDoc.replace(f"<@{x}@>", value)
        # create result file as binary
        outmemzip = BytesIO()
        newZip = ZipFile(outmemzip, "w", ZIP_DEFLATED)
        for x in docxZip.namelist():
            docXml = docxZip.open(x).read()
            if x == "word/document.xml":
                docXml = dxDoc.encode("utf8")
            newZip.writestr(x, docXml)
        newZip.close()
        self.docxResultBinary = outmemzip.getvalue()
        return True

    def process_rich_text(self, tmpDocxXml, columnName, columnValue):
        while match := re.search(columnName, tmpDocxXml):
            start_position = match.start()
            end_position = match.end()
            r_end = tmpDocxXml[end_position:].find("</w:t>") + end_position + 6
            tmpDocxXml = tmpDocxXml[:r_end] + columnValue[-6:] + columnValue[:-6] + tmpDocxXml[r_end:]
            tmpDocxXml = tmpDocxXml[:start_position] + tmpDocxXml[end_position:]
        return tmpDocxXml

    def preserve_new_line(self, columnValue):
        if "\n" in columnValue:  # preserve new line
            columnValue = columnValue.replace("\n", "</w:t><w:br/><w:t>")
        return columnValue

    def getSnippetRow(self, xml, tableName):
        rez = []
        table_pattern = r"(#\s*" + tableName + r"\s*\:+[^#]*#)|(#\s*" + tableName + r"\s*#)"
        while True:
            matches = list(re.finditer(table_pattern, xml))
            if len(matches) < 2:
                break
            snippet = ""
            tag1_pos = matches[0].start()
            tableProps = xml[tag1_pos + 1 : xml[tag1_pos + 1 :].index("#") + tag1_pos + 1].replace(
                tableName, ""
            )
            tag2_pos = matches[1].start()
            tag2_pos += xml[tag2_pos + 1 :].index("#") + 2
            snippet = xml[tag1_pos:tag2_pos]
            if not ("<w:tbl>" in snippet and "</w:tbl>" not in snippet):
                rez.append(
                    {
                        "snippet": snippet,
                        "tableProps": tableProps,
                        "start_tag": xml[tag1_pos : tag1_pos + xml[tag1_pos + 1 :].index("#") + 2],
                        "end_tag": xml[matches[1].start() : tag2_pos],
                    }
                )
            xml = xml[(tag2_pos + 1) :]
        return rez

    def getTableParams(self, tableSnippet, tableName):
        tmpTPList = (tableSnippet["tableProps"][1:]).split(":")
        if len(tmpTPList) > 4:
            tmpTPList[3] += ":" + ":".join(tmpTPList[4:])
        tmpTPList = tmpTPList + ([""] * (4 - len(tmpTPList)) if len(tmpTPList) < 4 else [])
        (columnNamesRow, startRow, endRow) = [int(x) if x.isdigit() else 0 for x in tmpTPList[:3]]
        if self.jsonBinary:
            columnNamesRow = 0
        if columnNamesRow != 0 and columnNamesRow in self.dataDic[tableName]:
            columnNamesProxy = self.dataDic[tableName][columnNamesRow]
        else:
            columnNamesProxy = {}
        rawFilterRow = tmpTPList[3]
        compiledFilterRow = None
        if len(rawFilterRow) > self.rawFilterRowLimit:
            if (
                w := f"Filter row lenght limit  ({self.rawFilterRowLimit}:{rawFilterRow}) exceeded."
            ) not in self.warning:
                self.warning += ("\n" if self.warning else "") + w

            # logging.warning(f"Filter row is too long, skipped: ({rawFilterRow})")
        elif rawFilterRow:
            rawFilterRow = html.unescape(rawFilterRow)
            try:
                compiledFilterRow = re.sub(r"([^=!\<\>])(=)([^=])", r"\1\2\2\3", rawFilterRow)
                compiledFilterRow = (
                    compiledFilterRow.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
                )
                compiledFilterRow = compile(compiledFilterRow, "", "eval")
                if [
                    x
                    for x in compiledFilterRow.co_names
                    if x.startswith("__") or (x not in WHITE_LIST and x in dir(__builtins__))
                ]:
                    logging.warning(f"Filter row compile error: {e} ({rawFilterRow})")
                    compiledFilterRow = None
            except Exception as e:
                logging.warning(f"Filter row compile error: {e} ({rawFilterRow})")

        return startRow, columnNamesRow, endRow, compiledFilterRow, rawFilterRow, columnNamesProxy

    # save resust to file
    def checkOutputFileName(self, fileName=""):
        if not fileName.lower().endswith(".docx"):
            fileName += ".docx"

        if not os.path.isdir(os.path.dirname(fileName)):
            os.mkdir(os.path.dirname(fileName))
        co = 0
        name, ext = os.path.splitext(fileName)
        while True:
            if os.path.isfile(fileName):
                try:
                    os.remove(fileName)
                except Exception as e:
                    co += 1
                    fileName = f"{name}{co:03d}{ext}"
                    continue
            break
            # lockfile = f"{os.path.dirname(fileName)}/.~lock.{os.path.basename(fileName)}#"
            # if os.path.isfile(lockfile):
            #     co += 1
            #     fileName = f"{name}{co:03d}{ext}"
            # else:
            #     break
        return fileName

    def saveFile(self, fileOut="", open_output_file=True):
        fileOut = self.checkOutputFileName(fileOut)
        try:
            open(fileOut, "wb").write(self.docxResultBinary)
        except Exception:
            return False
        if open_output_file:
            q2data2docx.open_document(fileOut)
        return fileOut

    @staticmethod
    def open_document(file_name):
        if os.path.isfile(file_name):
            if sys.platform == "win32":
                subprocess.Popen(
                    ["start", os.path.abspath(file_name)],
                    close_fds=True,
                    shell=True,
                    creationflags=subprocess.DETACHED_PROCESS,
                )
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([opener, file_name], close_fds=True, shell=False)
