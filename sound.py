#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import wave
import sys
import os
import argparse

class Audio:
	def __init__(self, filename):
		self.filename = filename
		self.nframe = 0 #sample数
		self.rframe = 1 #sample rate数
		self.channels = 0 #チャンネル
		self.sampwidth = 0 #sample size

	#return audio file as array of integer
	def read(self):
		#read wav file
		wav = wave.open(self.filename, "r")

		#move to head of the audio file
		wav.rewind()

		self.nframe = wav.getnframes()
		self.rframe = wav.getframerate()
		self.channels = wav.getnchannels()
		self.sampwidth = wav.getsampwidth()

		# read to buffer as binary format
		buf = wav.readframes(self.nframe)
		wav.close()

		if(self.channels == 1):
			audio_data = np.frombuffer(buf, dtype="int16")
		elif(self.channels == 2):
			audio_data = np.frombuffer(buf, dtype="int32")

		return audio_data 

	def is_split(self, y, size):
		if (len(y) > size):
			return True
		return False

	def is_silence(self, iterable):
		if max(iterable)<4096:
			return True
		else:
			return False

	def split_equal(self, y, split_num): 
		segment_points = list()
		size = len(y) / split_num;

		count=1
		while True: 
			if(count==(split_num)):
				break
			segment_points.append(size*count)
			count = count + 1

		segment_points.append(len(y))
		return segment_points

	def split(self, y, time_term, slience_time_term): 
		size = self.rframe*time_term #分割サイズ
		silence_size = self.rframe*slience_time_term #0.1s 無音の場合切る

		segment_points = list()

		count = 1
		count_silence = 0
		start = 0
		offset = 0 #segmentポイントから時間を図り始める

		while True: 
			start = offset + int(count*size + count_silence*silence_size)
			end = offset +	 int(count*size + (count_silence+1)*silence_size)
			# end = start + (count_silence+1)*silence_size

			if not self.is_split(y[start+silence_size/2: ], size):
				break

			z = np.absolute(y[start:end])

			if self.is_silence(z):
				if self.is_split(y[start+end/2: ], size):
					segment_points.append(start+end/2)
					count = count + 1
					count_silence = 0
					offset += start+end/2
				else:
					break
			else:
				count_silence = count_silence + 1		
		
		segment_points.append(len(y))
		return segment_points

	#audioの時間、単位: s
	def audio_time(self):
		return float(self.nframe/self.rframe)

	def write(self, filename, segment_points, audio_data):
		count = 0
		start = 0 
		for end in segment_points:
			version = "{:03d}".format(count)
			w = wave.Wave_write(filename+"/"+ filename+"-"+version+".wav")
			w.setnchannels(self.channels)
			w.setsampwidth(self.sampwidth)
			w.setframerate(self.rframe)
			w.writeframes(audio_data[start:end])
			start = end 
			w.close()
			count = count+1	

def parse_args():
	parser = argparse.ArgumentParser(description='WAV ファイル分割プログラム')
	parser.add_argument('-i', action='store', dest='file_name',
                help='wavファイルを指定', required=True, type=str)

	parser.add_argument('-type', action='store', type=str, dest='type', default="equal",
                help='分割種類の選択: 等分割、無音分割(equal | optional), デフォルト: euqal')
	parser.add_argument('-n', action='store', type=int, dest='split_num', default=2,
                help='等分割の場合, 分割数を設定, デフィルト: 2')

	parser.add_argument('-t', action='store', type=int, dest='time', default=300,
                help='各分割ファイルの最低サイズ, 単位: 秒, デフォルト: 300s')
	parser.add_argument('-st', action='store', type=float, dest='slience_time', default=1,
                help='無音ターム, 単位: 秒, デフォルト: 1s')

	parser.add_argument('--version', action='version', version='%(prog)s 1.0')

	results = parser.parse_args()
	return results

try:
	#引数の解析
	args = parse_args()

	#add progress bar, time_term, 無音term
	audio = Audio(args.file_name)
	audio_data  = audio.read()
	# time = audio.audio_time()
	if args.type=="equal": 
		segment_points = audio.split_equal(audio_data, args.split_num)
	elif args.type=="optional": 
		segment_points = audio.split(audio_data, args.time, args.slience_time)
	

	output = os.path.splitext(os.path.basename(args.file_name))
	os.system("sh check.sh " + output[0])
	audio.write(output[0], segment_points, audio_data)
except:
	print("FALSE")
	raise
