__author__ = 'gordonkeller'

import filecmp
import getpass
import os
import pysftp
from shutil import copyfile, rmtree
from os import listdir
from os.path import isfile, join

class Project:
    def __init__(self, projPath):
        self.pp = projPath
        self.files = []

    def addFile(self, fileName):
        self.files.append(fileName)
    def remFile(self, fileName):
        self.files.remove(fileName)

def ArgMin(num_param, list_param):
    if len(list_param) < num_param:
        return False
    else:
        return True

_hn = ""
_un = ""
_pw = ""

curr_dir = ""
curr_subdir = ""
curr_subsubdir = ""
proj_list = []
error_flag = False

def ListInfo():
    print("\n\n|-----------------------------------------------------------------------------------|")
    print("                                 information                                       ")
    print("|-----------------------------------------------------------------------------------|")
    if not curr_dir:
        print(" current directory (full path): none selected")
    elif not curr_subdir:
        print(" current directory (full path): " + curr_dir + "/(need subdir)...")
    elif not curr_subsubdir:
        print(" current directory (full path): " + curr_dir + "/" + curr_subdir + "/(need subsubdir)")
    else:
        print(" current directory (full path): " + curr_dir + "/" + curr_subdir + "/" + curr_subsubdir)
    print("|-----------------------------------------------------------------------------------|")
    if not proj_list:
        print(" No projects added")
    for i in range(0, len(proj_list)):
        print(" " + str(i + 1) + "   | " + proj_list[i].pp)
        for j in proj_list[i].files:
            print("     | " + j)
    print("|-----------------------------------------------------------------------------------|\n\n")

def print_menu():
    print"---------------------------------------------------------------------------------------- "
    print" Welcome to Puddin!                                                                      "
    print" Enter in any of the following commands:                                                 "
    print"  - listinfo: gives all available information about transaction information"
    print"  - dirpath (path): the directory containing the subdirectories to pull files from       "
    print"  - lab (name): the name of the lab folder to pull from"
    print"  - student (name): the student directory containing the files of interest                        "
    print"  - addproj (path): add a project with directory argument to the preexisting ones        "
    print"  - remproj (number)*: removes the list of project numbers from the running list         "
    print"  - addfile (proj number) (files)*: adds the files listed to the project number given    "
    print"  - remfile (proj number) (files)*: removes the files listed from the projects given     "
    print"  - apply: completes the transactions                                                    "
    print"  - reset: clears all current information                                                "
    print"  - q: Exits the program\n"
    print"  (item)* indicates that multiple may be specified"
    print"----------------------------------------------------------------------------------------\n\n "

# wait to run program until user has entered all necessary connection info
while True:
    _hn = ""
    _un = ""
    _pw = ""

    _hn = raw_input("Host name: ")
    _un = raw_input("Username: ")
    _pw = getpass.getpass(prompt="Password: ")

    if not(_hn and _un and _pw):
        print("Please reenter all necessary information.\n")
        continue
    else:
        print("Starting program...\n\n")
        break

print_menu()
while True:
    error_flag = 0
    comm = raw_input("::: ")
    input_list = comm.split(" ")

    # the path to grab children's files from
    if input_list[0] == "dirpath":
        if not ArgMin(2, input_list):
            print("ERROR: not enough arguments")
            continue
        else:
            curr_dir = input_list[1]

    # show all available information
    elif input_list[0] == "listinfo":
        ListInfo()

    # the name of the subdirectory to pull from (no backslash)
    elif input_list[0] == "lab":
        if not ArgMin(2, input_list):
            print("ERROR: not enough arguments")
            continue
        curr_subdir = input_list[1]

    elif input_list[0] == "student":
        if not ArgMin(2, input_list):
            print("ERROR: not enough arguments")
            continue
        curr_subsubdir = input_list[1]

    # add a project with the target directory as the only argument
    elif input_list[0] == "addproj":
        if not ArgMin(2, input_list):
            print("ERROR: not enough arguments")
            continue
        if os.path.isdir(input_list[1]):
            proj_list.append(Project(input_list[1]))
            print("Successfully added project " + str(len(proj_list)))
        else:
            print "ERROR: Project path does not exist."

    # removes any number of projects separated by spaces
    elif input_list[0] == "remproj":
        if not ArgMin(2, input_list):
            print("ERROR: not enough arguments")
            continue

        for i in range(1, len(input_list)):
            if not(input_list[i].isdigit()):
                print("ERROR: argument " + str(input_list[i]) + " is not a valid number")
                error_flag = True
                break
            elif not(i <= len(proj_list)):
                print("ERROR: Project specified doesn't exist")
                error_flag = True
                break

        if not error_flag:
            for i in range(1, len(input_list)):
                print_num = input_list[i]
                proj_list.remove(proj_list[int(input_list[i]) - 1])
                print("Successfully removed project " + print_num)

    # adds any listed files to the project (first argument) as the following arguments
    elif input_list[0] == "addfile":
        if not ArgMin(3, input_list):
            print("ERROR: not enough arguments")
            continue
        if not(input_list[1].isdigit()):
            print("ERROR: second argument is not a number")
        else:
            if not((int(input_list[1]) <= len(proj_list)) and (int(input_list[1]) > 0)):
                print("ERROR: Project specified does not exist")
            else:
                for index in range(2, len(input_list)):
                    proj_list[int(input_list[1]) - 1].addFile(input_list[index])
                print("Successfully added files to project " + input_list[1])

    # removes any listed files from the project (first argument) as the following arguments
    elif input_list[0] == "remfile":
        if not ArgMin(3, input_list):
            print("ERROR: not enough arguments")
            continue
        if not(input_list[1].isdigit()):
            print("ERROR: second argument is not a number")
        else:
            if not((int(input_list[1]) <= len(proj_list)) and (int(input_list[1]) > 0)):
                print("ERROR: Project specified does not exist")
            else:
                for index in range(2, len(input_list)):
                    if input_list[index] not in proj_list[int(input_list[1]) - 1].files:
                        print("WARNING: " + input_list[index] + " not in project")
                    else:
                        proj_list[int(input_list[1]) - 1].remFile(input_list[index])

    # completes the intended transaction
    elif input_list[0] == "apply":
        full_path = curr_dir + "/" + curr_subdir + "/" + curr_subsubdir

        # check that all information necessary is entered
        if curr_dir == "":
            print("ERROR: Specify a directory before applying")
            continue
        if curr_subdir == "":
            print("ERROR: Specify a subdirectory before applying")
            continue

        _sftp = pysftp.Connection(_hn, username=_un, password=_pw)

        # check to make sure that the directory exists
        if not(_sftp.exists(curr_dir + '/' + curr_subdir + '/' + curr_subsubdir)):
            _sftp.close()
            print("ERROR: Remote location specified is not a directory")
            continue

        if not proj_list:
            print("ERROR: Specify at least one project to copy into")
            continue

        else:
            proj_index = 1
            for i in proj_list:
                match_list = []
                full_match_list = []

                if not i.files:
                    _sftp.close()
                    print("WARNING: one or more projects do not have files")
                    break

                temp_path = "./temp_stor"

                if not os.path.exists(temp_path):
                    os.makedirs(temp_path)
                _sftp.get_d(full_path, temp_path)
                full_dir_files = [f for f in listdir(temp_path) if isfile(join(temp_path,f))]
                _sftp.close()

                # grabs all matching file names
                for j in i.files:
                    for k in full_dir_files:
                        if j in k:
                            match_list.append(k)

                match_list.sort(reverse = True)

                # grabs the latest submitted files' names
                for j in i.files:
                    for k in match_list:
                        if j in k:
                            full_match_list.append(k)
                            break

                print full_match_list

                # makes sure that all intended files were found in directory
                for j in i.files:
                    found = False
                    for k in full_match_list:
                        if j in k:
                            found = True
                    if not found:
                        print("ERROR: One or more files not located within subdir - " + j)
                        error_flag = True
                        break

                # move to next project if one file not found
                if error_flag:
                    rmtree(temp_path)
                    print("Transaction failed for project " + str(proj_index))
                    continue

                for j in i.files:
                    for k in full_match_list:
                        if j in k:
                            pathTo = i.pp + "/" + j
                            pathFrom = temp_path  + "/" + k
                            copyfile(pathFrom, pathTo)


                rmtree(temp_path)
                print("Successful transaction for project " + str(proj_index))
                proj_index += 1

    # quits the program
    elif input_list[0] == "q":
        break
    else:
        print "ERROR: Command not recognized."
        continue
