import pytesseract
import cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import random

## Known bugs: woorden met een streeepje ertussen pakt ie alleen het woord voor het streepje. Gaat meestal wel goed though


