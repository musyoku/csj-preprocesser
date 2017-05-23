# coding: utf-8
from __future__ import print_function
from six.moves import xrange
import argparse, os, codecs, re, jaconv

def parse_file(filename, dirname, out_dir):
	with codecs.open(os.path.join(dirname, filename), "r", "shift_jis") as f:
		print("loading {} ...".format(filename))
		MODE_READING = 1
		MODE_END = 2
		sentences = []
		headers = []
		dataset = []
		skip = False
		for line in f:
			line = line.strip()

			if re.search(r"^%", line):
				continue

			# 開始を検出
			if re.search(r"^[0-9]{4}", line):
				if len(sentences) > 0:
					assert len(headers) > 0
					sentence = "".join(sentences).strip()
					if len(sentence) > 0:
						dataset.append(headers[-1] + " " + sentence)
					sentences = []

				# <雑音>は除外
				if re.search(r"<.+>$", line):
					continue

				header = line.strip()
				if re.search(r"[RL]", header) is None:
					header += "S:"	# stereo
				header = re.sub(r"^[0-9]{4}", "", header)
				header = re.sub(r" ([RLS]):", r":\1:", header)
				header = header.strip()
				headers.append(header)
				skip = False
				print(header)

			# 人名は除外
			patterns = [ur"×", ur"笑", ur"泣", ur"咳"]
			for pattern in patterns:
				if re.search(pattern, line):
					skip = True
					sentences = []
					break
			if skip:
				continue

			# &で分割してカタカナ表記のみ取り出す
			components = line.split("&")
			if len(components) != 2:
				continue
			katakana = components[1].strip()

			katakana = re.sub(r"<[^>]+>", "", katakana)
			katakana = re.sub(r"\([^\)]\)", "", katakana)

			def replace_blackets(prefix, sentence):
				pattern = ur"\({prefix}([^\)\(]+)\)".format(prefix=re.escape(prefix))
				match = re.search(pattern, sentence)
				if match:
					while(match):
						candidate = match.group(1).strip()
						sentence = sentence.replace(match.group(0), candidate)
						match = re.search(pattern, sentence)
				return sentence

			def replace_begin_blackets(prefix, sentence):
				pattern = ur"\({prefix}([^\(\)]+)$".format(prefix=re.escape(prefix))
				match = re.search(pattern, sentence)
				if match:
					while(match):
						candidate = match.group(1).strip()
						sentence = sentence.replace(match.group(0), candidate)
						match = re.search(pattern, sentence)
				return sentence

			def replace_candidates(prefix, sentence):
				pattern = ur"\({prefix}([^\)\(]+)\)".format(prefix=re.escape(prefix))
				match = re.search(pattern, sentence)
				if match:
					while(match):
						candidate = match.group(1).split(";")[-1]
						sentence = sentence.replace(match.group(0), candidate)
						match = re.search(pattern, sentence)
				return sentence
			tags = ["?", "F", "L", "D2", "D", "X", "M", "O", u"咳", u"笑", u"泣"]

			_replaced = katakana
			while True:
				_original = _replaced

				# (W)の処理
				_replaced = replace_candidates("W", _replaced)
				_replaced = replace_candidates("B", _replaced)

				blackets_replaced = _replaced

				# (D)などの処理
				while True:
					blackets_original = blackets_replaced
					for tag in tags:
						blackets_replaced = replace_blackets(tag, blackets_replaced)
					if blackets_original == blackets_replaced:
						break
				_replaced = blackets_original

				if _original == _replaced:
					break

			katakana = _original

			_replaced = katakana
			while True:
				_original = _replaced
				for tag in tags:
					_replaced = replace_begin_blackets(tag, _replaced)
				if _original == _replaced:
					break
			katakana = _original

			katakana = re.sub(r"\)", "", katakana)

			if re.search(ur"[a-zA-Z0-9\(\)<>×]", katakana):
				print(line, ";", katakana)
				raise Exception()

			katakana = katakana.strip()
			if len(katakana) == 0:
				continue

			sentences.append(jaconv.kata2hira(katakana))
			print(sentences[-1])

	# 最後の1ブロックはループから漏れるので明示的に書き込む
	if sentences > 0 and skip == False:
		sentence = "".join(sentences).strip()
		if len(sentence) > 0:
			dataset.append(header + " " + sentence)

	with codecs.open(os.path.join(out_dir, filename), "w", "utf-8") as f:
		f.write("\n".join(dataset))

def parse(dirname, out_dir):
	try:
		os.mkdir(out_dir)
	except:
		pass
	fs = os.listdir(dirname)
	for filename in fs:
		parse_file(filename, dirname, out_dir)


def main(args):
	assert args.csj_dir
	assert args.out_dir
	try:
		os.mkdir(args.out_dir)
	except:
		pass

	trn_dir = args.csj_dir + "/TRN/Form1"

	# debug
	if args.csj_filename:
		parse_file(args.csj_filename, os.path.join(trn_dir, "core"), os.path.join(args.out_dir, "core"))
		return

	parse(os.path.join(trn_dir, "core"), os.path.join(args.out_dir, "core"))
	parse(os.path.join(trn_dir, "noncore"), os.path.join(args.out_dir, "noncore"))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--csj-dir", "-csj", type=str, default=None)
	parser.add_argument("--out-dir", "-out", type=str, default=None)
	parser.add_argument("--csj-filename", "-file", type=str, default=None)
	args = parser.parse_args()
	main(args)