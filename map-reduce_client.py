from concurrent import futures
import logging
import math
import time
import os
import argparse
import glob
import re

import grpc
import map_reduce_pb2
from map_reduce_pb2_grpc import DriverStub

SERVER_ADDR = 'localhost:50051'
TEMP_DIR = 'intermediate'
FINAL_DIR = 'out'

clientState = {"working":0, "idle":1, "waiting":2}

class Client:
    def __init__(self):
        self._state = clientState["waiting"]
    

    def _run(self):
        # run the worker
        while(True):
            try:
                response = self._request_task()
                # call the appropriate functions based on the task given by the server
                if response.task == 'map':
                    self._state = clientState["working"]
                    self._map(response.workerId, response.reduceNum, response.files, response.path)
                    self._send_result(response.task)
                elif response.task == 'reduce':
                    self._state = clientState["working"]
                    self._reduce(response.workerId, response.path)
                    self._send_result(response.task)
                elif response.task == "idle":
                    self._state = clientState["idle"]
                else:
                    return

            except grpc._channel._InactiveRpcError:
                self._state = clientState["waiting"]
                time.sleep(5)
                
    
    def _request_task(self):
        # call the request task rpc
        with grpc.insecure_channel(SERVER_ADDR) as channel:
            task_info = DriverStub(channel).requestTask(map_reduce_pb2.req(text="can i please work for money?"))
            return task_info



    def _map(self, workerId: int, reduceNum: int, files: list[str], path: str):
        # map the word in the given file into their respective temporary files
        newPath = path + '\\' + TEMP_DIR
        print(newPath)
        os.makedirs(newPath, exist_ok=True)
        for filename in files:
            # map the given file to the intended intermediate file
            if filename.endswith('.txt'):
                with open(path + '\\' + filename, 'r') as file:
                    text = file.read()
                    for word in text.split():
                        word = re.sub('[^A-Za-z0-9]+', '', word)
                        if word != '':
                            fileId = ord(word[0])%reduceNum
                            tempFile = open(newPath + '\\mr-' + str(workerId) + '-' + str(fileId) + '.txt', 'a+')
                            tempFile.write(word + '\n')
                        file.close()
        print('done mapping')


    def _send_result(self, task):
        # send result of mapping to server
        with grpc.insecure_channel(SERVER_ADDR) as channel:
            stub = DriverStub(channel)
            if task == 'map':
                stub.mapResult(map_reduce_pb2.req(text="I have mapped the words"))
            elif task == 'reduce':
                stub.reduceResult(map_reduce_pb2.req(text="I have reduced the files"))


    def _reduce(self, fileId: int, path: str):
        # reduce the files in the intermediate directory by counting the words and putting them in a new file
        
        # confirm the existence of the new directory
        intermediatePath = path + '\\' + TEMP_DIR + '\\'
        outPath = path + '\\' + FINAL_DIR + '\\'
        print(outPath)
        os.makedirs(outPath, exist_ok=True)

        # count the words in the intermediate directory
        wordCount = {}
        for file in glob.glob(intermediatePath + '\\mr-*-' + str(fileId) + '.txt'):
            with open(file) as f:
                for word in f.readlines():
                    word = re.sub('[^A-Za-z0-9]+', '', word)
                    if word not in wordCount:
                        wordCount[word] = 0
                    wordCount[word] += 1

        # put the word count in a final file in the new directory
        out = open(outPath + '\\mr-' + str(fileId) + '.txt', 'a+')
        for word, count in wordCount.items():
            out.write(word + ':' + str(count) + '\n')
        out.close()
        print('done with reduction!')


if __name__ == '__main__':
    client = Client()
    client._run()
