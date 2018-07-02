# -*- coding: utf-8 -*-

while True:
    line = raw_input('Sormak istediğiniz soruyu yazınız(çıkmak için "QUIT" yazınız): ')
    if line == 'QUIT':
        break
    print 'Yazılan soru: "%s"' % line
