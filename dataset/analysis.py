import json
import sys

with open('veriseti_v1.0.json') as f:
    data = json.load(f)
cnt = 0
err = 0

for ver in data['veri']:
    for prgrf in ver['paragraflar']:
        metin = prgrf['paragraf_metni']
        for sor_cvp in prgrf['soru_cevaplar']:
            cnt += 1
            print("metin['cevap_baslangici']: ",metin.split()[int(sor_cvp['cevap_baslangici'])])
            print("cevap[0]: ",sor_cvp['cevap'].split()[0])
            if metin.split()[int(sor_cvp['cevap_baslangici'])].lower()!=sor_cvp['cevap'].split()[0].lower():
                err += 1
                print("hata")
                print("paragraf: ",metin)
                print("cevap: ",sor_cvp['cevap'])
                print("cevap baslangici: ",sor_cvp['cevap_baslangici'])
                #sys.exit()
                print(cnt)
                print(err)
