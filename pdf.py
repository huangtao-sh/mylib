from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io

def read_pdf(file_name):
    rsrcmgr = PDFResourceManager(caching=False)
    outp=io.StringIO()
    pagenos=set()
    laparams = LAParams()
    maxpages=0
    device=TextConverter(rsrcmgr,outp,laparams=laparams)
    with open(file_name,'rb')as fp:
        process_pdf(rsrcmgr,device,fp,pagenos,maxpages=maxpages,
            caching=None,check_extractable=True)
    outp.seek(0)
    return outp.read().splitlines()

