#!/bin/bash

echo -e "\n\033[96m🧪 Task Management System - Enhanced Test Suite\033[0m"
echo -e "\033[96m============================================================\033[0m\n"

# Ejecutar tests y aplicar colores en tiempo real
docker exec django_web python manage.py test --verbosity=2 2>&1 | while IFS= read -r line; do
    # Aplicar colores a diferentes tipos de líneas
    if [[ "$line" =~ .*"... ok"$ ]]; then
        # Tests exitosos - verde bold sin checkmark
        echo -e "${line/... ok/... \033[92m\033[1mOK\033[0m}"
    elif [[ "$line" =~ .*"... OK"$ ]]; then
        # Migraciones exitosas - verde bold
        echo -e "${line/... OK/... \033[92m\033[1mOK\033[0m}"
    elif [[ "$line" =~ .+ok$ ]] && [[ ! "$line" =~ ^test_.* ]] && [[ ! "$line" =~ "WARNING" ]] && [[ ! "$line" =~ "INFO" ]]; then
        # Otros casos de "ok" al final - verde bold
        echo -e "${line/ok$/\033[92m\033[1mOK\033[0m}"
    elif [[ "$line" =~ ^[[:space:]]*ok$ ]]; then
        # "ok" solitario en su propia línea - verde bold
        echo -e "\033[92m\033[1mOK\033[0m"
    elif [[ "$line" =~ .*"... ERROR"$ ]]; then
        # Tests con error - rojo con X
        echo -e "${line/... ERROR/... \033[91m❌ ERROR\033[0m}"
    elif [[ "$line" =~ .*"... FAIL"$ ]]; then
        # Tests fallidos - rojo con X
        echo -e "${line/... FAIL/... \033[91m❌ FAIL\033[0m}"
    elif [[ "$line" =~ ^test_.* ]]; then
        # Nombres de tests - azul
        echo -e "\033[94m$line\033[0m"
    elif [[ "$line" =~ .*WARNING.* ]] && [[ ! "$line" =~ ^test_.* ]]; then
        # Warnings - amarillo con icono
        echo -e "${line/WARNING/\033[93m⚠️ WARNING\033[0m}"
    elif [[ "$line" =~ .*ERROR.* ]] && [[ ! "$line" =~ ^test_.* ]]; then
        # Errores del sistema - rojo con icono
        echo -e "${line/ERROR/\033[91m❌ ERROR\033[0m}"
    elif [[ "$line" =~ .*INFO.* ]] && [[ ! "$line" =~ ^test_.* ]]; then
        # Info - cian con icono
        echo -e "${line/INFO/\033[96mℹ️ INFO\033[0m}"
    elif [[ "$line" =~ ^Found.*test\(s\)\. ]] || [[ "$line" =~ ^Creating.* ]] || [[ "$line" =~ ^Destroying.* ]] || [[ "$line" =~ ^Operations.* ]] || [[ "$line" =~ ^Applying.* ]]; then
        # Mensajes del sistema - cian
        echo -e "\033[96m$line\033[0m"
    elif [[ "$line" =~ ^System\ check.* ]]; then
        # Check del sistema - verde
        echo -e "\033[92m$line\033[0m"
    elif [[ "$line" =~ ^Ran.*tests.*in.*s$ ]]; then
        # Resultado final - verde si OK
        if [[ "$line" =~ "OK" ]]; then
            echo -e "\033[92m$line\033[0m"
        else
            echo -e "\033[91m$line\033[0m"
        fi
    elif [[ "$line" =~ ^-{70}$ ]]; then
        # Líneas separadoras - cian
        echo -e "\033[96m$line\033[0m"
    else
        # Líneas normales
        echo "$line"
    fi
done

# Capturar el código de salida del pipe
exit_code=${PIPESTATUS[0]}

echo -e "\n\033[96m============================================================\033[0m"
if [ $exit_code -eq 0 ]; then
    echo -e "\033[92m\033[1m🎉 ALL TESTS PASSED! System ready for production! 🎉\033[0m"
else
    echo -e "\033[91m\033[1m❌ Some tests failed. Review output above for details.\033[0m"
fi
echo -e "\033[96m============================================================\033[0m\n"

exit $exit_code
