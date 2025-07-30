# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpio.transformations.transformations import swc2code_py, message2code_py, swc2launch, swc2main, swc2dockerCompose, update_robosapiensIO_ini, add_backbone_config, robochart2aadlmessages, robochart2logical
from rpio.utils.auxiliary import *
from rpio.parsers.parsers import *
from rpio.metamodels.aadl2_IL import *

import configparser
import sys
import os


# ------------------------------------------------------------------------------------
# ------------------------------ CONSTANTS ------------------------------------------
# ------------------------------------------------------------------------------------

BASE_DIR = os.getcwd()

DESIGN_DIR = os.path.join(BASE_DIR, "Design", "design.json")
RPIO_INI_DIR = os.path.join(BASE_DIR,"robosapiensIO.ini")

MESSAGES_DIR = os.path.join(BASE_DIR, "Realization", "Messages")
NODES_DIR = os.path.join(BASE_DIR,  "Realization", "Nodes")
PLATFORM_DIR = os.path.join(BASE_DIR,  "Realization","Platform")
RESOURCES_DIR = os.path.join(BASE_DIR, "Resources")

CONCEPT_DIR = os.path.join(BASE_DIR, "Concept")
MAPLE_RCT = os.path.join(CONCEPT_DIR, "MAPLE-K.rct")
MONITOR_RCT = os.path.join(CONCEPT_DIR, "Monitor.rct")
ANALYSIS_RCT = os.path.join(CONCEPT_DIR, "Analysis.rct")
PLAN_RCT = os.path.join(CONCEPT_DIR, "Plan.rct")
LEGITIMATE_RCT = os.path.join(CONCEPT_DIR, "Legitimate.rct")
EXECUTE_RCT = os.path.join(CONCEPT_DIR, "Execute.rct")
KNOWLEDGE_RCT = os.path.join(CONCEPT_DIR, "Knowledge.rct")

# ------------------------------------------------------------------------------------
# ------------------------------AADL2CODE TASKS --------------------------------------
# ------------------------------------------------------------------------------------
def t_load_design():
    # load name and description from ini
    config = configparser.ConfigParser()
    try:
        config.read(RPIO_INI_DIR)
        name = config['RoboSAPIENSIO']['name']
        description = config['RoboSAPIENSIO']['description']
        try:
            design = system(name=name, description=description, JSONDescriptor=DESIGN_DIR)  # TODO: load AADL when AADL parser is complete
        except:
            print("Design file not found. Please check the path.")
            design = None
    except:
        print("Could not load name and description from ini file")
        design = None
    return design

def t_generate_messages():
    try:
        design = t_load_design()
        # generate messages using the constants for managing systems
        message2code_py(system=design, path=MESSAGES_DIR)
        return True
    except:
        print("Failed to generate the messages")
        return False

def t_generate_swc_skeletons():
    try:
        design = t_load_design()
        # generate swc code skeletons using the constant for nodes directory
        swc2code_py(system=design, path=NODES_DIR)
        return True
    except:
        print("Failed to generate the software components")
        return False

def t_generate_swc_launch():
    try:
        design = t_load_design()
        # generate launch files using constants for platform directories
        swc2launch(system=design.systems[0], path=PLATFORM_DIR)
        return True
    except:
        print("Failed to generate the software component launch files")
        return False

def t_generate_main():
    try:
        config = configparser.ConfigParser()
        # use the constant for the ini file
        config.read(RPIO_INI_DIR)
        packageName = config['PACKAGE']['name']
        prefix = config['PACKAGE']['prefix']
        design = t_load_design()
        # generate main launch file using RESOURCES_DIR instead of a literal "../Resources"
        swc2main(system=design.systems[0], package=packageName, prefix=(prefix if prefix != "" else None), path=RESOURCES_DIR)
        return True
    except:
        print("Failed to generate the software component main file for the given platforms")
        return False

def t_generate_docker():
    try:
        design = t_load_design()
        # generate docker compose file using constant for managing platform directory
        swc2dockerCompose(system=design.systems[0], path=PLATFORM_DIR)
        # add backbone config using RESOURCES_DIR
        add_backbone_config(system=design, path=RESOURCES_DIR)
        return True
    except:
        print("Failed to generate the docker compose for the given platforms")
        return False

def t_update_robosapiensIO_ini():
    try:
        config = configparser.ConfigParser()
        config.read(RPIO_INI_DIR)
        packageName = config['PACKAGE']['name']
        prefix = config['PACKAGE']['prefix']
        design = t_load_design()
        # update ini file using the directory of RPIO_INI_DIR instead of a literal "../"
        update_robosapiensIO_ini(system=design, package=packageName, prefix=prefix, path=os.path.dirname(RPIO_INI_DIR))
        return True
    except:
        print("Could not update robosapiensIO.ini")
        return False

# ------------------------------------------------------------------------------------
# --------------------------RoboChart2AADL TASKS -------------------------------------
# ------------------------------------------------------------------------------------

def t_robochart_to_messages():
    try:
        # Parse RoboChart models using the defined constants
        parser = robochart_parser(
            MAPLEK=MAPLE_RCT,
            Monitor=MONITOR_RCT,
            Analysis=ANALYSIS_RCT,
            Plan=PLAN_RCT,
            Legitimate=LEGITIMATE_RCT,
            Execute=EXECUTE_RCT,
            Knowledge=KNOWLEDGE_RCT
        )
        # generate messages, here DESIGN_DIR is used if it represents the design folder;
        # alternatively
        robochart2aadlmessages(maplek=parser.maplek_model, path=DESIGN_DIR)
        return True
    except:
        print("Failed to generate AADL messages from provided RoboChart models")
        return False

def t_robochart_to_logical():
    try:
        # Parse robochart models
        models_parsed = robochart_parser(MAPLEK='../Concept/MAPLE-K.rct',Monitor='../Concept/Monitor.rct',Analysis='../Concept/Analysis.rct',Plan='../Concept/Plan.rct',Legitimate='../Concept/Legitimate.rct',Execute='../Concept/Execute.rct',Knowledge='../Concept/Knowledge.rct')
        # generate logical architecture
        robochart2logical(parsed=models_parsed,path='../Design')
        print("RoboChart to AADL logical architecture is not implemented yet!")
        return True
    except:
        print("Failed to generate AADL logical architecture from provided RoboChart models")
        return False

# ------------------------------------------------------------------------------------
# ------------------------------ CHECKING TASKS --------------------------------------
# ------------------------------------------------------------------------------------
def t_check_robosapiensio():
    check = check_package_installation(package='robosapiensio')
    return check
