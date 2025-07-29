cmake_minimum_required(VERSION 3.10.2)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POLICY_VERSION_MINIMUM 3.5)

project(
  collierf2py
  LANGUAGES C Fortran)



# Safety net
if(PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)
  message(
    FATAL_ERROR
      "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there.\n"
  )
endif()

find_package(Python3 REQUIRED
  COMPONENTS Interpreter Development)

if (NOT SKBUILD)
  # Kanged -->https://github.com/Kitware/torch_liberator/blob/master/CMakeLists.txt
  # If skbuild is not the driver; include its utilities in CMAKE_MODULE_PATH
  execute_process(
  COMMAND "${Python3_EXECUTABLE}"
  -c "import os, skbuild; print(os.path.dirname(skbuild.__file__))"
  OUTPUT_VARIABLE SKBLD_DIR
  OUTPUT_STRIP_TRAILING_WHITESPACE
  )
  set(SKBLD_CMAKE_DIR "${SKBLD_DIR}/resources/cmake")
  list(APPEND CMAKE_MODULE_PATH ${SKBLD_CMAKE_DIR})
endif()

# scikit-build style includes
find_package(PythonExtensions REQUIRED) # for ${PYTHON_EXTENSION_MODULE_SUFFIX}
find_package(NumPy REQUIRED) # for ${NumPy_INCLUDE_DIRS}
find_package(F2PY REQUIRED)


# dependencies
include(FetchContent)
FetchContent_Declare(
  collier
  URL https://collier.hepforge.org/downloads/?f=collier-1.2.8.tar.gz
)
FetchContent_GetProperties(collier)
if(NOT collier_POPULATED)
    FetchContent_Populate(collier)
    # Make subproject to use 'BUILD_SHARED_LIBS=ON' setting.
    set(static ON CACHE INTERNAL "Build static libraries")
    set(CMAKE_POSITION_INDEPENDENT_CODE ON CACHE INTERNAL "Build position independent code")
    add_subdirectory(${collier_SOURCE_DIR} ${collier_BINARY_DIR})
endif()


# Prepping the module
set(f2py_module_name "collierf2py")
set(fortran_src_file "${CMAKE_SOURCE_DIR}/src/pyCollier.f90")
set(generated_module_file ${f2py_module_name}${PYTHON_EXTENSION_MODULE_SUFFIX})


# Target for enforcing dependencies
add_custom_target(${f2py_module_name} ALL
  DEPENDS "${fortran_src_file}"
  )

# Custom command for generating .c
add_custom_command(
  OUTPUT "${f2py_module_name}module.c"
  COMMAND ${F2PY_EXECUTABLE}
    -m ${f2py_module_name}
    ${fortran_src_file}
    --lower
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS ${fortran_src_file}
  )
set(CMAKE_Fortran_FLAGS, "-fPIC")

add_library(${generated_module_file} MODULE
            "${f2py_module_name}module.c"
            "${F2PY_INCLUDE_DIR}/fortranobject.c"
            "${fortran_src_file}")

target_link_libraries(${generated_module_file} PRIVATE collier)
target_include_directories(${generated_module_file} PUBLIC
                           ${F2PY_INCLUDE_DIRS}
                           ${PYTHON_INCLUDE_DIRS}
                           ${collier_SOURCE_DIR}/modules)

set_target_properties(${generated_module_file} PROPERTIES PREFIX "")
set_target_properties(${generated_module_file} PROPERTIES SUFFIX "")


# Linker fixes
if (UNIX)
  if (APPLE)
    set_target_properties(${generated_module_file} PROPERTIES
    LINK_FLAGS  '-Wl,-dylib,-undefined,dynamic_lookup')
  else()
    set_target_properties(${generated_module_file} PROPERTIES
  LINK_FLAGS  '-Wl,--allow-shlib-undefined')
  endif()
endif()

if (SKBUILD)
  install(TARGETS ${generated_module_file} DESTINATION pyCollier)
else()
  install(TARGETS ${generated_module_file} DESTINATION ${CMAKE_SOURCE_DIR}/pyCollier)
endif()
