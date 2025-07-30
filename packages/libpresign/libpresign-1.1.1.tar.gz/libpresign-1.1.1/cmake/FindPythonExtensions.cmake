# FindPythonExtensions.cmake
# Helper functions for building Python extensions with CMake

function(python_extension_module name)
    # Get Python extension suffix
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -c
        "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
        OUTPUT_VARIABLE PYTHON_EXTENSION_SUFFIX
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    
    # Set the suffix on the target
    set_target_properties(${name} PROPERTIES SUFFIX "${PYTHON_EXTENSION_SUFFIX}")
    
    # Ensure the output name doesn't have lib prefix on Unix
    set_target_properties(${name} PROPERTIES PREFIX "")
endfunction()