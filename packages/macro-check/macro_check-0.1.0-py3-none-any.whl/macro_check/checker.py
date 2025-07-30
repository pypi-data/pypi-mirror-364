import os
import zipfile
import fitz  # PyMuPDF

def perform_macro_check(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext in ['.doc', '.xls', '.ppt']:
        from oletools.olevba import VBA_Parser
        vbaparser = VBA_Parser(filepath)
        if vbaparser.detect_vba_macros():
            return {"result": "PRESENT"}
        else:
            return {"result": "ABSENT"}

    elif ext in ['.docx', '.xlsx', '.pptx', '.docm', '.xlsm', '.pptm']:
        with zipfile.ZipFile(filepath, 'r') as z:
            has_macro = any('vbaProject.bin' in name for name in z.namelist())
            return {"result": "PRESENT" if has_macro else "ABSENT"}

    elif ext == '.pdf':
        doc = fitz.open(filepath)
        suspicious = any("/JavaScript" in doc.xref_object(i) for i in range(1, doc.xref_length()))
        return {"result": "PRESENT" if suspicious else "ABSENT"}

    else:
        return {"result": "UNSUPPORTED_FORMAT"}
