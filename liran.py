'''
    Модуль синтаксически разбирает текст, содержащий
    спискок позиционных обозначений или списком натуральных чисел
    в виде отдельных позиционных обозначений (чисел) или их диаппазонов.
    Выдаёт полный список позиционных обозначений (чисел), либо
    эквивалентный список, состоящий из диапазонов.
'''

import re



MINUS = ('-', '−', '–')
SPACES = (' ','\t','\r','\n')



def parse_int_list(plain_text):
    dict_of_lists = {}
    for line_number, string in enumerate(plain_text.split('\n')):
        values = re.findall(r'[\.,;\s]{0,}(\d{1,}|[-−–])[\.,;\s]{0,}', string)

        if values != [] and (values[0] in MINUS or values[-1] in MINUS):
            return {'Error #1':
                    'Format not valid! Text at line {} not correct.'.format(line_number + 1)}

        index = 0
        while index < len(values):
            if values[index] in MINUS:
                if values[index] == values[index - 1]:
                    del values[index]
                else:
                    index += 1
            else:
                values[index] = int(values[index])
                index += 1

        index = 0
        while index < len(values):
            if values[index] in MINUS:
                range_values = []
                for number in range(values[index - 1] + 1, values[index + 1]):
                    range_values.append(number)
                values = values[:index] + range_values + values[index + 1:]
                index = index + len(range_values)
            else:
                index += 1

        unique_values = []
        for value in values:
            if value in unique_values:
                continue
            unique_values.append(value)

        dict_of_lists[str(line_number + 1)] = unique_values
    return dict_of_lists


def parse_pos_desg(plain_text):
    plain_text = re.sub(r'[\.,;\s]', '', plain_text)

    letters_iter = re.finditer(r'[A-Za-z]{1,2}', plain_text)
    numbers_iter = re.finditer(r'[0-9]{1,}', plain_text)
    dict_of_pos_desg = {}

    prev_letter = None
    prev_number = None
    for letter_obj in letters_iter:
        number_obj = next(numbers_iter)

        letter = letter_obj.group()
        number = int(number_obj.group())
        # Если после буквы в поз. обознач. отсутствует цифра...
        # это может быть как ошибкой форматирования,
        # так и ошибкой содержания
        if letter_obj.end() != number_obj.start():
            return {'Error #1':
                    'Format not valid! Signification: '
                    '{}{}'.format(letter,number)}
        if plain_text[letter_obj.start() - 1] in MINUS:
            # Если буквы поз. обозначений одного диапазона не совпадают...
            if prev_letter != letter:
                return {'Error #2':
                        'Format not valid! Signification: '
                        '{}{}'.format(prev_letter,prev_number)}
            # Если номер начала диапазона больше либо равен номеру конца...
            if prev_number >= number:
                return {'Error #3':
                        'Format not valid! Signification: '
                        '{}{}'.format(prev_letter,prev_number)}

            for dig in range(prev_number + 1, number):
                # Если поз. обознач. повторяется...
                if dig in dict_of_pos_desg[letter]:
                    return {'Error #4':
                            'Format not valid! Signification: '
                            '{}{}'.format(letter,prev_number)}
                dict_of_pos_desg[letter].append(dig)
        prev_letter = letter
        prev_number = number

        if letter in dict_of_pos_desg:
            # Если поз. обознач. повторяется...
            if number in dict_of_pos_desg[letter]:
                return {'Error #4':
                        'Format not valid! Signification: '
                        '{}{}'.format(letter,number)}
            dict_of_pos_desg[letter].append(number)
        else:
            dict_of_pos_desg[letter] = [number]

    return dict_of_pos_desg
    '''
        нет проверки правильности форматирования:
            - на наличие запятой между поз. обознач.
            - на отсутствие пробела перед запятой и его наличие после
    '''


def parse(plain_text):
    for sign in plain_text:
        if sign not in SPACES:
            if   sign.isdigit():
                return parse_int_list(plain_text)
            elif sign.isalpha():
                return parse_pos_desg(plain_text)
            else:
                return {'Error #0':
                        'Format not valid! Start of text not correct.'}


def get_full(dict_of_lists, sep=';', ends='\n', end=''):
    full_list = ''
    for key in dict_of_lists:
        if key.isdigit():
            letter = ''
        else:
            letter = key
        if dict_of_lists[key] == []:
            full_list += ends
        else:
            dict_of_lists[key].sort()
            for number in dict_of_lists[key]:
                full_list += '{}{}{}'.format(letter, number, sep)
            full_list = full_list[:-len(sep)] + ends
    full_list = full_list[:-len(ends)] + end
    return full_list


def get_ranges(dict_of_lists, rsep='-', sep=';', ends='\n', end=''):
    ranges = ''
    for key in dict_of_lists:
        if key.isdigit():
            letter = ''
        else:
            letter = key
        if dict_of_lists[key] == []:
            ranges += ends
        else:
            dict_of_lists[key].sort()

            prev_num = -2
            prev_count_of_consecutive_numbers = 1
            for index, number in enumerate(dict_of_lists[key]):
                if prev_num + 1 == number:
                    count_of_consecutive_numbers += 1
                    if index + 1 == len(dict_of_lists[key]): # end of list
                        if   count_of_consecutive_numbers == 2:
                            ranges += '{}{}{}'.format(letter, number, sep)
                        elif count_of_consecutive_numbers  > 2:
                            ranges = ranges[:-len(sep)] + rsep
                            ranges += '{}{}{}'.format(letter, number, sep)
                else:
                    count_of_consecutive_numbers = 1
                    if   prev_count_of_consecutive_numbers == 1:
                        ranges += '{}{}{}'.format(letter, number, sep)
                    elif prev_count_of_consecutive_numbers == 2:
                        ranges += '{}{}{}'.format(letter, prev_num, sep)
                        ranges += '{}{}{}'.format(letter, number, sep)
                    elif prev_count_of_consecutive_numbers  > 2:
                        ranges = ranges[:-len(sep)] + rsep
                        ranges += '{}{}{}'.format(letter, prev_num, sep)
                        ranges += '{}{}{}'.format(letter, number, sep)
                prev_num = number
                prev_count_of_consecutive_numbers = count_of_consecutive_numbers
            ranges = ranges[:-len(sep)] + ends
    ranges = ranges[:-len(ends)] + end
    return ranges



if __name__ == '__main__':
    IN_DATA_TYPE = 0 # 0 - позиционные обозначения,
                     # 2 - натуральные числа
    OUT_DATA_VIEW = 0 # 0 - полный список, без свёрток в диапазоны,
                      # 1 - список свёрнутых в диапазоны значений
    # all test files are on the PROVING GROUND:
    FILE_PATHS = [r'PG/position designations.txt',
                  r'PG/integer list.txt',
                  r'PG/out.csv']
    with open(FILE_PATHS[IN_DATA_TYPE]) as text_file:
        plain_text = text_file.read()

    result = parse(plain_text)

    for key in result:
        if key.startswith('Error'):
            print('{}: {}'.format(key, result[key])) # сообщение об ошибке
        else:
            if OUT_DATA_VIEW == 0:
                out_text = get_full(result)
            elif OUT_DATA_VIEW == 1:
                out_text = get_ranges(result)
            with open(FILE_PATHS[2], 'w') as text_file:
                text_file.write(out_text)
            print('Done. No errors.')
            break