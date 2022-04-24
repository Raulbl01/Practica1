from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
import random


N = 5
NPROD = 4
NCONS = 1

def delay(factor = 3):
    sleep(0.05)

def add_data(lst_val, mutex):
    mutex.acquire()
    try:
        pos=int(current_process().name)
        lst_val[pos] = lst_val[pos] + random.randint(1,5)
        delay(6)
    finally:
        mutex.release()


def get_data(lst_val, lst_res, empty, mutex):
    mutex.acquire()
    try:
        pos_consumed = 0
        lst_val_pos = [x for x in lst_val if x >= 0]
        #print(f"{lst_val_pos}")
        for y in range(len(lst_val)):
             if lst_val[y] == min(lst_val_pos):
                 pos_consumed = y
        lst_res.append(lst_val[pos_consumed])
        empty[pos_consumed].release()

        delay(6)
    finally:
        mutex.release()

def is_the_end(lst_val, mutex):
    mutex.acquire()
    products = True
    i = 0
    while products and i < len(lst_val):
        products = products and lst_val[i] == -1
        i = i + 1
    mutex.release()
    return products


def producer(lst_val, empty, non_empty, mutex):
    pos=int(current_process().name)
    for v in range(N):
        #print (f"producer {current_process().name} produciendo")
        delay(6)
        empty.acquire()
        add_data(lst_val, mutex)
        print (f"producer {current_process().name} produccion {v}")
        non_empty.release()
    empty.acquire()
    mutex.acquire()
    lst_val[pos]=-1
    print(f"{[x for x in lst_val]}")
    mutex.release()
    non_empty.release()
    # Cuando termine hay que meter el -1, para al final de las iteraciones, sepa el consumidor cual

def merge(lst_val, lst_res, empty, non_empty, mutex):
    #Primera iteracion, esperamos a que produzcan el primer producto todos los prod.
    for w in range(NPROD):
        non_empty.acquire()
    # Si ya han acabado, vamos a consumir, alternando (CONS-PROD)
    # Hay que consumir los N*NPROD productos
    print(f"{[x for x in lst_val]}")
    while not is_the_end(lst_val, mutex):
        #print (f"merge {current_process().name} consumiendo")
        delay(6)
        get_data(lst_val, lst_res, empty, mutex)
        #print (f"merge {current_process().name} consumido {v}, lista: {lst_res}")
        non_empty.acquire()
    print(f"{lst_res}")


def main():
    lst_val = Array('i',NPROD)
    lst_res = []
    non_empty = Semaphore(0)
    empty = [Lock() for i in range(NPROD)]
    mutex = Lock()
    lst_prod = [ Process(target=producer,
                                  name=f"{i}",
                                  args=(lst_val, empty[i], non_empty, mutex))  for i in range(NPROD) ]

    consumidor = Process(target=merge,name="consumidor",args=(lst_val, lst_res, empty, non_empty, mutex))
    for p in lst_prod:
       print(f"arrancando productor {p.name}")
       p.start()
    print(f"arrancando consumidor {consumidor.name}")
    consumidor.start()

    for p in lst_prod:
        p.join()
    consumidor.join()

if __name__ == '__main__':
    main()
