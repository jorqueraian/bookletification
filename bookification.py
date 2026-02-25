from PyPDF2 import PdfReader, PdfWriter
from PyPDF2 import PageObject
from PyPDF2 import Transformation
from PyPDF2.generic import AnnotationBuilder
import sys
import re


input_pdf = None
page_scaling = 1.1
blanks_at_start = 0
blanks_at_end = 0

if len(sys.argv) > 1 and sys.argv[1] != "-h":
    input_pdf = sys.argv[1]
    if len(sys.argv) > 2:
        page_scaling = float(sys.argv[2])
        if len(sys.argv) > 3:
            blanks_at_start = int(sys.argv[3])
            if len(sys.argv) > 4:
                blanks_at_end = int(sys.argv[4])
elif input_pdf is None or (len(sys.argv) > 1 and sys.argv[1] == "-h"):
    print(f"It seems like you need help! <> indicate required fields, and [] indicate optional fields.\nbookification <input pdf file> [page scaling = 1.1] [blanks at start = 0] [blanks at end = 0]")
    sys.exit()

total_blanks = blanks_at_start + blanks_at_end


#if len(sys.argv) > 1 and sys.argv[1] != "-h":
#    input_pdf = sys.argv[1]
#    if len(sys.argv) > 2:
#        page_scaling = float(sys.argv[2])
#else:
#    print(f"It seems like you need help!\nbookletify <input pdf file> [page scaling = 1.1]")
#    sys.exit()

save_directory = "bookified-"+ re.split(r"[\\\/]",input_pdf)[-1]

reader = PdfReader(open(input_pdf,'rb'))
writer = PdfWriter()

num_pages = len(reader.pages)
remainder = 0 

sheets_per_signature = 8
print("Options:")
while sheets_per_signature > 2:
    remainder = (num_pages+total_blanks) % (sheets_per_signature*4)
    num_signatures = int((num_pages+total_blanks)//(sheets_per_signature*4))
    if remainder > 0:
        num_signatures += 1
    print(f"Sheets per signature: {sheets_per_signature}. Number of signatures: {num_signatures}. Blank pages at the end: {0 if remainder == 0 else (sheets_per_signature*4 - remainder)}")
    sheets_per_signature -= 1


input_text = input("Please select the desired number of sheets per signatures(leave blank for 1 signature): ")
if input_text == '':
    input_text = (num_pages + ((4-(num_pages % 4))%4))//4
    
sheets_per_signature = int(input_text)

remainder = (num_pages+total_blanks) % (sheets_per_signature*4)
num_signatures = int((num_pages+total_blanks)//(sheets_per_signature*4))
if remainder > 0:
    num_signatures += 1

total_pages_in_book = sheets_per_signature*4*num_signatures

# Add two blanks at the start and end, and how ever many 
# is needed to make the entire thing divisible by  4
reader_pages = ([None]*blanks_at_start) + list(reader.pages) + ([None]*blanks_at_end)  + ([None]*(total_pages_in_book-(num_pages+total_blanks)))
num_pages = total_pages_in_book
pages_per_signature = sheets_per_signature*4

# Ok so sadly the printer I use is unable to work with A4 Paper. So this hard codes the right size
# this is for the output
page_width = 612 # int(reader_pages[0].mediabox.width)
page_height = 792 # int(reader_pages[1].mediabox.height)

# this is from the input
input_page_width = int(reader_pages[blanks_at_start].mediabox.width)
input_page_height = int(reader_pages[blanks_at_start].mediabox.height)


# This the number of printed pages per signature
# which means the number of pdf pages per signature is 4 times this
for sig in range(num_signatures):
    first_page_in_sig = sig*pages_per_signature

    for counter, i in enumerate(range(pages_per_signature//2-1,-1,-1)):
        if counter % 2 == 0:
            page_1 = reader_pages[first_page_in_sig+i]
            page_2 = reader_pages[first_page_in_sig+pages_per_signature-i-1]
        else:
            page_2 = reader_pages[first_page_in_sig+i]
            page_1 = reader_pages[first_page_in_sig+pages_per_signature-i-1]
        

        scale_factor = page_scaling*(page_height/2)/input_page_width
        new_height = scale_factor*input_page_height
        
        side_margins = ((page_height/2)-scale_factor*input_page_width)/2
        topbottom_margins = (page_width-new_height)/2

        translated_page = PageObject.create_blank_page(None, page_width, page_height)
        #translated_page.mergeScaledTranslatedPage(page_1, 1, 0, page_height)
        if page_1 is not None:
            temp_page = PageObject.create_blank_page(None, page_width, page_height)
            temp_page.merge_page(page_1)
            temp_page.add_transformation(Transformation().scale(scale_factor,scale_factor).rotate(-90).translate(topbottom_margins,page_height-side_margins))#.translate(0, page_height))
            translated_page.merge_page(temp_page)
        if page_2 is not None:
            temp_page = PageObject.create_blank_page(None, page_width, page_height)
            temp_page.merge_page(page_2)
            temp_page.add_transformation(Transformation().scale(scale_factor,scale_factor).rotate(-90).translate(topbottom_margins,page_height/2-side_margins))
            translated_page.merge_page(temp_page)
        print(f"added pages {first_page_in_sig+i}, {first_page_in_sig+pages_per_signature-i-1}")
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