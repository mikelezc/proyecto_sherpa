#!/bin/bash

# This script is a test runner with colored output for easy visual inspection of test results

echo -e "\n\033[96m🧪 Task Management System - Enhanced Test Suite\033[0m"
echo -e "\033[96m============================================================\033[0m\n"

docker exec django_web python manage.py test --verbosity=2 2>&1 | while IFS= read -r line; do

    # Filter out expected warnings that are NOT real issues
    if [[ "$line" =~ Method\ Not\ Allowed\ \(GET\):\ /api/auth/login/ ]] || \
       [[ "$line" =~ Method\ Not\ Allowed\ \(GET\):\ /api/auth/register/ ]] || \
       [[ "$line" =~ Unauthorized:\ /api/auth/users/me/ ]] || \
       [[ "$line" =~ Not\ Found:\ /static/css/styles.css ]] || \
       [[ "$line" =~ CELERY_USER\ environment\ variable\ not\ set ]] || \
       [[ "$line" =~ Assignment\ notifications\ sent\ for\ task ]] || \
       [[ "$line" =~ Daily\ summaries\ sent\ to ]] || \
       [[ "$line" =~ Marked.*tasks\ as\ overdue ]] || \
       [[ "$line" =~ Task\ completed\ -\ Processing\ complete ]] || \
       [[ "$line" =~ STARTING\ CLEANUP\ TASK ]] || \
       [[ "$line" =~ END\ OF\ CLEANUP\ TASK ]]; then
        continue
    fi
    
    if [[ "$line" =~ .*"... ok"$ ]]; then
        echo -e "${line/... ok/... \033[92m\033[1mOK\033[0m}"
    elif [[ "$line" =~ .*"... OK"$ ]]; then
        echo -e "${line/... OK/... \033[92m\033[1mOK\033[0m}"
    elif [[ "$line" =~ .+ok$ ]] && [[ ! "$line" =~ ^test_.* ]] && [[ ! "$line" =~ "WARNING" ]] && [[ ! "$line" =~ "INFO" ]]; then
        echo -e "${line/ok$/\033[92m\033[1mOK\033[0m}"
    elif [[ "$line" =~ ^[[:space:]]*ok$ ]]; then
        echo -e "\033[92m\033[1mOK\033[0m"
    elif [[ "$line" =~ .*"... ERROR"$ ]]; then
        echo -e "${line/... ERROR/... \033[91m❌ ERROR\033[0m}"
    elif [[ "$line" =~ .*"... FAIL"$ ]]; then
        echo -e "${line/... FAIL/... \033[91m❌ FAIL\033[0m}"
    elif [[ "$line" =~ ^test_.* ]]; then
        echo -e "\033[94m$line\033[0m"
    elif [[ "$line" =~ .*WARNING.* ]] && [[ ! "$line" =~ ^test_.* ]]; then
        # Only show unexpected WARNING
        echo -e "${line/WARNING/\033[93m⚠️ WARNING\033[0m}"
    elif [[ "$line" =~ .*ERROR.* ]] && [[ ! "$line" =~ ^test_.* ]]; then
        echo -e "${line/ERROR/\033[91m❌ ERROR\033[0m}"
    elif [[ "$line" =~ .*INFO.* ]] && [[ ! "$line" =~ ^test_.* ]]; then
        # Only show important INFO (not from normal Celery tasks)
        echo -e "${line/INFO/\033[96mℹ️ INFO\033[0m}"
    elif [[ "$line" =~ ^Found.*test\(s\)\. ]] || [[ "$line" =~ ^Creating.* ]] || [[ "$line" =~ ^Destroying.* ]] || [[ "$line" =~ ^Operations.* ]] || [[ "$line" =~ ^Applying.* ]]; then
        echo -e "\033[96m$line\033[0m"
    elif [[ "$line" =~ ^System\ check.* ]]; then
        echo -e "\033[92m$line\033[0m"
    elif [[ "$line" =~ ^Ran.*tests.*in.*s$ ]]; then
        if [[ "$line" =~ "OK" ]]; then
            echo -e "\033[92m$line\033[0m"
        else
            echo -e "\033[91m$line\033[0m"
        fi
    elif [[ "$line" =~ ^-{70}$ ]]; then
        echo -e "\033[96m$line\033[0m"
    else
        echo "$line"
    fi
done

exit_code=${PIPESTATUS[0]}

echo -e "\n\033[96m============================================================\033[0m"
if [ $exit_code -eq 0 ]; then
    echo -e "\033[92m\033[1m ALL TESTS PASSED \033[0m"
else
    echo -e "\033[91m\033[1m Some tests failed \033[0m"
fi
echo -e "\033[96m============================================================\033[0m\n"

exit $exit_code
