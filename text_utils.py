def latin1_to_ascii(unicrap):
    """This replaces UNICODE Latin-1 characters with
    something equivalent in 7-bit ASCII. All characters in the standard
    7-bit ASCII range are preserved. In the 8th bit range all the Latin-1
    accented letters are stripped of their accents. Most symbol characters
    are converted to something meaninful. Anything not converted is deleted.
    """
    xlate = {0xc0: 'A', 0xc1: 'A', 0xc2: 'A', 0xc3: 'A', 0xc4: 'A', 0xc5: 'A',
             0xc6: 'Ae', 0xc7: 'C',
             0xc8: 'E', 0xc9: 'E', 0xca: 'E', 0xcb: 'E',
             0xcc: 'I', 0xcd: 'I', 0xce: 'I', 0xcf: 'I',
             0xd0: 'Th', 0xd1: 'N',
             0xd2: 'O', 0xd3: 'O', 0xd4: 'O', 0xd5: 'O', 0xd6: 'O', 0xd8: 'O',
             0xd9: 'U', 0xda: 'U', 0xdb: 'U', 0xdc: 'U',
             0xdd: 'Y', 0xde: 'th', 0xdf: 'ss',
             0xe0: 'a', 0xe1: 'a', 0xe2: 'a', 0xe3: 'a', 0xe4: 'a', 0xe5: 'a',
             0xe6: 'ae', 0xe7: 'c',
             0xe8: 'e', 0xe9: 'e', 0xea: 'e', 0xeb: 'e',
             0xec: 'i', 0xed: 'i', 0xee: 'i', 0xef: 'i',
             0xf0: 'th', 0xf1: 'n',
             0xf2: 'o', 0xf3: 'o', 0xf4: 'o', 0xf5: 'o', 0xf6: 'o', 0xf8: 'o',
             0xf9: 'u', 0xfa: 'u', 0xfb: 'u', 0xfc: 'u',
             0xfd: 'y', 0xfe: 'th', 0xff: 'y',
             0xa1: '!', 0xa2: '{cent}', 0xa3: '{pound}',
             0xa5: '{yen}', 0xa6: '|', 0xa7: '{section}', 0xa8: '{umlaut}',
             0xa9: '{C}', 0xaa: '^a', 0xab: '<<',
             0xad: '-', 0xaf: '_',
             0xb1: '+/-', 0xb2: '^2', 0xb3: '^3', 0xb4: "'",
             0xb5: '{micro}', 0xb6: '{paragraph}', 0xb7: '*', 0xb8: '{cedilla}',
             0xbb: '>>',
             0xbc: '1/4', 0xbd: '1/2', 0xbe: '3/4', 0xbf: '?',
             0xd7: '*', 0xf7: '/'
             }

    r = ''
    for i in unicrap:
        if ord(i) in xlate:
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += i
    return r


def wrap_text_line(line, wrap_limit):
    words = line.split(" ")
    wrapped_lines = []
    current_line = ""

    if len(line) <= wrap_limit:
        return [line]

    for word in words:
        if len(current_line + word) > wrap_limit:
            wrapped_lines.append(current_line)
            current_line = word + " "
        else:
            current_line += word + " "

    wrapped_lines.append(current_line)
    return wrapped_lines


def wrapText(text, wrap_limit):
    wrapped_text = []
    for line in text.split("\n"):
        wrapped_text.extend(wrap_text_line(line, wrap_limit))
    return wrapped_text
