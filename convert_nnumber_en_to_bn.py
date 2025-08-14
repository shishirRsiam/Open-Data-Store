
def convert_number_en_to_bn(self, en_number):
    en_to_bn = {
        ' ': '', '-': '-', '0': '০', '1': '১',
        '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬',
        '7': '৭', '8': '৮', '9': '৯',
    }
    if en_number[:1] == '+':
        en_number = en_number[1:]
    if en_number[:2] == '88':
        en_number = en_number[2:]

    bn_number = ''
    for ch in en_number:
        bn_number += en_to_bn[ch]
        
    print(en_number)
    print(bn_number)
    return bn_number

number = '0 1780-550608'
print(convert_number_en_to_bn("", number))