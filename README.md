# Reduce_mapping
This is my code to complete the reduce mapping problem using gRPC. The code was built to be run on a windows machine sorry to linux users.
The template specifications for the problem that was completed can be found in the file map-reduce-task.pdf

The map-reduce.proto file is the basis for the function calls between the server and clients, and was used for the generation of the files map-reduce_pb2.py and map_reduce_pb2_grpc.py. These files are generated using the following command "py -m grpc_tools.protoc -I../grpc --python_out=. --pyi_out=. --grpc_python_out=. map-reduce.proto"

The map-reduce_server.py file holds the code for the launching the server and the server class which handles the calls from the clients and distributes the mapping and reduction tasks. The server is started by calling "py .\map-reduce_server.py -n* -m*" in the terminal. The "*" symbols after the "-n" and the "-m" are for the number of mapping tasks and reduction tasks to be completed respectively.

map-reduce_client.py file hold the code for launching the client, handling the calls to and responses from the server, and handles the actuall mapping and reduction functions themselves. To launch the client call "py .\map-reduce_client.py" in a seperate terminal from the server or other clients.

To run the code and test its ability to solve the map reduce problem on the files in the inputs directory with 3 mapping tasks and 3 reduction tasks complete the following steps
1. launch the server by running the command "py .\map-reduce_server.py -N3 -M3" in your terminal from the directory that the code is in
2. launch a client by running the command "py .\map-reduce_client.py" in a seperate terminal in the directory that the code is in 
3. repeat step 2 for as many clients as you would like completing tasks (step 2 and 3 can be complete before step 1)
4. sit back and watch the magic happen

At its current state the solution is complete but I am still looking to return to the code to clean it up and improve its consistency.
