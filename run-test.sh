#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NO_COLOR='\033[0m'

run_tests() {
    local test_name=$1
    local test_path=$2

    echo -e "${BLUE}Running tests for ${test_name}${NO_COLOR}"
    python3 -m unittest discover -s "${test_path}" -p "test*.py" -t .
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}${test_name} tests passed successfully!${NO_COLOR}"
    else
        echo -e "${RED}${test_name} tests failed :( ${NO_COLOR}"
    fi
}

run_tests "Entry Parsing" "./entryParsing/tests"
run_tests "Packet Tracker" "./packetTracker/tests"
run_tests "Grouper" "./grouper/tests"
run_tests "Sorters" "./sorter/tests"
run_tests "Joiner OS Support" "./joinerOSCount/tests"
run_tests "Filterers" "./filterer/tests"


