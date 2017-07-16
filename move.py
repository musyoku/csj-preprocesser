import os

test_ids_core = [
	"A01M0110",
	"A01M0137",
	"A01M0097",
	"A01M0056",
	"A03F0072",
	"S00M0112",
	"S00F0066",
	"S00M0213",
]
test_ids_noncore = [
	"A04M0123",
	"A04M0121",
	"A04M0051",
	"A03M0156",
	"A03M0112",
	"A03M0106",
	"A05M0011",
	"A02M0012",
	"A03M0016",
	"A06M0064",
	"A06F0135",
	"A01F0034",
	"A01F0063",
	"A01F0001",
	"A01M0141",
	"S00F0019",
	"S00M0079",
	"S01F0105",
	"S00F0152",
	"S00M0070",
	"S00M0008",
	"S00F0148", 
]

wav_dir = "/home/stark/sandbox/CSJ/WAV"
trn_dir = "/home/stark/sandbox/CSJ_"

def move_file(base_dir, category, data_id, ext):
	source_path = os.path.join(base_dir, category, str(data_id) + "." + ext)
	target_path = os.path.join(base_dir, "test", str(data_id) + "." + ext)
	if os.path.isfile(source_path):
		print(source_path)
		os.rename(source_path, target_path)

def move_wav(category, data_id):
	move_file(wav_dir, category, data_id, "wav")

def move_trn(category, data_id):
	move_file(trn_dir, category, data_id, "trn")

try:
	os.mkdir(os.path.join(wav_dir, "test"))
except:
	pass
try:
	os.mkdir(os.path.join(trn_dir, "test"))
except:
	pass

for data_id in test_ids_core:
	move_wav("core", data_id)
	move_trn("core", data_id)

for data_id in test_ids_noncore:
	move_wav("noncore", data_id)
	move_trn("noncore", data_id)
