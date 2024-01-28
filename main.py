import os
import sys
import subprocess
import threading
import difflib

#папки по умолчанию 
in_dir = 'in/'
out_dir = 'out/'

# проверка папок по умолчанию
if not  os.path.isdir(in_dir):
    raise FileExistsError('Not fount  "in" folder')
if not  os.path.isdir(out_dir):
    raise FileExistsError('Not fount  "out" folder')


#создаём список дамп файлов во входящей папке
def pcaplist(path:str) -> list:
    out_list = list()
    tmp_list = os.listdir(path)
    for i in tmp_list:
        if i.endswith('.pcap') or i.endswith('.pcapng'):
            out_list.append(i)
    return out_list


#прогоняем файлы через tcpcapinfo
def get_pcap_info(filename:list, i_dir, o_dir):
    print('Processing', i_dir, filename)
    in_filename = ''.join((i_dir, filename))
    out_filename  = ''.join((o_dir, filename + '.txt'))
    result = subprocess.run(['tcpcapinfo', in_filename], stdout=subprocess.PIPE, encoding='utf-8')
    with open(out_filename, 'w') as f:
        f.write(result.stdout)
    #print(result.stdout)


# запускаем обратоку в отдельных тредах для каждого файла ибо так надо
def file_processing(in_list:list):
    threads= []
    for i in in_list:
        th = threading.Thread(target=get_pcap_info, args=(i, in_dir, out_dir))
        threads.append(th)
        th.start()
# це хуйня что бы дождаться окончания обработки всех тредов 
# надо было делать через threading.active_count() но лениво
    for t in threads:
        t.join()
    print('Обработка дампов завершена')


def file_convert(filename:str) -> list:
    with open(filename, 'r') as f:
        txt_list = f.readlines()[8:]
    out_list = list()
    for i in txt_list:
        out_list.append(i.split('\t'))
    return out_list


def compare_files(filename_list:list):
    size_list = len(filename_list)
    for i in range(0, size_list - 1):
        tmp_file1 = ''.join((out_dir, filename_list[i] + '.txt'))
        tmp_file2 = ''.join((out_dir, filename_list[i + 1] + '.txt'))
        out_file = ''.join((out_dir, filename_list[i] + '<->' + filename_list[i + 1] + '.txt'))
        c_txt1 = file_convert(tmp_file1)
        c_txt2 = file_convert(tmp_file2)
        
        max_size = max(len(c_txt1), len(c_txt2))
        diff = list()
        for i in range(0, max_size):
            if c_txt1[i][6] != c_txt2[i][6]:
                diff.append(c_txt1[i])
                diff.append(c_txt2[i])
                diff.append('-----------------------------------------------------------------\n')
        with open(out_file, 'w') as w_f:
            for s in diff:
                w_f.write(str(s))
                w_f.write('\n')



#тутова обрабатываем дампы
list_files = pcaplist('in')
file_processing(list_files)
#тутова сравниваем текстовые файлы
compare_files(list_files)
