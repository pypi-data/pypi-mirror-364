install(CODE "
    message(\"Generating .pyi stub files.\")
")

# Temporarily copy _tango extension to source dir
install(CODE "
    file(COPY \"$<TARGET_FILE:pytango_tango>\" DESTINATION \"${CMAKE_CURRENT_SOURCE_DIR}/tango\")
    file(RENAME \"${CMAKE_CURRENT_SOURCE_DIR}/tango/$<TARGET_FILE_NAME:pytango_tango>\" \"${CMAKE_CURRENT_SOURCE_DIR}/tango/$<TARGET_FILE_PREFIX:pytango_tango>$<TARGET_FILE_BASE_NAME:pytango_tango>$<TARGET_FILE_SUFFIX:pytango_tango>\")
")

# Trick to get the PYTHONPATH from isolated environment
install(CODE "
    execute_process(
        COMMAND python -c \"import os; print(os.environ.get('PYTHONPATH', ''))\"
        OUTPUT_VARIABLE ISOLATED_PYTHONPATH
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ECHO_OUTPUT_VARIABLE
    )
")

# Determine system path separator sign
# Convert source path according to platform
if(WIN32)
    set(PATH_SEPARATOR ";")
    install(CODE "string(REPLACE \"/\" \"\\\\\" PYTANGO_SOURCE_DIR \"${CMAKE_CURRENT_SOURCE_DIR}\")")
else()
    set(PATH_SEPARATOR ":")
    install(CODE "set(PYTANGO_SOURCE_DIR \"\${CMAKE_CURRENT_SOURCE_DIR}\")")
endif()

# Generate the .pyi stubs
# Appending tango source code directory to ISOLATED_PYTHONPATH
if(WIN32)
    install(CODE "
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E env \"PYTHONPATH=\${PYTANGO_SOURCE_DIR}${PATH_SEPARATOR}\${ISOLATED_PYTHONPATH}\"
            python cmake\\\\generate_stubs.py tango --ignore-all-errors
            RESULT_VARIABLE TRY_TO_INSTALL_STUBS
        )
    ")
else()
    install(CODE "
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E env \"PYTHONPATH=\${PYTANGO_SOURCE_DIR}${PATH_SEPARATOR}\${ISOLATED_PYTHONPATH}\"
            pybind11-stubgen tango --ignore-all-errors
            RESULT_VARIABLE TRY_TO_INSTALL_STUBS
        )
    ")
endif()

# Copy generated .pyi stubs
install(CODE "
    if(\${TRY_TO_INSTALL_STUBS} EQUAL 0)
        file(
            COPY \"\${CMAKE_CURRENT_SOURCE_DIR}/stubs/tango/_tango.pyi\"
            DESTINATION \"\${CMAKE_CURRENT_SOURCE_DIR}/tango\"
        )
        message(STATUS \"File copied: \${CMAKE_CURRENT_SOURCE_DIR}/stubs/tango/_tango.pyi\")
    else()
        message(WARNING \"Stub files generation failed. They will not be installed.\")
    endif()
")

# Clean _tango extension from source dir and remove stubs folder
install(CODE "
    file(REMOVE \"${CMAKE_CURRENT_SOURCE_DIR}/tango/$<TARGET_FILE_PREFIX:pytango_tango>$<TARGET_FILE_BASE_NAME:pytango_tango>$<TARGET_FILE_SUFFIX:pytango_tango>\")
    file(REMOVE_RECURSE \"${CMAKE_CURRENT_SOURCE_DIR}/stubs\")
")
