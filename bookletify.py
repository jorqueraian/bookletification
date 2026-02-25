from PyPDF2 import PdfReader, PdfWriter
from PyPDF2 import PageObject
from PyPDF2 import Transformation
from PyPDF2.generic import AnnotationBuilder
import sys
import re


input_pdf = None
page_scaling = 1.1

print("Attention user. This code has problems and has be deprecated. Please use bookification.py")

if len(sys.argv) > 1 and sys.argv[1] != "-h":
    input_pdf = sys.argv[1]
    if len(sys.argv) > 2:
        page_scaling = float(sys.argv[2])
else:
    print(f"It seems like you need help!\nbookletify <input pdf file> [page scaling = 1.1]")
    sys.exit()


save_directory = "mini-booklet-"+ re.split(r"[\\\/]",input_pdf)[-1]

reader = PdfReader(open(input_pdf,'rb'))
writer = PdfWriter()

num_pages = len(reader.pages)

reader_pages = list(reader.pages) + ([None]*((4-(num_pages % 4))%4))
num_pages += ((4-(num_pages % 4))%4)

# Ok so sadly the printer I use is unable to work with A4 Paper. So this hard codes the right size
page_width = 612 # int(reader_pages[0].mediabox.width)
page_height = 792 # int(reader_pages[1].mediabox.height)

for counter, i in enumerate(range(num_pages//2-1,-1,-1)):
    if counter % 2 == 0:
        page_1 = reader_pages[i]
        page_2 = reader_pages[num_pages-i-1]
    else:
        page_2 = reader_pages[i]
        page_1 = reader_pages[num_pages-i-1]
    
    scale_factor = page_scaling*min(page_width / page_height, (page_height/2)/page_width)
    new_height = scale_factor*page_height
    topbottom_margins = (page_width-new_height)/2

    translated_page = PageObject.create_blank_page(None, page_width, page_height)
    #translated_page.mergeScaledTranslatedPage(page_1, 1, 0, page_height)
    if page_1 is not None:
        page_1.add_transformation(Transformation().scale(scale_factor,scale_factor).rotate(-90).translate(topbottom_margins,page_height+(1-scale_factor)*scale_factor*0))#.translate(0, page_height))
        translated_page.merge_page(page_1)
    if page_2 is not None:
        page_2.add_transformation(Transformation().scale(scale_factor,scale_factor).rotate(-90).translate(topbottom_margins,page_height/2+(1-scale_factor)*scale_factor*0))#.translate(0, page_height))
        translated_page.merge_page(page_2)
    print(f"added pages {i}, {num_pages-i-1}")
    writer.add_page(translated_page)

line_offset = 70
annotation = AnnotationBuilder.line(
    rect=(line_offset, page_height/2-1,page_width-line_offset, page_height/2+1),
    p1=(line_offset, page_height/2),
    p2=(page_width-line_offset, page_height/2)
)

#writer.add_annotation(page_number=0, annotation=annotation,)
#writer.add_annotation(page_number=counter, annotation=annotation)

with open(save_directory, 'wb') as f:
    writer.write(f)

print("DOne! Thank you for using Ian's bookletifier to create your booklets.")