from rembg import remove
from PIL import Image
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from transformers import pipeline
from nltk.corpus import genesis
from transformers import pipeline
import nltk
import requests
import time
import qrcode

_buff_lang = 'en'
_buff_glob = 'null_file'
_buff_glob_lib_inri = 'null'
_buff_glob_lib = 'null'
_buf_glob_rag_coll = {"file":"null","rag_file":"null","pos_x":0.0,"pos_y":0.0,"file_type":"null","content":"null","layer_type":"null"}
_buf_glob_rag_coll_arr = [_buf_glob_rag_coll]

def set_init(_buff_glob_file):
	_buff_glob = _buf_glob_file

def set_lang(_buff_lang_flag):
	_buff_lang = _buf_lang_flag

def add_read_lib_uri(_buff_uri):
	_buff_glob_lib_inri += _buff_uri

def add_read_lib(_buff_uri):
	_buff_glob_lib += _buff_uri

def set_picture(image_file):
	fl_in = image_file
	_w = image_file + "rag_0x_sx_nbx0.png"
	with open(fl_in, "rb") as _fl:
		_buff = _fl.read()
	fl_out = remove(_buff)
	with open(fl_out, "wb") as _fl_buff:
	    	_w.write(_fl_buff)

def set_board(siz_x,siz_y,color_rgb):
	_c_arr = color_rgb.split(',')
	_buff_glob = Image.new("RGB", (siz_x,siz_y), color = (_c_arr[0],_c_arr[1],_c_arr[2]))
	_buff_glob.save(_buff_glob)

def set_text(txt,pos_x,pos_y,format, text_color_rgb):
	_buff_glob_temp = Image.open(_buff_glob)
	_c_w = ImageDraw.Draw(_buff_glob_temp)
	_c_txt = str(txt)
	try:
		font = ImageFont.truetype("arial.ttf", 40)
	except IOError:
		font = ImageFont.load_default()
	_c_pos = (pox_x, pos_y)
	_c_arr = text_color_rgb.split(',')
	_c_txt_rgb = (_c_arr[0], _c_arr[1], _c_arr[2])
	_c_w.text(_c_pos, _c_txt, fill=_c_txt_rgb, font=font)
	_buff_glob_temp.save(_buff_glob)  # Save the image

def set_text_inri(keywords, glob_lang):
	_dbas = genesis.words(keywords)
	_dbas_txt = nltk.Text(_dbas)
	_dbas_txt_coll = [_dbas_txt.generate(length=800),_dbas_txt.generate(length=400),_dbas_txt.generate(length=200),	_dbas_txt.generate(length=100),_dbas_txt.generate(length=80),_dbas_txt.generate(length=40),_dbas_txt.generate(length=20)]
	return _dbas_txt_coll

def set_glob_lang(glob_lang_cod, _dbas_txt):
	_cfg_glob_lang = pipeline("translation", model="Helsinki-NLP/opus-mt-{_buff_lang}-{glob_lang_cod}")
	_txt_glob_lang = _dbas_txt
	_tot_txt_glob_lang = translator(_txt_glob_lang)[0]['translation_text']
	return _tot_txt_glob_lang

def search_image(key_words, _buff_glob_lib_flag, pos_x, pos_y):
	_fl_conn = webdriver.Chrome()
	_buff_uri_lib = _buff_glob_lib.split(';')
	_fl_conn.get(_buf_uri_lib[_buf_glob_lib_flag])
	for _bit in range(1):
		_fl_conn.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
		time.sleep(2)
	_fl_dw = _fl_conn.find_elements(By.CSS_SELECTOR, 'img[alt]')
	for _bit_dw in _fl_dw:
		print(_bit_dw.get_attribute('src'))
		_fl_dw_w = _bit_dw.get_attribute('src')
	_fl_conn.quit()
	_fl_www = requests.get(_fl_dw_w)
	_fl_data_bit = BytesIO(_fl_www.content)
	_buff_glob_fl_data_bit = Image.Open(_fl_data_bit)
	_buff_glob_fl = Image.open(_buff_glob)
	_buff_glob_fl.paste(_buff_glob_fl_data_bit, (pos_x, pos_y))


def search_data(key_words,_buff_uri_index):
	try:
		_www_conn = requests.get(_buf_data_uri[_buff_uri_index++])
		_www_conn.raise_for_status()
		_www = BeautifulSoup(response.text, 'html.parser')
		_txt = _www.get_text()
		if _m.lower() in _txt.lower():
			return f"{_txt.lower()}"
		else:
			_uri = _buf_data_uri[_buff_uri_index++]
			return search_data(key_words,_uri)
		except requests.exceptions.RequestException as e:
			return f"404 - {url}: {e}"

def set_background(key_words):
	_fl_r = Image.open(_buff_glob)
	_fl_r = _fl_r.convert("RGB")
	_buff = _fl_r.getdata()
	_buff_coll = []
	for _pass in _buff:
		if _pass[0] in list(range(190, 256)):
			_buff_coll.append((255, 204, 100))
		else:
			_buff_coll.append(_pass)
	_fl_r.putdata(_buff_coll)
	_fl_r.save(_buff_glob)

def set_comix(_buff_glob_data):
	_buf_glob_data_comix = Image.open(_buf_glob_data)
	_buf_glob_data_comix_x = img.quantize(colors=64)
	_buf_glob_data_comix_x.save(_buf_glob_data)

def set_qrcode(url):
	_uri = url
	_buff_qr_x = qrcode.QRCode(version=1, box_size=10, border=4,)
	_buff_qr_x.add_data(_uri)
	_buff_qr_x.make(fit=True)
	_w = _buff_qr_x.make_image(fill_color="black", back_color="white").convert("RGBA")
	return _w

def add_qrcode(_w, pos_x, pos_y):
	try:
		_fl_qr_w = Image.open(_buff_glob).convert("RGBA")
	except FileNotFoundError:
		print("Background image not found. Skipping pasting.")
	if _fl_qr_w:
		qr_w, qr_h = _w.size
		bg_w, bg_h = _fl_qr_w.size
		pos = (pos_x, pos_y)
		_buff_glob_mx = _buf_glob.split()[-1]
		_fl_qr_w.paste(_w, pos, _buff_glob_mx)
		_fl_qr_w.save(_buff_glob)
	else:
		_fl_qr_w.save(_buff_glob)

def set_sign(author,email):
	_author_sign = author + ":" + email
	set_text(_author_sign,0,0,'LEFT')
