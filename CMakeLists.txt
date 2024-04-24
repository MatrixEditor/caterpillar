cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

python_add_library(
  _core
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

  src/intatomobj.c

  WITH_SOABI
)

target_include_directories(_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)

message(STATUS "CMake ${CMAKE_VERSION}")
message(STATUS "Python ${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")
install(TARGETS _core DESTINATION caterpillar)