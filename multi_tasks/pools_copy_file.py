import os
import multiprocessing 
from multiprocessing import Manager

def copy_file(queue, file_name, old_folder_name, new_folder_name):
    # print('-----模拟copy%s文件: 从%s------> 到%s' % (file_name, old_folder_name, new_folder_name))
    with open(old_folder_name + '/' + file_name, 'rb') as fp:
        content = fp.read()

    with open(new_folder_name + '/' + file_name, 'wb') as fp:
        fp.write(content)

    # 如果完成copy，就往队列中放入一各消息，实现通信
    queue.put(file_name)

def main():
    # 1. 获取用户要copy的文件夹的名字
    old_fold_name = input('请输入要copy的文件夹的名字：')
    # 2. 创建一个新的文件夹
    try:
        new_fold_name = old_fold_name + '[复件]'
        os.mkdir(old_fold_name + '[复件]')
    except:
        pass
    # 3. 获取文件夹下所有的文件
    file_names = os.listdir(old_fold_name)
    # print(file_names)

    # 4. 创建进程池
    po = multiprocessing.Pool(5)

    # 若要实现进度表打印，则需要和主进程通信，用Queue队列
    # 完成进程池中的通信，只能用Manger中的队列
    q = Manager().Queue()  

    # 5. 向进程池加入copy文件的任务
    for file_name in file_names:
        po.apply_async(copy_file, args=(q, file_name, old_fold_name, new_fold_name))

    po.close()
    # po.join()
    
    copy_ok = 0
    while True:  # 主进程显示进度更佳，闲着也是闲着
        single_name = q.get()
        # print('已经完成copy： %s' % single_name)

        # 实现进度条打印
        copy_ok += 1
        print('\r----------完成进度%0.2f %%-------------' % (copy_ok / len(file_names) * 100), end = '')

        # 跳出进程，否则会一直等待
        if copy_ok == len(file_names):
            break

if __name__ == '__main__':
    main()