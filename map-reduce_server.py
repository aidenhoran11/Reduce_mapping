from concurrent import futures
import logging
import math
import time
import os
import argparse
import glob
from threading import Event

import grpc
import map_reduce_pb2
import map_reduce_pb2_grpc as services

INPUTS_FILE_LOC = 'inputs'

class MapReduceService (services.DriverServicer):
    def _group_files(self, n: int):
        # group or split the files into n groups
        # num_of_files = len(os.listdir(INPUTS_FILE_LOC))
        # assuming number of map tasks is smaller than number of files
        grouped_files = [[]for _ in range(n)]
        for i, file in enumerate(glob.glob(INPUTS_FILE_LOC + '\\*.txt')):
            group_id = i%n
            grouped_files[group_id].append(file)
        return grouped_files

    
    def __init__(self, n: int, m: int):
        # initialize
        self.stop_event = Event()
        self._n = n
        self._m = m
        self._files_by_group_id = self._group_files(n)
        self._state = "map"
        self._task_num = 0
        self._finished_tasks = 0
        self._start_time = 0
    

    def _next_map_task(self):
        # determine the next map task to provide to the next available driver
        group_id = self._task_num
        # if the last map task has started but not finished set state to idle
        if self._task_num == self._n and self._finished_tasks < self._n:
            self._state = "idle"
        print('the list of list files by group id: %d', self._files_by_group_id)
        self._task_num += 1
        # return the details of the next task
        current_path = os.getcwd()
        return map_reduce_pb2.Details(
            task = self._state,
            workerId= group_id,
            reduceNum = self._m,
            files = self._files_by_group_id[group_id],
            path =current_path
        )


    def _next_reduce_task(self):
        # determine the next reduce task to provide to the next available driver
        current_path = os.getcwd()
        group_id = self._task_num
        self._task_num += 1
        return map_reduce_pb2.Details(
            task = self._state,
            workerId= group_id,
            reduceNum = self._m,
            path = current_path
        )


    def requestTask(self, request, context):
        # send the appropriate task to the driver
        print(self._state)
        if self._state == "reduce":
            return self._next_reduce_task()
        if self._state == "map":
            return self._next_map_task()
        return map_reduce_pb2.Details(task = self._state)
    

    def mapResult(self, request, context):
        # recieve this when the worker has finished with a map task
        self._finished_tasks += 1

        if self._finished_tasks == self._n:
            self._state = "reduce"
            self._task_num = 0
            self._finished_tasks = 0
        return map_reduce_pb2.req(text = "hell yeah")
        

    def reduceResult(self, request, context):
        # this is called when a client has finished the reduce task
        self._finished_tasks += 1
        if self._finished_tasks == self._m:
            self._state = "finished"
            self.stop_event.set()
        return map_reduce_pb2.req(text = "Thanks!")


def serve(service: MapReduceService):
    # start server
    server = grpc.server(futures.ThreadPoolExecutor())
    
    services.add_DriverServicer_to_server(
        service, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    service.stop_event.wait()
    # wait for workers to shut down
    time.sleep(5)
    server.stop(0)

def get_args():
    # get arguments from the user when the file is run
    parser = argparse.ArgumentParser(description='Starts the server.')
    parser.add_argument('-n', dest='n', type=int,
                        required=True, help='Number of Mapping tasks')
    parser.add_argument('-m', dest='m', type=int,
                        required=True, help='Number of Reduction tasks')
    args = parser.parse_args()
    return args.n, args.m

if __name__ == '__main__':
    logging.basicConfig()
    n,m = get_args()
    service = MapReduceService(n,m)
    serve(service)
