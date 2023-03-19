import pytesseract
import cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import random
from pathlib import Path

## Known bugs: woorden met een streeepje ertussen pakt ie alleen het woord voor het streepje. Gaat meestal wel goed though
import argparse

FILE = "papa_test.jpg"

def filter_words(word,blacklist):
    ## Returns false if word does not meet requirements:
    ##  - is shorter than 3 characters,
    ##  - is in blacklist (when lowercased)
    word = clean_word(word)
    if len(word) <= 3:
        return False

    if word.lower() in blacklist:
        return False

    else:
        return True

def clean_word(word):
    ## Clean the word before it is filtered. Make it lowercase, remove punctuation and 
    # print("woord= '",word, "'")
    word = word.lower()
    ## TODO turn into stem for better filtering
    #save only alphanumeric (\w means alphanumeric, + means any amount)
    match = re.findall('\w+',word)
    if len(match) > 1:
        print(f"Warning: more than 1 word found: {match}. Only returning {match[0]}")
    if match == None or match == []:
        # print("DEBUG: 0 found", word)
        return ''
    return match[0]

def process_file(path):
    image = Image.open(path)

    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    cut_image, answer_dict = process_image(image,data)
    
    # create folders for this project
    orig_path = Path(path)
    project_name = orig_path.stem
    print(orig_path)
    main_folder = Path(project_name + '_processed')
    main_folder.mkdir(exist_ok=True)
    answer_folder = main_folder / 'answers'
    answer_folder.mkdir(exist_ok=True)

    #save cut image in main folder, answers in answers
    cut_image.save(main_folder/f'{project_name}_cut.png')
    for filename, pic in answer_dict.items():
        pic.save(answer_folder/filename)


def get_blacklist():
    ### Blacklisting words
    # top10k dutch words, manual blacklist
    filespaths = ["dutch10000-utf8.txt", "manual_blacklist.txt"]

    blacklist = []
    for filepath in filespaths:
        with open(filepath) as fp:
            blacklist += fp.read().split()

    return blacklist



def process_image(image, data, select_n = 9, start_on_1 = True):
    blacklist = get_blacklist() # get a list of words that are deemed not-interesting for filtering purposes
    image_copy = image.copy() #work on a fresh copy of the original image
    draw = ImageDraw.Draw(image_copy) #enable drawing the squares on the image

    # Loop over the words found in the ocr'd image, filter out words that arent interesting. 
    # TODO, the level part is a bit weird, may not work later on
    word_occurences = [ i for i, word in enumerate(data["text"]) if (filter_words(word,blacklist)) and (data['level'][i] >4)]
    detected_words = []
    cut_word_images = {}

    # Sample {select_n} words from the the interesting words list. These words will be cut out of the original file
    if select_n:
        word_occurences = random.sample(word_occurences, select_n)

    # Process the words that are to be cut from the image.
    for i,occ in enumerate(word_occurences):
        if start_on_1:
            i = i+1
        # extract the width, height, top and left position for that detected word
        w = data["width"][occ]
        h = data["height"][occ]
        l = data["left"][occ]
        t = data["top"][occ]
        halfway_x = l+(w/2) #for placing text, find the center coordinates
        halfway_y = t+(h/2) 
        # define all the surrounding box points
        p1 = (l, t)
        p2 = (l + w, t)
        p3 = (l + w, t + h)
        p4 = (l, t + h)

        cut_word_images[f"{i}.png"] = image_copy.crop((*p1,*p3)) # Cut the word out and save it in a dict so it can be saved.

        # Draw a red box, and fill it in with the number of the word.
        draw.rectangle([p1,p3], outline="red", width=3, fill='red')
        fontsize = int(h)
        font = ImageFont.truetype('arial.ttf', fontsize)
        draw.text((halfway_x,halfway_y), str(i), (255,255,255), anchor='mm', font=font )
        
        detected_words += [data['text'][occ]] # for debugging purposes, save the words in a list too.
    
    return image_copy, cut_word_images


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='File')
    parser.add_argument('-f',"--file", dest='file', type=str, help='Filename of the file that will be parsed')

    args = parser.parse_args()

    if args.file:
        print(f"Processing: {args.file}")
        process_file(Path(args.file))
    else:
        print(f"No file input. Defaulting to {FILE}")
        process_file(Path(FILE))

