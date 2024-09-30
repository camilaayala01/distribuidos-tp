#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NO_COLOR='\033[0m'

# execute entry parsing tests
echo -e "${BLUE}Running tests for entry parsing modules${NO_COLOR}"
python3 -m unittest discover -s ./entryParsing/tests -p "test*.py" -t .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Entry parsing tests passed successfully!${NO_COLOR}"
else
    echo -e "${RED}Entry parsing tests failed :( ${NO_COLOR}"
fi

# execute sorter tests
echo -e "${BLUE}Running tests for sorters${NO_COLOR}"
python3 -m unittest discover -s ./sorterTopFinder/tests -p "test*.py" -t .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Sorter tests passed successfully!${NO_COLOR}"
else
    echo -e "${RED}Sorter tests failed :( ${NO_COLOR}"
fi

# execute joiner os tests
echo -e "${BLUE}Running tests for Joiner that counts OS support${NO_COLOR}"
python3 -m unittest discover -s ./joinerOsCount/tests -p "test*.py" -t .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Entry parsing tests passed successfully!${NO_COLOR}"
else
    echo -e "${RED}Entry parsing tests failed :( ${NO_COLOR}"
fi
