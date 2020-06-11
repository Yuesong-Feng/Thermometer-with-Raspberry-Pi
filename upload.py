import base64
import requests,json
import os
def ToBase64(file, txt):
    with open(file, 'rb') as fileObj:
        image_data = fileObj.read()
        base64_data = base64.b64encode(image_data)
        fout = open(txt, 'w')
        fout.write(base64_data.decode())
        fout.close()
def ToFile(txt, file):
    with open(txt, 'r') as fileObj:
        base64_data = fileObj.read()
        ori_image_data = base64.b64decode(base64_data)
        fout = open(file, 'wb')
        fout.write(ori_image_data)
        fout.close()
ToBase64("data5.wav",'data5_base64.txt')
with open('data5_base64.txt','r',encoding='utf-8') as f:
     content = f.read()
size = os.path.getsize('data5.wav')
url = 'http://tempscan.applinzi.com/tempscan/uploadRecord'
data1 = {
    "temp": 35.34893840000,
    "time": "2020-05-20 19:30:20",
    "ftype": "wav",
    "flen": size,
    "audio": content
}
print(data1)
r = requests.post(url,data=json.dumps(data1))
print(r.text)
print(r.status_code)