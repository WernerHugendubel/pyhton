import cv2
import pytesseract
import os
import re

from PIL import Image

#fw 01.06.2023
#

#sudo apt install imagemagick

#fw 01.06.2023 - 17:00
# area = w * h
#area selbst berechnet! besser sonst hat area
# mit  area = cv2.contourArea ( contour ) NICHT gepasst!

#so gehts irgendwie fast
#. area:  55544 aspect:  4.943396226415095 w:  524 H: 106
#K104142

def replace_chars(in_text):
    """
    Replaces all characters instead of numbers from 'text'.
   
    :param text: Text string to be filtered
    :return: Resulting number
    """
    #list_of_numbers = re.findall(r'\d+', text)
    #[A-Z0-9]
    #only capitals and numbers
    list_of_chars_numbers = re.findall(r'[A-Z0-9]+', in_text)
   
    #print (list_of_chars_numbers)
   
    result_chars = ''.join(list_of_chars_numbers)
    #print (result_chars)
 
    return result_chars



# Load the image
#plate1_klein = "NU 614R"
#plate2_klein = "KI 04142"

#alternative plate2.jpg
img = cv2 . imread ('/home/wfo/Python/plate2.jpg' )

gray = cv2.cvtColor (img,cv2.COLOR_BGR2GRAY)

#ok das geht! zeigt grayscale Bild
#cv2.imshow('grey1',gray)
#cv2.waitKey(0)

blurred = cv2.GaussianBlur ( gray , ( 5 , 5 ) , 0 )

#Pixels with gradient values below threshold1 are discarded, whereas pixels with gradient values above threshold2
#are considered as edges. Pixels with gradient values between these two thresholds are considered as edges
#only if they are connected to pixels with gradient values above threshold2.
#original 50,150

edges = cv2.Canny ( blurred , 40 , 150 )
#cv2.imshow('edges',edges)
#cv2.waitKey(0)


#ok das geht! zeigt Konturen sw
contours , hierarchy = cv2.findContours ( edges , cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for contour in contours:
    x=0
    y=0
    w=0
    h=0
    x , y , w, h = cv2.boundingRect ( contour )
    aspectratio = w / h
    area = cv2.contourArea ( contour )
    area = w * h
    #original area > 1000 < 5000
    #print ('.','area: ',area, 'aspect: ',aspectratio,'w: ',w,'H:',h)
    #if (aspectratio > 3 and aspectratio < 8)  and (area > 200 and area < 600):
    #ok bei erstem Foto mit area > 25000 aspectratio > 4
    #ok bei 2 Kenntafeln .. aber KI O4142 macht Probleme mit O bzw 0 ratio 1.5 area 500
    if (aspectratio > 4.0 and area > 30000.0):
        #cv2.imshow('edges', edges)
        #cv2.waitKey(0)
        #print (x,y,w,h, x+w,y+h, 'area: ',area)
        # This contouris likely to be a licenseplate
        #cv2.rectangle ( img , ( x , y ) , ( x + w, y + h ) , ( 255 , 255 , 0 ) , 4 )
        cv2.rectangle ( img , (0 , x ) , ( 200, 100 ) , ( 255 , 255 , 0 ) , 4 )
        plate_img = img [ y : y+h , x : x+w]

        # Apply thresholding to the license plate image
        plate_gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
       
     
        #aber es geht jetzt plötzlich 17:30
        #versuch äußeren Rand weglassen, damit nur Buchstaben usw. bleiben x+2 y+2 .. und -
        #18:00
        #18:04 ... cv2.rectangle brauchts gar nicht!!!
        #cv2.rectangle ( plate_gray , ( x , y ) , ( x + w, y + h ) , ( 255 , 255 , 0 ) , 2 )
       
        #test 1 statt 0 127, dann 100, ok mit 100 ist sw Kenntafel Buchstabe definierter
        #Pixel values below this threshold are converted to 0 (black),
        #whereas pixel values above this threshold are converted to max_value (white)
        #0,255 original
        ret,plate_thresh = cv2.threshold(plate_gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        cv2.imshow('pl thresh', plate_thresh)
        cv2.waitKey(0)

        #file schreiben
        #filename = "{}.png".format(os.getpid())
        #cv2.imwrite(filename, plate_gray)
        #cv2.imwrite(filename, plate_thresh)
       
        #text = pytesseract.image_to_string('9033.png', config='--psm 11')
       
        #7 geht schon besser z.B. K104142 K 1.04142 # oder NU614R | NU, 614 R ‘
        #1 kennt KI nicht...
        #6 geht auch
        text = pytesseract.image_to_string(plate_thresh, config='--psm 6')
        #--psm 1: Automatic page segmentation with OSD and OCR.
        #-psm 7: Treat the image as a single text line.
        #--psm 8: Treat the image as a single word.
        #--psm 9: Treat the image as a single word in a circle.
        #--psm 10: Treat the image as a single character.
        #--psm 11: Sparse text. Find as much text as possible in no particular order.
       
        print (replace_chars(text),text)
        #cv2.imshow('rechteck', plate_gray)
        #cv2.waitKey(0)
       
        #testbild
        edges = cv2.Canny ( blurred , 40 , 150 )
        #cv2.imshow('edges',edges)
        #cv2.waitKey(0)

# Recognize the text on the license plate using Tesseract OCR
#text = pytesseract.image_to_string(plate_thresh, config='--psm 10')