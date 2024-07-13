cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

add_compile_definitions(_CPMODULE)

python_add_library(
  _C
  MODULE

  src/arch.c
  src/atomobj.c
  src/context.c
  src/field.c
  src/option.c
  src/module.c
  src/context.c
  src/state.c
  src/struct.c

  src/parsing_typeof.c
  src/parsing_sizeof.c
  src/parsing_pack.c
  src/parsing_unpack.c

  src/atomimpl/intatomobj.c
  src/atomimpl/floatatomobj.c
  src/atomimpl/boolatomobj.c
  src/atomimpl/charatomobj.c
  src/atomimpl/padatomobj.c
  src/atomimpl/stringatomobj.c

  WITH_SOABI
)

target_include_directories(_C PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include)

message(STATUS "CMake ${CMAKE_VERSION}")
message(STATUS "Python ${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")

add_custom_target(
 genapi ALL
 COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/src/code_gen/genapi.py ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillar.h.in ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar.c.in
 BYPRODUCTS ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar/include/caterpillar/caterpillar.h ${CMAKE_CURRENT_SOURCE_DIR}/src/caterpillar.c
 COMMENT "Generating Public Caterpillar API"
)

add_dependencies(_C genapi)

install(TARGETS _C DESTINATION caterpillar)
